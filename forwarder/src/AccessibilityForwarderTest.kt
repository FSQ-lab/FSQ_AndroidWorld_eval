package com.google.androidenv.accessibilityforwarder

import android.content.Intent
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.view.accessibility.AccessibilityWindowInfo
import com.google.common.truth.Truth.assertThat
import io.grpc.ManagedChannel
import io.grpc.Metadata
import io.grpc.ServerCall
import io.grpc.ServerCallHandler
import io.grpc.ServerInterceptor
import io.grpc.ServerInterceptors
import io.grpc.Status
import io.grpc.StatusException
import io.grpc.inprocess.InProcessChannelBuilder
import io.grpc.inprocess.InProcessServerBuilder
import io.grpc.testing.GrpcCleanupRule
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.delay
import kotlinx.coroutines.test.TestCoroutineScheduler
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import org.junit.After
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowLog

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [33])
class AccessibilityForwarderTest {

  @get:Rule(order = 1) val cleanupRule = GrpcCleanupRule()

  class FakeAccessibilityService : A11yServiceGrpcKt.A11yServiceCoroutineImplBase(Dispatchers.Unconfined) {
    val forests = mutableListOf<AndroidAccessibilityForest>()
    val events = mutableListOf<EventRequest>()
    var sendForestChecker: suspend (AndroidAccessibilityForest) -> String = { _ -> "" }
    var sendEventChecker: suspend (EventRequest) -> String = { _ -> "" }

    override suspend fun sendForest(request: AndroidAccessibilityForest) = forestResponse {
      forests.add(request)
      error = sendForestChecker(request)
    }

    override suspend fun sendEvent(request: EventRequest) = eventResponse {
      error = sendEventChecker(request)
      events.add(request)
    }
  }

  private lateinit var forwarder: AccessibilityForwarder
  private val fakeA11yService = FakeAccessibilityService()
  private val scheduler = TestCoroutineScheduler()
  private val dispatcher = UnconfinedTestDispatcher(scheduler)
  private val channels = mutableListOf<ManagedChannel>()
  private val endpoints = mutableListOf<Pair<String, Int>>()
  private val forestHeaders = mutableListOf<Map<String, String?>>()
  private val serverName by lazy {
    InProcessServerBuilder.generateName().also { name ->
      cleanupRule.register(
        InProcessServerBuilder.forName(name)
          .directExecutor()
          .addService(ServerInterceptors.intercept(fakeA11yService, object : ServerInterceptor {
            override fun <ReqT : Any?, RespT : Any?> interceptCall(
              call: ServerCall<ReqT, RespT>,
              headers: Metadata,
              next: ServerCallHandler<ReqT, RespT>,
            ): ServerCall.Listener<ReqT> {
              if (call.methodDescriptor.bareMethodName == "SendForest") {
                forestHeaders.add(listOf(
                  "fsq-forwarder-instance", "fsq-forwarder-generation", "fsq-forest-sequence",
                ).associateWith { headers.get(Metadata.Key.of(it, Metadata.ASCII_STRING_MARSHALLER)) })
              }
              return next.startCall(call, headers)
            }
          }))
          .build()
          .start()
      )
    }
  }

  @After
  fun stopForwarder() {
    if (::forwarder.isInitialized) forwarder.onDestroy()
  }

