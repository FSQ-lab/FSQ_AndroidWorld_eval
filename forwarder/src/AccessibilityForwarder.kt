package com.google.androidenv.accessibilityforwarder

import android.accessibilityservice.AccessibilityService
import android.content.Context
import android.content.Intent
import android.os.Process
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.view.accessibility.AccessibilityWindowInfo
import com.google.androidenv.accessibilityforwarder.A11yServiceGrpcKt.A11yServiceCoroutineStub
import com.google.gson.Gson
import io.grpc.ManagedChannel
import io.grpc.Metadata
import io.grpc.ManagedChannelBuilder
import io.grpc.ProxyDetector
import io.grpc.StatusException
import java.io.File
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineName
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.runInterruptible
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout

/**
 * An Android service that listens to accessibility events and forwards them via gRPC.
 *
 * This service also logs the accessibility tree if [LogFlags.logAccessibilityTree] is set and if
 * [LogFlags.grpcPort] is positive.
 *
 * Please see
 * https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent#getEventType()
 * for a comprehensive list of events emitted by Android.
 */
class AccessibilityForwarder(
  private val channelFactory: (host: String, port: Int) -> ManagedChannel = { host, port ->
    ManagedChannelBuilder.forAddress(host, port)
      .proxyDetector(ProxyDetector { _ -> null })
      .usePlaintext()
      .build()
  },
  private val workerDispatcher: CoroutineDispatcher = Dispatchers.IO,
  private val captureWindows: (AccessibilityForwarder) -> List<AccessibilityWindowInfo> = { it.windows },
) : AccessibilityService() {

  private val instance = "${Process.myPid()}:${nextInstance.incrementAndGet()}"
  // Lifecycle callbacks serialize starts/stops; the worker never takes this monitor.
  private val lifecycleLock = Any()
  private val channelLock = Any()
  @Volatile private var connection: Connection? = null
  private var nextGeneration = 0L

  private class Connection(val generation: Long, val workerName: String) {
    val job = SupervisorJob()
    var channel: ManagedChannel? = null
    var stub: A11yServiceCoroutineStub? = null
    val forestSequence = AtomicLong()
    val eventSequence = AtomicLong()
  }

  public override fun onServiceConnected() {
    super.onServiceConnected()
    synchronized(lifecycleLock) {
      if (connection != null) return
      val generation = ++nextGeneration
      val current = Connection(generation, "a11y-$instance-$generation")
      connection = current
      Log.i(TAG, "Connected service=$instance generation=$generation worker=${current.workerName}")
      CoroutineScope(current.job + workerDispatcher + CoroutineName(current.workerName)).launch {
        Log.i(TAG, "Worker started ${source(current)} thread=${Thread.currentThread().name}")
        try {
          while (isActive && LogFlags.a11yTreePeriodMs > 0) {
            try {
              // Interruptible capture also cancels the tree creator's nested runBlocking calls.
              val windows = runInterruptible { captureWindows(this@AccessibilityForwarder) }
              logAccessibilityTree(current, windows)
            } catch (e: ConcurrentModificationException) {
              // A changing Android window list is sampled again on the normal capture period.
            }
            delay(LogFlags.a11yTreePeriodMs.coerceAtLeast(1))
          }
        } finally {
          Log.i(TAG, "Worker stopped ${source(current)}")
        }
      }
    }
  }

  override fun onUnbind(intent: Intent?): Boolean {
    stopConnection("unbind")
    return super.onUnbind(intent)
  }

  override fun onDestroy() {
    stopConnection("destroy")
    super.onDestroy()
  }

  private fun stopConnection(reason: String) {
    synchronized(lifecycleLock) {
      val current = connection ?: return
      synchronized(channelLock) {
        connection = null
        // Cancel the coroutine RPC as well as closing its transport before joining the worker.
        current.job.cancel()
        closeChannel(current)
      }
      runBlocking { current.job.join() }
      Log.i(TAG, "Disconnected ${source(current)} reason=$reason")
    }
  }

  private fun grpcStub(current: Connection): A11yServiceCoroutineStub? =
    synchronized(channelLock) {
      if (connection !== current || !current.job.isActive) return@synchronized null
      if (current.stub == null) {
        Log.i(TAG, "Building channel ${source(current)} endpoint=${LogFlags.grpcHost}:${LogFlags.grpcPort}")
        val channel = channelFactory(LogFlags.grpcHost, LogFlags.grpcPort)
        current.channel = channel
        current.stub = A11yServiceCoroutineStub(channel)
      }
      current.stub
    }

  private fun closeChannel(current: Connection, expected: A11yServiceCoroutineStub? = null) {
    synchronized(channelLock) {
      if (expected != null && current.stub !== expected) return
      current.channel?.shutdownNow()
      current.channel = null
      current.stub = null
    }
  }

  private fun source(current: Connection): String =
    "service=$instance generation=${current.generation} source=capture worker=${current.workerName}"

  override fun onInterrupt() {
    // Android requests interruption of accessibility feedback, not disconnection of the service.
    // This forwarder produces no user feedback, so capture and the process-wide flags stay intact.
    connection?.let { Log.i(TAG, "Feedback interrupted ${source(it)}") }
  }

  override fun onAccessibilityEvent(event: AccessibilityEvent?) {
    val current = connection ?: return
    if (event == null) {
      Log.i(TAG, "`event` is null.")
      return
    }

    logExtrasForEvent(current, event)
    val eventType = event.eventType
    val eventTypeStr: String = AccessibilityEvent.eventTypeToString(eventType)
    if (eventTypeStr.isNotEmpty()) {
      Log.i(TAG, eventTypeStr)
    }
  }

  private fun serializeMapToJson(map: MutableMap<String, String>): String {
    val gson = Gson()
    return gson.toJson(map)
  }

  private fun writeToInternalStorage(data: Any, fileName: String, context: Context) {
    val tmpFile = File(context.filesDir, "$fileName.tmp")

    when (data) {
      is ByteArray -> {
        tmpFile.writeBytes(data)
      }
      is String -> {
        tmpFile.writeText(data)
      }
      else -> {
        Log.e(TAG, "Unsupported data type for writing to internal storage.")
        return
      }
    }

    // Rename the file to the final name to prevent partial writes.
    val finalFile = File(context.filesDir, fileName)
    if (tmpFile.renameTo(finalFile)) {
      Log.i(TAG, "File written successfully and renamed to $fileName")
    } else {
      Log.i(TAG, "File renaming failed")
    }
  }

  private suspend fun logAccessibilityTree(
    current: Connection,
    windows: List<AccessibilityWindowInfo>,
  ) {
    if (!LogFlags.logAccessibilityTree) {
      Log.i(TAG, "Not logging accessibility tree")
      return
    }

    // Check gRPC port before actually building the forest.
    if (LogFlags.grpcPort <= 0) {
      Log.w(TAG, "Can't log accessibility tree because gRPC port has not been set.")
      return
    }

    val forest = runInterruptible { creator.buildForest(windows) }
    currentCoroutineContext().ensureActive()

    if (LogFlags.logUsingInternalStorage) {
      runInterruptible { writeToInternalStorage(forest.toByteArray(), "accessibility_tree.pb", this) }
    }

    if (LogFlags.logUsingGRPC) {
      val stub = grpcStub(current) ?: return
      val sequence = current.forestSequence.incrementAndGet()
      val headers = Metadata().apply {
        put(INSTANCE_HEADER, instance)
        put(GENERATION_HEADER, current.generation.toString())
        put(SEQUENCE_HEADER, sequence.toString())
      }
      try {
        currentCoroutineContext().ensureActive()
        Log.i(TAG, "sending (blocking) gRPC request for tree ${source(current)} sequence=$sequence windows=${forest.windowsCount}")
        val response: ForestResponse = withTimeout(GRPC_TIMEOUT_MILLIS) { stub.sendForest(forest, headers) }
        if (response.error.isNotEmpty()) {
          Log.w(TAG, "gRPC response.error: ${response.error}")
        } else {
          Log.i(TAG, "gRPC request for tree succeeded ${source(current)} sequence=$sequence")
        }
      } catch (e: StatusException) {
        Log.w(TAG, "gRPC StatusException; are you sure networking is turned on?")
        Log.i(TAG, "extra: exception ['$e']")
        closeChannel(current, stub)
      } catch (e: TimeoutCancellationException) {
        Log.w(TAG, "gRPC TimeoutCancellationException; are you sure networking is turned on?")
        Log.i(TAG, "extra: exception ['$e']")
        closeChannel(current, stub)
      }
    }
  }

  /** Logs extras for all event types. */
  private fun logExtrasForEvent(current: Connection, event: AccessibilityEvent) {

    val events: MutableMap<String, String> = mutableMapOf()

    val sourceDescription = event.source?.contentDescription()
    if (!sourceDescription.isNullOrEmpty()) {
      events.put("source_content_description", sourceDescription)
    }

    // Output the event text.
    val eventText = event.text.joinToString(", ")
    if (eventText.isNotEmpty()) {
      events.put("event_text", eventText)
    }

    // Output the source text.
    val sourceText = event.source?.text?.toString()
    if (!sourceText.isNullOrEmpty()) {
      events.put("source_text", sourceText)
    }

    val eventTypeStr: String = AccessibilityEvent.eventTypeToString(event.eventType)
    if (eventTypeStr.isNotEmpty()) {
      events.put("event_type", eventTypeStr)
    }

    val className = event.source?.className?.toString()
    if (!className.isNullOrEmpty()) {
      events.put("source_class_name", className)
    }

    val packageName = event.packageName?.toString()
    if (!packageName.isNullOrEmpty()) {
      events.put("event_package_name", packageName)
    }

    // Text editing properties.
    val beforeText = event.beforeText?.toString()
    if (!beforeText.isNullOrEmpty()) {
      events.put("before_text", beforeText)
    }

    val fromIndex = event.fromIndex
    if (fromIndex != -1) {
      events.put("from_index", fromIndex.toString())
    }

    val toIndex = event.toIndex
    if (toIndex != -1) {
      events.put("to_index", toIndex.toString())
    }

    val addedCount = event.addedCount
    if (addedCount != -1) {
      events.put("added_count", addedCount.toString())
    }

    val removedCount = event.removedCount
    if (removedCount != -1) {
      events.put("removed_count", removedCount.toString())
    }

    //  Text traversal properties
    val movementGranularity = event.movementGranularity
    if (movementGranularity != 0) {
      events.put("movement_granularity", movementGranularity.toString())
    }

    val action = event.action
    if (action != 0) {
      events.put("action", action.toString())
    }

    // Scrolling properties.
    if (eventTypeStr == "TYPE_VIEW_SCROLLED") {
      events.put("scroll_delta_x", event.scrollDeltaX.toString())
      events.put("scroll_delta_y", event.scrollDeltaY.toString())
    }

    // Report viewID so we know exactly where the event came from.
    val viewId = event.source?.viewIdResourceName?.toString()
    if (!viewId.isNullOrEmpty()) {
      events.put("view_id", viewId)
    }

    if (LogFlags.logUsingInternalStorage) {
      writeToInternalStorage(serializeMapToJson(events), "event.json", this)
    }

    // Format [events] as a Python dict.
    if (events.isNotEmpty()) {
      events.put("event_timestamp_ms", event.eventTime.toString(10))
      // Check if we want to use gRPC.
      if (LogFlags.grpcPort > 0) {
        val stub = grpcStub(current) ?: return
        val sequence = current.eventSequence.incrementAndGet()
        val eventSource = "service=$instance generation=${current.generation} source=event worker=callback sequence=$sequence"
        try {
          val request = eventRequest { this.event.putAll(events) }
          val response: EventResponse =
            runBlocking(current.job) {
              ensureActive()
              Log.i(TAG, "sending (blocking) gRPC request for event $eventSource")
              withTimeout(GRPC_TIMEOUT_MILLIS) { stub.sendEvent(request) }
            }
          if (response.error.isNotEmpty()) {
            Log.w(TAG, "gRPC response.error: ${response.error}")
          } else {
            Log.i(TAG, "gRPC request for event succeeded $eventSource")
          }
        } catch (e: StatusException) {
          Log.w(TAG, "gRPC StatusException; are you sure networking is turned on?")
          Log.i(TAG, "extra: exception ['$e']")
          closeChannel(current, stub)
        } catch (e: TimeoutCancellationException) {
          Log.w(TAG, "gRPC TimeoutCancellationException; are you sure networking is turned on?")
          Log.i(TAG, "extra: exception ['$e']")
          closeChannel(current, stub)
        } catch (e: CancellationException) {
          // A lifecycle stop cancels event RPCs as well; do not escape the Android callback.
          Log.i(TAG, "gRPC request for event cancelled $eventSource")
        }
      } else {
        Log.w(TAG, "Can't log accessibility event because gRPC port has not been set.")
      }
    }
  }

  /** Recursively climbs the accessibility tree until the root, collecting descriptions. */
  private fun AccessibilityNodeInfo?.contentDescription(): String {
    if (this == null) {
      return ""
    }

    val descriptions = mutableListOf<String>()
    var current: AccessibilityNodeInfo? = this
    while (current != null) {
      val description = current.contentDescription
      if (description != null) {
        descriptions.add(description.toString())
      }

      current = current.parent
    }
    return descriptions.joinToString(", ")
  }

  companion object {
    private const val TAG = "AndroidRLTask"
    private const val GRPC_TIMEOUT_MILLIS = 1000L
    private val nextInstance = AtomicLong()
    private val INSTANCE_HEADER = Metadata.Key.of("fsq-forwarder-instance", Metadata.ASCII_STRING_MARSHALLER)
    private val GENERATION_HEADER = Metadata.Key.of("fsq-forwarder-generation", Metadata.ASCII_STRING_MARSHALLER)
    private val SEQUENCE_HEADER = Metadata.Key.of("fsq-forest-sequence", Metadata.ASCII_STRING_MARSHALLER)
    private val creator = AccessibilityTreeCreator()
  }
}
