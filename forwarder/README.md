# Accessibility forwarder lifecycle repair

This standalone Android application is the accessibility-forwarder replacement introduced in Harness 14 and retained unchanged in Harness 15. It preserves the official protobuf schemas and task/evaluator behavior. The original APK/cache entry and historical campaign results remain unchanged.

## Lifecycle contract

- Start capture in `onServiceConnected`, never in the service constructor. Duplicate connected callbacks retain one worker.
- Unbind/destroy cancels the connection-owned coroutine hierarchy and RPC, interrupts capture, closes its channel, and joins worker completion before returning. Reconnection starts a new connection; a replacement service object has a new instance identifier.
- `onInterrupt` interrupts accessibility feedback, not connectivity; it does not disable process-wide capture flags.
- Genuine empty forests remain valid payloads and are not filtered. Capture remains 100 ms by default; the RPC timeout remains 1000 ms.
- Logs and SendForest metadata identify service instance, connection generation, and per-connection forest sequence. A coroutine dispatcher can reuse a native thread ID; thread identity is not worker ownership.

Harness 14 canonicalizes W3C capability candidates and forwards explicit `appium:disableSuppressAccessibilityService: true`. Contradictory requests fail before forwarding. Missing/false returned confirmation fails closed while retaining a created session's ownership for reconciliation. Configuration identity and actual request/response evidence are bound into preparation, manifests, episode records, qualification and scoring. Historical r12/r13 scoring paths are not migrated.

## Harness 15 reference-clock boundary

Harness 15 adds only the public `task.device_time` reference captured after successful official task initialization. `taskTimeContext` protocol version 1 identifies `initialized_task.device_time` and `initialization_reference_not_live`; the episode's `task.timeContext` records the timezone-aware ISO reference and its canonical UTC-offset timezone. The same context is delivered outside the exact goal. Relative dates use this task reference, not the host date; the goal's week-start convention remains authoritative. This is not a live device-clock measurement and includes no hidden parameters or expected answers.

Naive timestamps are rejected. Scoring and calibration provenance require the new context while preserving bounded business receipts from r13 and actual accessibility coexistence evidence from r14. A pre-Agent initialization error may lack a reference instead of inventing one. Saved r12/r13/r14 records gain no clock requirement. Goals, frozen parameters, budgets, models and official evaluator semantics do not change; the new source/prompt/protocol identity requires fresh qualification, full rehearsal and calibration before any new formal run. No APK rebuild or installed dependency change is part of this cutover.

Offline verification and the 18-case contract audit are in `../evidence/remaining-failures-batch-20261109T110443Z/harness/`. These are development checks, not a task replay, live readiness proof, new evaluator reward or formal score. The Appium Settings clipboard getter's observed helper-startup timeout does not establish a Harness preparation defect; no helper force-start or capability change was applied.

## Build and artifact identity

Pinned build: Gradle 8.9, Android Gradle Plugin 8.7.3, Kotlin 2.0.21, Android platform 33, build-tools 35.0.0, JVM target 17. The recorded build used JDK 21. Dependencies and schema digests are recorded in `build.gradle.kts` and `schema-provenance.json`.

With the already provisioned isolated SDK, Gradle distribution and dependency cache:

```sh
JAVA_HOME="$JDK_HOME" \
ANDROID_HOME="$ISOLATED_ANDROID_SDK" \
GRADLE_USER_HOME="$ISOLATED_GRADLE_CACHE" \
"$GRADLE_8_9/bin/gradle" -p forwarder --no-daemon --offline \
  testDebugUnitTest assembleDebug writeForwarderProvenance
```

Run from the evaluation repository root. This command does not provision missing dependencies. Outputs are `forwarder/build/outputs/apk/debug/forwarder-debug.apk` and `forwarder/build/forwarder-provenance.json`.

The deployed artifact is `../assets/fsq-accessibility-forwarder-lifecycle-v1.apk`; its recorded build/source hashes are in the adjacent JSON. `../src/fsq_androidworld_eval/environment.py` pins its exact hash and size. Rebuilding or re-signing does not guarantee byte identity: refresh the release identity/pins and qualifications before using different bytes. Never overwrite the original frozen helper cache.

## Exercised scope and limits

The fixed diagnostic matrix and causal evidence are in `../evidence/accessibility-coexistence-repair-20261109T064155Z/repair-report.md`. It includes four Clock cells and BrowserDraw/Calendar regressions, not a formal 116-task campaign. The final environment was restored to the production helper and normal binding.

An Android `Init UiAutomation ... flags=0` log is not a measurement of final effective flags. The saved dumpsys captures show actual coexistence/binding but do not expose numeric flags. Preserve this distinction rather than substituting capability echoes for native state.