  /** Initializes [forwarder] and [LogFlags] from the given args. */
  fun createForwarder(
    logAccessibilityTree: Boolean = false,
    a11yTreePeriodMs: Long = 0,
    grpcHost: String = "10.0.2.2",
    grpcPort: Int = 0,
    a11yWindows: MutableList<AccessibilityWindowInfo>? = null,
    connect: Boolean = true,
    workerDispatcher: CoroutineDispatcher = dispatcher,
    captureWindows: (AccessibilityForwarder) -> List<AccessibilityWindowInfo> = { it.windows },
  ) {
    LogFlags.logAccessibilityTree = logAccessibilityTree
    LogFlags.a11yTreePeriodMs = a11yTreePeriodMs
    LogFlags.grpcHost = grpcHost
    LogFlags.grpcPort = grpcPort
    LogFlags.logUsingInternalStorage = false
    LogFlags.logUsingGRPC = true
    forwarder = AccessibilityForwarder(
      channelFactory = { host, port ->
        endpoints.add(host to port)
        cleanupRule.register(
          InProcessChannelBuilder.forName(serverName).directExecutor().build()
        ).also { channels.add(it) }
      },
      workerDispatcher = workerDispatcher,
      captureWindows = captureWindows,
    )
    if (a11yWindows == null) {
      shadowOf(forwarder).setWindows(mutableListOf(AccessibilityWindowInfo.obtain()))
    } else {
      shadowOf(forwarder).setWindows(a11yWindows)
    }
    if (connect) forwarder.onServiceConnected()
  }

