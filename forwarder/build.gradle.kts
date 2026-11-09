import com.google.protobuf.gradle.id
import java.security.MessageDigest

plugins {
  id("com.android.application") version "8.7.3"
  id("org.jetbrains.kotlin.android") version "2.0.21"
  id("org.jetbrains.kotlin.kapt") version "2.0.21"
  id("com.google.protobuf") version "0.9.4"
}

require(gradle.gradleVersion == "8.9") { "Use the pinned Gradle 8.9 distribution for this build." }

// Standalone native fork: the frozen AndroidWorld Python checkout stays untouched.
val forwarderSources = "src"

android {
  namespace = "com.google.androidenv.accessibilityforwarder"
  compileSdk = 33
  buildToolsVersion = "35.0.0"

  defaultConfig {
    applicationId = "com.google.androidenv.accessibilityforwarder"
    minSdk = 28
    targetSdk = 33
    versionCode = 20261109
    versionName = "2026.11.09-lifecycle1"
  }

  sourceSets {
    getByName("main") {
      manifest.srcFile("$forwarderSources/AndroidManifest.xml")
      res.setSrcDirs(listOf("$forwarderSources/res"))
    }
  }

  compileOptions {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
  }
  kotlinOptions.jvmTarget = "17"
  testOptions.unitTests.isIncludeAndroidResources = true
  packaging.resources.excludes += setOf("META-INF/INDEX.LIST", "META-INF/io.netty.versions.properties")
}

kotlin.sourceSets {
  getByName("main").kotlin.apply {
    setSrcDirs(listOf(forwarderSources))
    exclude("**/*Test.kt")
  }
  getByName("test").kotlin.apply {
    setSrcDirs(listOf(forwarderSources))
    include("**/*Test.kt")
  }
}

protobuf {
  protoc { artifact = "com.google.protobuf:protoc:3.25.5" }
  plugins {
    id("grpc") { artifact = "io.grpc:protoc-gen-grpc-java:1.76.0" }
    id("grpckt") { artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.1:jdk8@jar" }
  }
  generateProtoTasks {
    all().configureEach {
      builtins { id("java"); id("kotlin") }
      plugins {
        id("grpc")
        id("grpckt")
      }
    }
  }
}

dependencies {
  implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
  implementation("com.google.protobuf:protobuf-kotlin:3.25.5")
  implementation("io.grpc:grpc-okhttp:1.76.0")
  implementation("io.grpc:grpc-protobuf:1.76.0")
  implementation("io.grpc:grpc-stub:1.76.0")
  implementation("io.grpc:grpc-kotlin-stub:1.4.1")
  implementation("com.google.code.gson:gson:2.11.0")
  compileOnly("javax.annotation:javax.annotation-api:1.3.2")
  compileOnly("com.google.auto.value:auto-value-annotations:1.11.0")
  kapt("com.google.auto.value:auto-value:1.11.0")

  testImplementation("junit:junit:4.13.2")
  testImplementation("org.robolectric:robolectric:4.14.1")
  testImplementation("com.google.truth:truth:1.4.4")
  testImplementation("org.jetbrains.kotlin:kotlin-test:2.0.21")
  testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
  testImplementation("io.grpc:grpc-inprocess:1.76.0")
  testImplementation("io.grpc:grpc-testing:1.76.0")
}

tasks.register("writeForwarderProvenance") {
  dependsOn("assembleDebug")
  val sourceFiles = files(
    fileTree(forwarderSources) { exclude("**/*Test.kt", "AndroidManifest_lite.xml") },
    fileTree("src/main/proto"),
    "build.gradle.kts",
    "settings.gradle.kts",
    "gradle.properties",
    "schema-provenance.json",
  )
  inputs.files(sourceFiles)
  inputs.file(layout.buildDirectory.file("outputs/apk/debug/forwarder-debug.apk"))
  val provenance = layout.buildDirectory.file("forwarder-provenance.json")
  outputs.file(provenance)
  doLast {
    fun sha256(file: File): String = MessageDigest.getInstance("SHA-256")
      .digest(file.readBytes()).joinToString("") { "%02x".format(it) }
    val apk = layout.buildDirectory.file("outputs/apk/debug/forwarder-debug.apk").get().asFile
    val content = mapOf(
      "versionName" to android.defaultConfig.versionName,
      "versionCode" to android.defaultConfig.versionCode,
      "gradleVersion" to gradle.gradleVersion,
      "javaVersion" to System.getProperty("java.version"),
      "apk" to apk.relativeTo(projectDir).invariantSeparatorsPath,
      "apkSha256" to sha256(apk),
      "sources" to sourceFiles.files.sortedBy { it.path }.associate {
        it.relativeTo(rootDir.parentFile).invariantSeparatorsPath to sha256(it)
      },
    )
    provenance.get().asFile.writeText(groovy.json.JsonOutput.prettyPrint(groovy.json.JsonOutput.toJson(content)) + "\n")
  }
}
