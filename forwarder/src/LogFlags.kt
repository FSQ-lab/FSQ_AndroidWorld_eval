package com.google.androidenv.accessibilityforwarder

/**
 * Controls global settings in AccessibilityForwarder.
 *
 * Individual values are volatile because broadcasts update them while the capture worker reads them.
 */
object LogFlags {
  // The frozen APK streams via gRPC without an ENABLE_GRPC broadcast; official
  // AndroidEnv configures only SET_GRPC and ENABLE_ACCESSIBILITY_TREE_LOGS.
  @Volatile var logUsingGRPC: Boolean = true
  @Volatile var logUsingInternalStorage: Boolean = false

  // Whether to log the accessibility tree.
  @Volatile var logAccessibilityTree: Boolean = false
  // How frequent to emit a11y trees (in milliseconds).
  @Volatile var a11yTreePeriodMs: Long = 100

  // The gRPC server to connect to. (Only available if grpcPort>0).
  @Volatile var grpcHost: String = ""
  // If >0 this represents the gRPC port number to connect to.
  @Volatile var grpcPort: Int = 0
}