  @Test
  fun onInterrupt_doesNotCrash() {
    // Arrange.
    createForwarder(logAccessibilityTree = false)
    fakeA11yService.sendEventChecker = { _: EventRequest ->
      assertFalse(true) // This should not be called.
      "" // This should be unreachable
    }

    // Act.
    forwarder.onInterrupt()

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_nullEventShouldBeIgnored() {
    // Arrange.
    createForwarder(logAccessibilityTree = false)
    fakeA11yService.sendEventChecker = { _: EventRequest ->
      assertFalse(true) // This should not be called.
      "" // This should be unreachable
    }

    // Act.
    forwarder.onAccessibilityEvent(null)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_knownEventWithNoInformationShouldNotBeEmitted() {
    // Arrange.
    createForwarder(logAccessibilityTree = false)
    var nodeInfo = AccessibilityNodeInfo()
    nodeInfo.setContentDescription("")
    var event = AccessibilityEvent()
    shadowOf(event).setSourceNode(nodeInfo)
    fakeA11yService.sendEventChecker = { _: EventRequest ->
      assertFalse(true) // This should not be called.
      "" // This should be unreachable
    }

    // Act.
    forwarder.onAccessibilityEvent(event)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_typeViewClicked_sendEventViaGrpc() {
    // Arrange.
    createForwarder(logAccessibilityTree = false, grpcPort = 1234)
    var nodeInfo = AccessibilityNodeInfo()
    nodeInfo.setContentDescription("My Content Description")
    nodeInfo.setText("My Source Text")
    nodeInfo.setClassName("AwesomeClass")
    var event = AccessibilityEvent()
    event.setEventTime(1357924680)
    event.setEventType(AccessibilityEvent.TYPE_VIEW_CLICKED)
    event.getText().add("Some text!")
    event.setPackageName("some.loooong.package.name")
    shadowOf(event).setSourceNode(nodeInfo)
    fakeA11yService.sendEventChecker = { request: EventRequest ->
      // Check that all fields are consistent with how they were set above.
      assertThat(request.eventMap.get("event_type")).isEqualTo("TYPE_VIEW_CLICKED")
      assertThat(request.eventMap.get("event_package_name")).isEqualTo("some.loooong.package.name")
      assertThat(request.eventMap.get("source_content_description"))
        .isEqualTo("My Content Description")
      assertThat(request.eventMap.get("source_text")).isEqualTo("My Source Text")
      assertThat(request.eventMap.get("source_class_name")).isEqualTo("AwesomeClass")
      assertThat(request.eventMap.get("event_text")).isEqualTo("Some text!")
      assertThat(request.eventMap.get("event_timestamp_ms")).isEqualTo("1357924680")
      // No error message
      ""
    }

    // Act.
    forwarder.onAccessibilityEvent(event)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_typeViewTextChanged_ensureAllFieldsForwarded() {
    // Arrange.
    createForwarder(logAccessibilityTree = false, grpcPort = 1234)
    var nodeInfo = AccessibilityNodeInfo()
    nodeInfo.setContentDescription("My Content Description")
    nodeInfo.setText("My Source Text")
    nodeInfo.setClassName("AwesomeClass")
    var event = AccessibilityEvent()
    event.setEventTime(1357924680)
    event.setEventType(AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED)
    event.getText().add("Some text!")
    event.fromIndex = 7
    event.beforeText = "Old words"
    event.addedCount = 12
    event.removedCount = 9
    event.setPackageName("some.loooong.package.name")
    shadowOf(event).setSourceNode(nodeInfo)
    fakeA11yService.sendEventChecker = { request: EventRequest ->
      // Check that all fields are consistent with how they were set above.
      assertThat(request.eventMap.get("event_type")).isEqualTo("TYPE_VIEW_TEXT_CHANGED")
      assertThat(request.eventMap.get("event_package_name")).isEqualTo("some.loooong.package.name")
      assertThat(request.eventMap.get("source_content_description"))
        .isEqualTo("My Content Description")
      assertThat(request.eventMap.get("source_text")).isEqualTo("My Source Text")
      assertThat(request.eventMap.get("source_class_name")).isEqualTo("AwesomeClass")
      assertThat(request.eventMap.get("event_text")).isEqualTo("Some text!")
      assertThat(request.eventMap.get("event_timestamp_ms")).isEqualTo("1357924680")
      assertThat(request.eventMap.get("from_index")).isEqualTo("7")
      assertThat(request.eventMap.get("before_text")).isEqualTo("Old words")
      assertThat(request.eventMap.get("added_count")).isEqualTo("12")
      assertThat(request.eventMap.get("removed_count")).isEqualTo("9")
      assertFalse(request.eventMap.containsKey("to_index"))
      assertFalse(request.eventMap.containsKey("view_id"))
      assertFalse(request.eventMap.containsKey("action"))
      assertFalse(request.eventMap.containsKey("movement_granularity"))
      assertFalse(request.eventMap.containsKey("scroll_delta_x"))
      assertFalse(request.eventMap.containsKey("scroll_delta_y"))
      // No error message
      ""
    }

    // Act.
    forwarder.onAccessibilityEvent(event)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_typeViewScrolled_ensureAllFieldsForwarded() {
    // Arrange.
    createForwarder(logAccessibilityTree = false, grpcPort = 1234)
    var nodeInfo = AccessibilityNodeInfo()
    nodeInfo.setContentDescription("My Content Description")
    nodeInfo.setText("My Source Text")
    nodeInfo.setClassName("AwesomeClass")
    var event = AccessibilityEvent()
    event.setEventTime(1357924680)
    event.setEventType(AccessibilityEvent.TYPE_VIEW_SCROLLED)
    event.getText().add("Some text!")
    event.scrollDeltaX = 13
    event.scrollDeltaY = 27
    event.setPackageName("some.loooong.package.name")
    shadowOf(event).setSourceNode(nodeInfo)
    fakeA11yService.sendEventChecker = { request: EventRequest ->
      // Check that all fields are consistent with how they were set above.
      assertThat(request.eventMap.get("event_type")).isEqualTo("TYPE_VIEW_SCROLLED")
      assertThat(request.eventMap.get("event_package_name")).isEqualTo("some.loooong.package.name")
      assertThat(request.eventMap.get("source_content_description"))
        .isEqualTo("My Content Description")
      assertThat(request.eventMap.get("source_text")).isEqualTo("My Source Text")
      assertThat(request.eventMap.get("source_class_name")).isEqualTo("AwesomeClass")
      assertThat(request.eventMap.get("event_text")).isEqualTo("Some text!")
      assertThat(request.eventMap.get("event_timestamp_ms")).isEqualTo("1357924680")
      assertThat(request.eventMap.get("scroll_delta_x")).isEqualTo("13")
      assertThat(request.eventMap.get("scroll_delta_y")).isEqualTo("27")
      assertFalse(request.eventMap.containsKey("from_index"))
      assertFalse(request.eventMap.containsKey("to_index"))
      assertFalse(request.eventMap.containsKey("before_text"))
      assertFalse(request.eventMap.containsKey("added_count"))
      assertFalse(request.eventMap.containsKey("removed_count"))
      // No error message
      ""
    }

    // Act.
    forwarder.onAccessibilityEvent(event)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_typeViewTextTraversedAtMovementGranularity_ensureAllFieldsForwarded() {
    // Arrange.
    createForwarder(logAccessibilityTree = false, grpcPort = 1234)
    var nodeInfo = AccessibilityNodeInfo()
    nodeInfo.setContentDescription("My Content Description")
    nodeInfo.setText("My Source Text")
    nodeInfo.setClassName("AwesomeClass")
    nodeInfo.viewIdResourceName = "this.big.old.view.id"
    var event = AccessibilityEvent()
    event.setEventTime(1357924680)
    event.setEventType(AccessibilityEvent.TYPE_VIEW_TEXT_TRAVERSED_AT_MOVEMENT_GRANULARITY)
    event.getText().add("Some text!")
    event.setPackageName("some.loooong.package.name")
    event.movementGranularity = 5
    event.fromIndex = 6
    event.toIndex = 8
    event.action = 23
    shadowOf(event).setSourceNode(nodeInfo)
    fakeA11yService.sendEventChecker = { request: EventRequest ->
      // Check that all fields are consistent with how they were set above.
      assertThat(request.eventMap.get("event_type"))
        .isEqualTo("TYPE_VIEW_TEXT_TRAVERSED_AT_MOVEMENT_GRANULARITY")
      assertThat(request.eventMap.get("event_package_name")).isEqualTo("some.loooong.package.name")
      assertThat(request.eventMap.get("source_content_description"))
        .isEqualTo("My Content Description")
      assertThat(request.eventMap.get("source_text")).isEqualTo("My Source Text")
      assertThat(request.eventMap.get("source_class_name")).isEqualTo("AwesomeClass")
      assertThat(request.eventMap.get("event_text")).isEqualTo("Some text!")
      assertThat(request.eventMap.get("event_timestamp_ms")).isEqualTo("1357924680")
      assertThat(request.eventMap.get("movement_granularity")).isEqualTo("5")
      assertThat(request.eventMap.get("from_index")).isEqualTo("6")
      assertThat(request.eventMap.get("to_index")).isEqualTo("8")
      assertThat(request.eventMap.get("view_id")).isEqualTo("this.big.old.view.id")
      assertThat(request.eventMap.get("action")).isEqualTo("23")
      // No error message
      ""
    }

    // Act.
    forwarder.onAccessibilityEvent(event)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_sendingevent_grpcTimeout() {
    // Arrange.
    createForwarder(
      logAccessibilityTree = false,
      a11yTreePeriodMs = 0,
      grpcHost = "amazing.host",
      grpcPort = 4321,
    )
    var nodeInfo = AccessibilityNodeInfo()
    nodeInfo.setContentDescription("My Content Description")
    nodeInfo.setText("My Source Text")
    nodeInfo.setClassName("AwesomeClass")
    var event = AccessibilityEvent()
    event.setEventTime(1357924680)
    event.setEventType(AccessibilityEvent.TYPE_VIEW_CLICKED)
    event.getText().add("Some text!")
    event.setPackageName("some.loooong.package.name")
    shadowOf(event).setSourceNode(nodeInfo)
    fakeA11yService.sendEventChecker = { _ ->
      // Delay the request to prompt a timeout
      delay(1500L)
      "" // Return no error.
    }

    // Act.
    forwarder.onAccessibilityEvent(event)

    // Run a second request to ensure that the channel gets rebuilt.
    fakeA11yService.sendEventChecker = { _ -> "" }
    forwarder.onAccessibilityEvent(event)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun onAccessibilityEvent_sendingevent_grpcStatusException() {
    // Arrange.
    createForwarder(logAccessibilityTree = false, grpcHost = "amazing.host", grpcPort = 4321)
    var nodeInfo = AccessibilityNodeInfo()
    nodeInfo.setContentDescription("My Content Description")
    nodeInfo.setText("My Source Text")
    nodeInfo.setClassName("AwesomeClass")
    var event = AccessibilityEvent()
    event.setEventTime(1357924680)
    event.setEventType(AccessibilityEvent.TYPE_VIEW_CLICKED)
    event.getText().add("Some text!")
    event.setPackageName("some.loooong.package.name")
    shadowOf(event).setSourceNode(nodeInfo)
    fakeA11yService.sendEventChecker = { _ -> throw StatusException(Status.UNAVAILABLE) }

    // Act.
    forwarder.onAccessibilityEvent(event)

    // Run a second request to ensure that the channel gets rebuilt.
    fakeA11yService.sendEventChecker = { _ -> "" }
    forwarder.onAccessibilityEvent(event)

    // Assert.
    // See `sendEventChecker` above.
  }

  @Test
  fun constructor_doesNotCaptureOrCreateChannelBeforeConnection() {
    var captures = 0
    createForwarder(
      logAccessibilityTree = true,
      a11yTreePeriodMs = 100,
      grpcPort = 1234,
      connect = false,
      captureWindows = { captures++; emptyList() },
    )

    scheduler.advanceTimeBy(1000)
    scheduler.runCurrent()
    assertThat(captures).isEqualTo(0)
    assertThat(channels).isEmpty()

    forwarder.onServiceConnected()
    assertThat(captures).isEqualTo(1)
    assertThat(fakeA11yService.forests).hasSize(1)
  }

  @Test
  fun repeatedConnection_hasOneWorkerAndKeepsOfficialCapturePeriod() {
    var captures = 0
    createForwarder(
      logAccessibilityTree = true,
      a11yTreePeriodMs = 100,
      grpcPort = 1234,
      captureWindows = { captures++; emptyList() },
    )

    forwarder.onServiceConnected()
    scheduler.advanceTimeBy(99)
    scheduler.runCurrent()
    assertThat(captures).isEqualTo(1)
    scheduler.advanceTimeBy(1)
    scheduler.runCurrent()
    assertThat(captures).isEqualTo(2)
    assertThat(channels).hasSize(1)
    assertThat(LogFlags.a11yTreePeriodMs).isEqualTo(100L)
  }

  @Test
  fun logAccessibilityTreeFalse_doesNotSendForest() {
    createForwarder(logAccessibilityTree = false, a11yTreePeriodMs = 100, grpcPort = 1234)
    scheduler.advanceTimeBy(1000)
    scheduler.runCurrent()
    assertThat(fakeA11yService.forests).isEmpty()
    assertThat(channels).isEmpty()
  }

  @Test
  fun grpcPortZero_doesNotSendForest() {
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 0)
    scheduler.advanceTimeBy(1000)
    scheduler.runCurrent()
    assertThat(fakeA11yService.forests).isEmpty()
    assertThat(channels).isEmpty()
  }

  @Test
  fun destroyingOldService_doesNotStopReplacementInstance() {
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)
    val old = forwarder
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)
    assertThat(fakeA11yService.forests).hasSize(2)

    old.onUnbind(Intent())
    old.onDestroy()
    scheduler.advanceTimeBy(100)
    scheduler.runCurrent()

    assertThat(fakeA11yService.forests).hasSize(3)
    assertTrue(channels[0].isShutdown)
    assertFalse(channels[1].isShutdown)
    assertThat(forestHeaders[0]["fsq-forwarder-instance"])
      .isNotEqualTo(forestHeaders[1]["fsq-forwarder-instance"])
    assertThat(forestHeaders[2]["fsq-forwarder-instance"])
      .isEqualTo(forestHeaders[1]["fsq-forwarder-instance"])
  }

  @Test
  fun connectedCapture_forwardsWindowAndActualEmptyForest() {
    val window = AccessibilityWindowInfo.obtain()
    shadowOf(window).setType(AccessibilityWindowInfo.TYPE_SYSTEM)
    createForwarder(
      logAccessibilityTree = true,
      a11yTreePeriodMs = 100,
      grpcHost = "amazing.host",
      grpcPort = 4321,
      a11yWindows = mutableListOf(window),
    )
    assertThat(fakeA11yService.forests.single().windowsList.single().windowType)
      .isEqualTo(AndroidAccessibilityWindowInfo.WindowType.TYPE_SYSTEM)
    assertThat(endpoints).containsExactly("amazing.host" to 4321)

    shadowOf(forwarder).setWindows(emptyList())
    scheduler.advanceTimeBy(100)
    scheduler.runCurrent()
    assertThat(fakeA11yService.forests).hasSize(2)
    assertThat(fakeA11yService.forests.last().windowsCount).isEqualTo(0)
    assertThat(forestHeaders.map { it["fsq-forest-sequence"] }).containsExactly("1", "2").inOrder()
    assertThat(forestHeaders.map { it["fsq-forwarder-generation"] }).containsExactly("1", "1")
    assertThat(forestHeaders[0]["fsq-forwarder-instance"]).isNotEmpty()
    assertThat(forestHeaders[1]["fsq-forwarder-instance"])
      .isEqualTo(forestHeaders[0]["fsq-forwarder-instance"])
  }

  @Test
  fun unbind_stopsCaptureAndEventsAndClosesChannel() {
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)
    assertThat(fakeA11yService.forests).hasSize(1)
    val oldChannel = channels.single()

    forwarder.onUnbind(Intent())
    forwarder.onAccessibilityEvent(clickedEvent())
    scheduler.advanceTimeBy(1000)
    scheduler.runCurrent()

    assertTrue(oldChannel.isShutdown)
    assertThat(fakeA11yService.forests).hasSize(1)
    assertThat(fakeA11yService.events).isEmpty()
    assertThat(LogFlags.a11yTreePeriodMs).isEqualTo(100L)
  }

  @Test
  fun destroy_cancelsInFlightRpcAndIsIdempotent() {
    var cancelled = false
    fakeA11yService.sendForestChecker = {
      try {
        awaitCancellation()
      } finally {
        cancelled = true
      }
    }
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)
    assertThat(fakeA11yService.forests).hasSize(1)

    forwarder.onDestroy()
    forwarder.onDestroy()
    forwarder.onUnbind(Intent())
    scheduler.advanceTimeBy(2000)
    scheduler.runCurrent()

    assertTrue(cancelled)
    assertTrue(channels.single().isShutdown)
    assertThat(fakeA11yService.forests).hasSize(1)
  }

  @Test
  fun unbindThenReconnect_usesNewChannelAndGenerationWithoutOldWorker() {
    var cancelled = false
    fakeA11yService.sendForestChecker = {
      try {
        awaitCancellation()
      } finally {
        cancelled = true
      }
    }
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)
    forwarder.onUnbind(Intent())
    assertTrue(cancelled)

    fakeA11yService.sendForestChecker = { "" }
    forwarder.onServiceConnected()
    forwarder.onServiceConnected()
    scheduler.advanceTimeBy(100)
    scheduler.runCurrent()

    assertThat(channels).hasSize(2)
    assertTrue(channels[0].isShutdown)
    assertFalse(channels[1].isShutdown)
    assertThat(fakeA11yService.forests).hasSize(3)
    assertThat(forestHeaders.map { it["fsq-forwarder-generation"] })
      .containsExactly("1", "2", "2").inOrder()
    assertThat(forestHeaders.map { it["fsq-forest-sequence"] })
      .containsExactly("1", "1", "2").inOrder()
    val sends = ShadowLog.getLogsForTag("AndroidRLTask").map { it.msg }
      .filter { it.startsWith("sending (blocking) gRPC request for tree") }
    assertThat(sends).hasSize(3)
    assertThat(sends[0]).contains("generation=1 source=capture")
    assertThat(sends[0]).contains("sequence=1")
    assertThat(sends[1]).contains("generation=2 source=capture")
    assertThat(sends[1]).contains("sequence=1")
    assertThat(sends[2]).contains("sequence=2")
  }

  @Test
  fun interrupt_isFeedbackOnlyAndDoesNotStopCaptureOrMutateFlags() {
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)
    forwarder.onInterrupt()
    scheduler.advanceTimeBy(100)
    scheduler.runCurrent()
    assertThat(fakeA11yService.forests).hasSize(2)
    assertThat(LogFlags.a11yTreePeriodMs).isEqualTo(100L)
    assertTrue(LogFlags.logAccessibilityTree)
    assertFalse(channels.single().isShutdown)
  }

  @Test
  fun unbind_interruptsCaptureBeforeAnyLateSendAndReconnects() {
    val entered = CountDownLatch(1)
    val exited = CountDownLatch(1)
    val neverReleased = CountDownLatch(1)
    val sent = CountDownLatch(1)
    val captures = AtomicInteger()
    fakeA11yService.sendForestChecker = { sent.countDown(); awaitCancellation() }
    createForwarder(
      logAccessibilityTree = true,
      a11yTreePeriodMs = 100,
      grpcPort = 1234,
      connect = false,
      workerDispatcher = Dispatchers.IO,
      captureWindows = {
        if (captures.incrementAndGet() == 1) {
          entered.countDown()
          try {
            neverReleased.await()
          } finally {
            exited.countDown()
          }
        }
        emptyList()
      },
    )
    forwarder.onServiceConnected()
    assertTrue(entered.await(5, TimeUnit.SECONDS))

    forwarder.onUnbind(Intent())
    assertTrue(exited.await(5, TimeUnit.SECONDS))
    assertThat(fakeA11yService.forests).isEmpty()
    assertThat(channels).isEmpty()

    forwarder.onServiceConnected()
    assertTrue(sent.await(5, TimeUnit.SECONDS))
    forwarder.onUnbind(Intent())
    assertThat(fakeA11yService.forests).hasSize(1)
    assertTrue(channels.single().isShutdown)
  }

  @Test
  fun sendingForest_timeoutClosesChannelAndNextCaptureRebuildsIt() {
    fakeA11yService.sendForestChecker = { delay(1500); "" }
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)

    scheduler.advanceTimeBy(1000)
    scheduler.runCurrent()
    assertTrue(channels.single().isShutdown)
    fakeA11yService.sendForestChecker = { "" }
    scheduler.advanceTimeBy(100)
    scheduler.runCurrent()

    assertThat(channels).hasSize(2)
    assertFalse(channels[1].isShutdown)
    assertThat(fakeA11yService.forests).hasSize(2)
  }

  @Test
  fun sendingForest_statusExceptionClosesChannelAndNextCaptureRebuildsIt() {
    fakeA11yService.sendForestChecker = { throw StatusException(Status.UNAVAILABLE) }
    createForwarder(logAccessibilityTree = true, a11yTreePeriodMs = 100, grpcPort = 1234)
    assertTrue(channels.single().isShutdown)

    fakeA11yService.sendForestChecker = { "" }
    scheduler.advanceTimeBy(100)
    scheduler.runCurrent()
    assertThat(channels).hasSize(2)
    assertFalse(channels[1].isShutdown)
    assertThat(fakeA11yService.forests).hasSize(2)
  }

  private fun clickedEvent(): AccessibilityEvent = AccessibilityEvent.obtain().apply {
    eventType = AccessibilityEvent.TYPE_VIEW_CLICKED
    text.add("click")
  }
}
