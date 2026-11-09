import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import sys
import time

import pytest

from fsq_androidworld_eval.campaign import (
    CALIBRATION_TASKS,
    _classification,
    _cleanup_failed,
    _group_metrics,
    _load_manifest,
    _prepare_agent_workspace,
    _readiness_identity,
    _retryable,
    _write_summary,
    build_manifest,
)
from fsq_androidworld_eval.continuation import CAMPAIGN_CONTINUATION, INHERITED_TASKS_SHA256
from fsq_androidworld_eval.runner import _sha256, _task
from fsq_androidworld_eval.lifecycle import TIME_BUDGET_PROTOCOL, episode_time_budget
from fsq_androidworld_eval.appium_proxy import SESSION_ACCESSIBILITY_CONFIG

FROZEN_SOURCE = Path(__file__).resolve().parents[1] / "campaigns/amkernel-3388314-r11-timeout300-full-20261106T142607Z/manifest.json"


@pytest.fixture(autouse=True)
def isolated_artifact_identity(monkeypatch):
    from fsq_androidworld_eval import campaign

    source = json.loads(FROZEN_SOURCE.read_text())
    runtime = json.loads(json.dumps(source["protocol"]["runtimeIdentity"]))
    runtime["harnessSourceSha256"] = "c" * 64
    monkeypatch.setattr(campaign, "_runtime_identity", lambda project: json.loads(json.dumps(runtime)))
    artifacts = json.loads(json.dumps(source["protocol"]["environmentArtifacts"]))
    helper = next(row for row in artifacts["artifacts"] if row["name"] == SESSION_ACCESSIBILITY_CONFIG["inheritedForwarderArtifactName"])
    helper.update(name=SESSION_ACCESSIBILITY_CONFIG["forwarderArtifactName"], sha256="d" * 64,
                  sizeBytes=1234, url="repo:assets/fsq-accessibility-forwarder-lifecycle-v1.apk")
    monkeypatch.setattr(campaign, "artifact_identity", lambda project: json.loads(json.dumps(artifacts)))

def _submission_artifacts(directory: Path, business_seconds: int) -> tuple[dict, dict, str]:
    import hashlib
    from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL, parse_submission

    raw = directory / "raw-private"
    raw.mkdir()
    text = json.dumps({"taskOutcome": "fixture answer"})
    events = [{"type": "message_end", "message": {
        "role": "assistant", "stopReason": "stop", "content": [{"type": "text", "text": text}]
    }}, {"type": "agent_end", "isTerminal": True}]
    event_bytes = ("\n".join(json.dumps(event) for event in events) + "\n").encode()
    (raw / "agent-events.jsonl").write_bytes(event_bytes)
    report = parse_submission(text)
    submission_bytes = json.dumps(report).encode()
    (raw / "business-submission.json").write_bytes(submission_bytes)
    digest = hashlib.sha256(submission_bytes).hexdigest()
    evidence = {"protocol": ANSWER_SUBMISSION_PROTOCOL,
                "path": "raw-private/business-submission.json", "sha256": digest,
                "receipt": {"eventSequence": 1, "receivedAtSeconds": 0.1, "phase": "business"},
                "cutoffSeconds": 0.2, "businessDeadlineSeconds": business_seconds,
                "finalizationStartedAtSeconds": None, "finalizationDeadlineSeconds": None,
                "cleanupRequestedAtSeconds": 0.2, "ignoredFinalMessages": 0}
    answer = {key: report[key] for key in ("validContract", "reason", "taskOutcomeType", "sha256")}
    answer["rawSubmission"] = {"path": evidence["path"], "sha256": digest}
    return evidence, answer, hashlib.sha256(event_bytes).hexdigest()


def _qualified_calibration_campaign(root: Path) -> Path:
    root.mkdir(parents=True)
    manifest = build_manifest("calibration-proof", inherit_manifest=FROZEN_SOURCE)
    (root / "manifest.json").write_text(json.dumps(manifest))
    readiness = _fixture_readiness(manifest)
    (root / "device-readiness.json").write_text(json.dumps(readiness))
    (root / "run-metadata.json").write_text(json.dumps({
        "campaignId": manifest["campaignId"], "manifestSha256": _sha256(manifest),
        "readinessIdentitySha256": readiness["identitySha256"],
        "liveTargetAttestation": _fixture_attestation(), "startedAtUnix": 0,
        "initialCoreServices": _fixture_core_services(),
    }))
    events = []
    for task in manifest["tasks"]:
        result_path = (
            root
            / "episodes"
            / f"{task['index']:03d}-{task['name']}"
            / "attempt-1"
            / "result.json"
        )
        result_path.parent.mkdir(parents=True, exist_ok=True)
        submission, answer, raw_events_sha = _submission_artifacts(result_path.parent, task["timeBudget"]["businessSeconds"])
        result_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 3,
                    "startedAtUnix": task["index"] * 2 + 1.1,
                    "completedAtUnix": task["index"] * 2 + 1.9,
                    "androidWorld": {"revision": manifest["protocol"]["androidWorldRevision"]},
                    "amkernel": {
                        "version": manifest["protocol"]["runtimeIdentity"]["amkernelVersion"],
                        "tool": "python_exec",
                    },
                    "target": {"serial": manifest["target"]["serial"]},
                    "task": {
                        "name": task["name"],
                        "seed": task["instanceSeed"],
                        "params": task["params"],
                        "paramsSha256": task["paramsSha256"],
                        "complexity": task["complexity"],
                        "timeContext": {"referenceTime": "2023-10-15T15:34:00+00:00", "timezone": "UTC"},
                    },
                    "protocol": {
                        "harnessRevision": manifest["protocol"]["harnessRevision"],
                        "promptTemplateSha256": manifest["protocol"]["promptTemplateSha256"],
                        "mcpRequestTimeoutMs": manifest["protocol"]["mcpRequestTimeoutMs"],
                        "sessionCreationTimeoutSeconds": manifest["protocol"]["sessionCreationTimeoutSeconds"],
                        "readinessIdentitySha256": readiness["identitySha256"],
                        "pythonExecCallAdvisory": manifest["protocol"]["pythonExecCallAdvisory"],
                        "stepBudget": manifest["protocol"]["stepBudget"],
                        "timeBudget": manifest["protocol"]["timeBudget"],
                        "answerSubmission": manifest["protocol"]["answerSubmission"],
                        "environmentArtifacts": manifest["protocol"]["environmentArtifacts"],
                        "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
                        "taskTimeContext": manifest["protocol"]["taskTimeContext"],
                    },
                    "timeBudget": task["timeBudget"],
                    "agent": {
                        "answerSubmission": submission,
                        "rawEventsSha256": raw_events_sha,
                        "agentCompleted": True,
                        "termination": {"reason": "completed"},
                        "normalized": {
                            "provider": "github-copilot",
                            "model": "gpt-5.6-sol",
                            "parseErrors": 0,
                            "toolCalls": [
                                {
                                    "tool": "write",
                                    "target": "xd://mcp__amkernel_python_exec",
                                    "sessionCleanup": {
                                        "sessionIdSha256": "b" * 64,
                                        "quitReturned": True,
                                    },
                                }
                            ],
                        }
                    },
                    "agentAnswer": answer,
                    "appiumSessionAudit": {
                        "createdSessionCount": 1,
                        "createdSessionHashes": ["b" * 64],
                        "deletedSessionCount": 1,
                        "deletedSessionHashes": ["b" * 64],
                        "errors": [],
                        "sessionAccessibility": _fixture_accessibility(manifest["target"]["serial"]),
                    },
                    "budget": {"pythonExecCalls": 1, "exceededAdvisory": False,
                               "advisory": manifest["protocol"]["pythonExecCallAdvisory"],
                               "affectsOfficialReward": False},
                    "stepBudget": {
                        "protocol": manifest["protocol"]["stepBudget"],
                        "maxSteps": task["maxSteps"],
                        "referenceStepsExecuted": 1,
                        "executedActionCount": 0,
                        "rejectedActionCount": 0,
                        "actions": [],
                        "agentIndicatedDone": True,
                        "exhausted": False,
                    },
                    "evaluator": {
                        "implementation": "android_world.task_eval.is_successful"
                    },
                    "error": None,
                    "officialReward": 1.0,
                    "cleanup": {
                        "agentSession": {
                            "status": "closed",
                            "sessionIdSha256": "b" * 64,
                            "verificationStatus": "absent",
                        },
                        "taskTearDown": "completed",
                        "environment": "closed",
                    },
                }
            )
        )
        from fsq_androidworld_eval import campaign
        binding = {
            "taskIndex": task["index"], "task": task["name"], "attempt": 1,
            "manifestSha256": _sha256(manifest),
            "readinessIdentitySha256": readiness["identitySha256"],
            "taskSpecSha256": _sha256(task), "result": str(result_path.relative_to(root)),
        }
        events.extend([
            {**binding, "event": "attempt_started", "startedAtUnix": task["index"] * 2 + 1},
            {**binding, "event": "attempt_terminal", "completedAtUnix": task["index"] * 2 + 2,
             "classification": "passed", "officialReward": 1.0,
             "resultSha256": campaign._file_sha256(result_path)},
        ])
    events.append({"event": "finished", "completedAtUnix": len(manifest["tasks"]) * 2 + 1})
    (root / "checkpoint.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))
    _write_summary(root, manifest)
    return root


def _fixture_accessibility(serial: str) -> dict:
    capabilities = {"alwaysMatch": {
        "platformName": "Android", "appium:automationName": "UiAutomator2", "appium:udid": serial,
        "appium:noReset": True, "appium:skipUnlock": True, "appium:autoLaunch": False,
        SESSION_ACCESSIBILITY_CONFIG["capability"]: True,
    }, "firstMatch": [{}]}
    body = json.dumps({"capabilities": capabilities}, sort_keys=True).encode()
    returned = {"disableSuppressAccessibilityService": True}
    return {"config": SESSION_ACCESSIBILITY_CONFIG, "creations": [{
        "request": {"capabilities": capabilities, "sha256": hashlib.sha256(body).hexdigest(), "byteCount": len(body)},
        "response": {"status": 200, "bodySha256": "a" * 64, "capabilities": returned,
                     "capabilityByteCount": len(json.dumps(returned, sort_keys=True).encode()), "confirmed": True},
    }]}


def _fixture_readiness(manifest: dict) -> dict:
    readiness = {
        "schemaVersion": 2, "manifestSha256": _sha256(manifest), "qualified": True,
        "environmentClose": "closed", "adbOutputIsolated": True,
        "environmentArtifacts": manifest["protocol"]["environmentArtifacts"],
        "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
        "snapshotRestores": [{"app": app, "status": "restored"} for app in sorted({
            app for task in manifest["tasks"] for app in task["apps"]
        })],
        "target": manifest["target"],
    }
    readiness["identitySha256"] = _sha256(readiness)
    return readiness


def _fixture_attestation() -> dict:
    attestation = {"qualified": True, "mismatches": {}}
    attestation["identitySha256"] = _sha256(attestation)
    return attestation


def _fixture_core_services() -> dict:
    return {
        "adbState": "device", "bootCompleted": "1", "activityService": True,
        "packageService": True, "settingsService": True, "windowService": True,
        "systemServerPids": ["333"], "surfaceFlingerPids": ["500"],
        "bootId": "0f36e370-012a-4423-a1f9-959beae8f90d",
        "appiumReady": True, "grpcReady": True, "qualified": True,
    }


def test_manifest_freezes_ordered_reproducible_parameters(tmp_path: Path) -> None:
    manifest = build_manifest("test-campaign")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))

    loaded = _load_manifest(path)

    assert loaded["schemaVersion"] == 2
    assert loaded["protocol"]["scoreContract"] == "official_reward_only"
    assert [task["name"] for task in loaded["tasks"]] == CALIBRATION_TASKS
    assert loaded["protocol"]["timeBudget"] == TIME_BUDGET_PROTOCOL
    assert "agentTimeoutSeconds" not in loaded["protocol"]
    assert "episodeTimeoutSeconds" not in loaded["protocol"]
    for task_spec in loaded["tasks"]:
        regenerated = _task(
            task_spec["name"], params_json=None, task_seed=task_spec["instanceSeed"]
        )
        assert _sha256(regenerated.params) == task_spec["paramsSha256"]
        assert task_spec["timeBudget"] == episode_time_budget(task_spec["maxSteps"])


def test_calibration_manifest_rejects_previous_harness_protocol(tmp_path: Path) -> None:
    manifest = build_manifest("stale-protocol")
    manifest["protocol"]["harnessRevision"] -= 1
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))

    with pytest.raises(ValueError):
        _load_manifest(path)


def test_full_manifest_contains_reproducible_official_116_task_split(tmp_path: Path) -> None:
    calibration_dir = _qualified_calibration_campaign(tmp_path / "calibration")
    manifest = build_manifest(
        "full-campaign", kind="full", calibration_campaign_dir=calibration_dir
    )

    families = [task["family"] for task in manifest["tasks"]]
    assert len(manifest["tasks"]) == 116
    assert families.count("android") == 91
    assert families.count("information_retrieval") == 25
    assert all(task["difficulty"] != "unknown" for task in manifest["tasks"])
    assert manifest["calibrationGate"]["campaignId"] == "calibration-proof"
    assert len(CALIBRATION_TASKS) == 12
    for task_spec in manifest["tasks"]:
        if task_spec["paramsTransport"] == "json":
            reconstructed = _task(
                task_spec["name"],
                params_json=json.dumps(task_spec["params"]),
                task_seed=None,
            )
        else:
            reconstructed = _task(
                task_spec["name"],
                params_json=None,
                task_seed=task_spec["instanceSeed"],
            )
        assert _sha256(reconstructed.params) == task_spec["paramsSha256"]


def test_full_manifest_rejects_missing_or_unqualified_calibration(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        build_manifest("full-without-gate", kind="full")
    calibration_dir = _qualified_calibration_campaign(tmp_path / "calibration")
    first_result = next(calibration_dir.glob("episodes/*/attempt-1/result.json"))
    record = json.loads(first_result.read_text())
    record["agent"]["normalized"]["toolCalls"] = []
    first_result.write_text(json.dumps(record))
    calibration_manifest = json.loads((calibration_dir / "manifest.json").read_text())
    _write_summary(calibration_dir, calibration_manifest)
    with pytest.raises(ValueError):
        build_manifest(
            "full-bad-gate", kind="full", calibration_campaign_dir=calibration_dir
        )


def test_group_metrics_uses_numeric_official_reward_and_excludes_invalid() -> None:
    tasks = [
        {"index": 0, "family": "android"},
        {"index": 1, "family": "android"},
        {"index": 2, "family": "information_retrieval"},
    ]
    episodes = [
        {"index": 0, "classification": "passed", "officialReward": 1.0},
        {"index": 1, "classification": "invalid_setup", "officialReward": None},
        {"index": 2, "classification": "failed", "officialReward": 0.5},
    ]

    metrics = _group_metrics(tasks, episodes, "family")

    assert metrics["android"]["scoreOnValidEpisodes"] == 1.0
    assert metrics["android"]["lowerBoundScoreOnPlannedEpisodes"] == 0.5
    assert metrics["android"]["invalidEpisodeCount"] == 1
    assert metrics["information_retrieval"]["scoreOnValidEpisodes"] == 0.5


def test_classification_never_lets_call_budget_change_reward() -> None:
    assert _classification(
        {"error": {"type": "SetupError"}, "invalidReason": "invalid_setup"}
    ) == "invalid_setup"
    assert _classification(
        {"error": None, "officialReward": 0.0, "budget": {"exceeded": False}}
    ) == "failed"
    assert _classification(
        {"error": None, "officialReward": 1.0, "budget": {"exceeded": True}}
    ) == "passed"


@pytest.mark.parametrize("status", ["unknown", "leaked", "harness_reclaimed", "idle_timeout"])
def test_cleanup_distinguishes_agent_close_from_non_agent_cleanup(status: str) -> None:
    base = {"taskTearDown": "completed", "environment": "closed"}
    assert _cleanup_failed({"cleanup": {**base, "agentSession": {"status": "closed"}}}) is False
    assert _cleanup_failed(
        {
            "error": {"type": "InfrastructureError"},
            "cleanup": {**base, "agentSession": {"status": "not_created"}},
        }
    ) is False
    assert _cleanup_failed(
        {"error": None, "cleanup": {**base, "agentSession": {"status": "not_created"}}}
    ) is True
    assert _cleanup_failed({"cleanup": {**base, "agentSession": {"status": status}}}) is True


def test_agent_workspace_contains_only_agent_assets(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"

    identity = _prepare_agent_workspace(Path.cwd(), workspace)

    assert identity["fileCount"] > 0
    assert (workspace / ".agents/skills/amkernel/SKILL.md").is_file()
    assert json.loads((workspace / ".omp/mcp.json").read_text())["mcpServers"]["amkernel"]["cwd"] == "."
    assert not (workspace / "src").exists()
    assert not (workspace / "android_world").exists()
    assert not (workspace / "campaigns").exists()
    assert not (workspace / "evidence").exists()
    sandbox = subprocess.run(
        [
            "/usr/bin/sandbox-exec",
            "-f",
            str(workspace / ".sandbox.sb"),
            str(Path(sys.executable).resolve()),
            "-c",
            f"open({str((Path.cwd() / 'src/fsq_androidworld_eval/runner.py').resolve())!r}).read()",
        ],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    assert sandbox.returncode != 0
    assert "Operation not permitted" in sandbox.stderr


def test_unknown_runner_state_is_never_retryable() -> None:
    assert _retryable(
        {
            "error": {"type": "MissingResult"},
            "invalidReason": "invalid_agent",
            "agent": {"state": "unknown"},
        }
    ) is False


@pytest.mark.parametrize("change", ["none", "old_schema", "contaminated_adb", "missing_app", "failed_restore", "duplicate_app"])
def test_readiness_gate_requires_clean_capture_and_every_snapshot(tmp_path: Path, change: str) -> None:
    manifest = build_manifest("readiness-campaign")
    apps = sorted({app for task in manifest["tasks"] for app in task["apps"]})
    report = {
        "schemaVersion": 2,
        "campaignId": manifest["campaignId"],
        "manifestSha256": _sha256(manifest),
        "qualified": True,
        "environmentClose": "closed",
        "adbOutputIsolated": True,
        "snapshotRestores": [{"app": app, "status": "restored"} for app in apps],
        "environmentArtifacts": manifest["protocol"]["environmentArtifacts"],
        "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
        "target": manifest["target"],
    }
    if change == "old_schema":
        report["schemaVersion"] = 1
    elif change == "contaminated_adb":
        report["adbOutputIsolated"] = False
    elif change == "missing_app":
        report["snapshotRestores"].pop()
    elif change == "failed_restore":
        report["snapshotRestores"][0]["status"] = "failed"
    elif change == "duplicate_app":
        report["snapshotRestores"][0] = report["snapshotRestores"][1]
    report["identitySha256"] = _sha256(report)
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(report))

    if change == "none":
        _readiness_identity(path, manifest)
    else:
        with pytest.raises(ValueError, match="ADB capture|snapshot restore"):
            _readiness_identity(path, manifest)


@pytest.mark.parametrize("value", [None, {}, {"version": 0}])
def test_readiness_rejects_missing_or_different_accessibility_config(tmp_path, value):
    manifest = build_manifest("accessibility-readiness")
    report = _fixture_readiness(manifest)
    report["sessionAccessibilityConfig"] = value
    report["identitySha256"] = _sha256({key: item for key, item in report.items() if key != "identitySha256"})
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="session accessibility configuration"):
        _readiness_identity(path, manifest)


def test_readiness_identity_rejects_environment_close_failure(tmp_path: Path) -> None:
    manifest = build_manifest("readiness-close-failure")
    report = {
        "schemaVersion": 1,
        "campaignId": manifest["campaignId"],
        "manifestSha256": _sha256(manifest),
        "qualified": True,
        "environmentClose": "failed:RuntimeError",
    }
    report["identitySha256"] = _sha256(report)
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(report))

    with pytest.raises(ValueError, match="did not close"):
        _readiness_identity(path, manifest)


def test_full_campaign_rejects_reward_without_reference_budget_proof(tmp_path: Path) -> None:
    calibration_dir = _qualified_calibration_campaign(tmp_path / "calibration")
    result_path = next(calibration_dir.glob("episodes/*/attempt-1/result.json"))
    record = json.loads(result_path.read_text())
    record["stepBudget"]["executedActionCount"] = record["stepBudget"]["maxSteps"] + 1
    result_path.write_text(json.dumps(record))
    manifest = json.loads((calibration_dir / "manifest.json").read_text())
    _write_summary(calibration_dir, manifest)
    with pytest.raises(ValueError):
        build_manifest("over-budget", kind="full", calibration_campaign_dir=calibration_dir)


def test_agent_sandbox_denies_direct_android_transports(tmp_path: Path) -> None:
    workspace = tmp_path / "agent"
    _prepare_agent_workspace(Path.cwd(), workspace)
    probe = subprocess.run(
        [
            "/usr/bin/sandbox-exec", "-f", str(workspace / ".sandbox.sb"),
            str(Path(sys.executable).resolve()), "-c",
            "import json,socket; "
            "ports=(4723,5037,5554,8554,8200,8299); "
            "print(json.dumps([socket.socket().connect_ex(('127.0.0.1',p)) for p in ports]))",
        ],
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    )
    import errno
    assert json.loads(probe.stdout) == [errno.EPERM] * 6




def _scheduler_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from fsq_androidworld_eval import campaign

    evidence = _qualified_calibration_campaign(tmp_path / "evidence")
    manifest = json.loads((evidence / "manifest.json").read_text())
    records = {task["index"]: json.loads((evidence / "episodes" / campaign._episode_slug(task)
               / "attempt-1/result.json").read_text()) for task in manifest["tasks"]}
    output = tmp_path / "campaign-run"
    monkeypatch.setattr(campaign, "validate_report", lambda *_args: "rehearsal-sha")
    monkeypatch.setattr(campaign.shutil, "copytree", lambda *_args: None)
    monkeypatch.setattr(campaign, "attest_device", lambda *_args: _fixture_attestation())
    monkeypatch.setattr(campaign, "_appium_session_hashes", lambda *_args: [])
    monkeypatch.setattr(campaign, "_core_service_health", lambda *_args: _fixture_core_services())
    monkeypatch.setattr(campaign, "_prepare_agent_workspace", lambda *_args: {"fileCount": 0})
    launched = []

    def fake_attempt(_manifest, task, attempt_dir, *_args):
        checkpoint = [json.loads(line) for line in (output / "checkpoint.jsonl").read_text().splitlines()]
        assert checkpoint[-1]["event"] == "attempt_started"
        assert checkpoint[-1]["taskSpecSha256"] == _sha256(task)
        assert checkpoint[-1]["result"] == str((attempt_dir / "result.json").relative_to(output))
        assert not attempt_dir.exists()
        attempt_dir.mkdir(parents=True)
        raw = attempt_dir / "raw-private"
        raw.mkdir()
        original_raw = evidence / "episodes" / campaign._episode_slug(task) / "attempt-1" / "raw-private"
        for name in ("business-submission.json", "agent-events.jsonl"):
            (raw / name).write_bytes((original_raw / name).read_bytes())
        launched.append((task["index"], int(attempt_dir.name.split("-")[-1])))
        record = json.loads(json.dumps(records[task["index"]]))
        record["startedAtUnix"] = time.time()
        record["completedAtUnix"] = time.time()
        return record

    monkeypatch.setattr(campaign, "_run_attempt", fake_attempt)
    args = SimpleNamespace(
        project=str(tmp_path), manifest=str(evidence / "manifest.json"), output_dir=str(output),
        readiness_report=str(evidence / "device-readiness.json"), adb_path="/fake/adb",
        rehearsal_report=str(tmp_path / "rehearsal/report.json"),
    )
    return args, manifest, records, launched, output


def test_fresh_campaign_records_first_launch_and_all_terminals(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, manifest, _records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    assert campaign.run_campaign(args) == 0
    assert launched == [(index, 1) for index in range(12)]
    summary = json.loads((output / "summary.json").read_text())
    assert summary["actualStartedEpisodeCount"] == 12
    assert summary["actualAttemptStartCount"] == 12
    assert summary["unstartedTaskIndexes"] == []
    assert summary["coverageAudit"]["valid"] is True
    assert summary["legacyOfficialScore"] is None
    assert (output / "manifest.json").read_bytes() == Path(args.manifest).read_bytes()


@pytest.mark.parametrize("classification", ["invalid_setup", "invalid_evaluator", "invalid_agent", "invalid_protocol"])
def test_nonretryable_invalid_continues_after_verified_recovery(
    tmp_path: Path, monkeypatch, classification: str,
) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0]["invalidReason"] = classification
    records[0]["error"] = {"type": "EpisodeFailure"}
    if classification == "invalid_evaluator":
        records[0]["officialReward"] = None
    assert campaign.run_campaign(args) == 1
    assert launched == [(index, 1) for index in range(12)]
    summary = json.loads((output / "summary.json").read_text())
    assert summary["episodes"][0]["classification"] == classification
    assert summary["episodes"][0]["officialReward"] == records[0]["officialReward"]
    assert summary["coverageAudit"]["valid"] is True
    assert summary["qualified"] is False
    recovery = json.loads(next(path for path in (output / "recoveries").glob("*.json") if not path.name.endswith("-before.json")).read_text())
    assert recovery["originalClassification"] == classification
    assert recovery["originalCleanup"] == records[0]["cleanup"]
    assert recovery["continuationAllowed"] is True


def test_harness_reclaim_permits_coverage_but_never_repairs_agent_cleanup(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0]["agent"]["normalized"]["toolCalls"][0].pop("sessionCleanup")
    records[0]["appiumSessionAudit"].update({"deletedSessionCount": 0, "deletedSessionHashes": []})
    records[0]["cleanup"]["agentSession"] = {
        "status": "harness_reclaimed", "attribution": "harness", "verificationStatus": "absent",
        "pendingRequestCount": 0, "unknownCreationOutcomeCount": 0, "activeSessionCount": 0,
        "sessions": [{"quitReturned": True, "absentVerified": True, "sessionHash": "b" * 64}],
    }
    assert campaign.run_campaign(args) == 1
    assert launched == [(index, 1) for index in range(12)]
    summary = json.loads((output / "summary.json").read_text())
    assert summary["cleanupFailureCount"] == 1
    assert summary["coverageAudit"]["valid"] is True
    assert summary["episodes"][0]["classification"] == "passed"
    assert summary["episodes"][0]["officialReward"] == 1.0
    assert summary["qualified"] is False


@pytest.mark.parametrize("unsafe", ["unknown_cleanup", "idle_timeout", "failed_teardown", "failed_environment", "unavailable", "sessions", "services", "identity"])
def test_unsafe_recovery_pauses_with_explicit_unstarted_tasks(tmp_path: Path, monkeypatch, unsafe: str) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0]["invalidReason"] = "invalid_agent"
    records[0]["error"] = {"type": "EpisodeFailure"}
    if unsafe in {"unknown_cleanup", "idle_timeout"}:
        records[0]["cleanup"]["agentSession"]["status"] = "unknown" if unsafe == "unknown_cleanup" else "idle_timeout"
    elif unsafe == "failed_teardown":
        records[0]["cleanup"]["taskTearDown"] = "failed:RuntimeError"
    elif unsafe == "failed_environment":
        records[0]["cleanup"]["environment"] = "unknown"
    elif unsafe == "identity":
        original_load = campaign._load_manifest
        loads = []

        def load(*args):
            loads.append(True)
            if len(loads) > 1:
                raise ValueError("frozen Runtime identity drift")
            return original_load(*args)

        monkeypatch.setattr(campaign, "_load_manifest", load)
    elif unsafe == "unavailable":
        calls = []

        def attest(*_args):
            calls.append(True)
            if len(calls) > 1:
                raise ConnectionError("device unavailable")
            return _fixture_attestation()

        monkeypatch.setattr(campaign, "attest_device", attest)
    elif unsafe == "sessions":
        monkeypatch.setattr(campaign, "_appium_session_hashes", lambda *_args: ["unowned-session"])
    else:
        health_calls = []

        def health(*_args):
            health_calls.append(True)
            return _fixture_core_services() if len(health_calls) == 1 else {"qualified": False}

        monkeypatch.setattr(campaign, "_core_service_health", health)
    assert campaign.run_campaign(args) == 2
    assert launched == [(0, 1)]
    summary = json.loads((output / "summary.json").read_text())
    assert summary["paused"] is True
    assert summary["unstartedTaskIndexes"] == list(range(1, 12))
    assert summary["actualStartedEpisodeCount"] == 1
    assert summary["pauseReason"]
    assert len(summary["recoveryReferences"]) == 1
    assert summary["recoveryReferences"][0]["continuationAllowed"] is False
    assert summary["qualified"] is False
    assert not (output / "episodes" / campaign._episode_slug(_manifest["tasks"][1])).exists()


def test_preagent_infrastructure_retry_is_bounded_and_preserves_both_attempts(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0].update({
        "agent": None, "invalidReason": "invalid_infrastructure", "officialReward": None,
        "error": {"type": "InfrastructureError"},
        "cleanup": {"agentSession": {"status": "not_created"},
                    "taskTearDown": "not_applicable", "environment": "not_created"},
    })
    assert campaign.run_campaign(args) == 1
    assert launched[:3] == [(0, 1), (0, 2), (1, 1)]
    assert len(launched) == 13
    summary = json.loads((output / "summary.json").read_text())
    assert summary["actualAttemptStartCount"] == 13
    assert summary["episodes"][0]["attempts"] == 2
    assert summary["coverageAudit"]["nullRewardCount"] == 2
    assert summary["coverageAudit"]["valid"] is True
    assert len(list((output / "recoveries").glob("*.json"))) == 4


@pytest.mark.parametrize("previous", ["checkpoint.jsonl", "run-metadata.json", "summary.json", "attempt", "attempt_without_result"])
def test_r12_rejects_prior_execution_without_launching(tmp_path: Path, monkeypatch, previous: str) -> None:
    from fsq_androidworld_eval import campaign

    args, manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    output.mkdir()
    if previous.startswith("attempt"):
        attempt = output / "episodes" / campaign._episode_slug(manifest["tasks"][0]) / "attempt-1"
        attempt.mkdir(parents=True)
        if previous == "attempt":
            (attempt / "result.json").write_text(json.dumps(records[0]))
    else:
        (output / previous).write_text("{}")
    with pytest.raises(ValueError, match="cannot resume"):
        campaign.run_campaign(args)
    assert launched == []


def test_initial_environment_unavailable_records_pause_without_any_start(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, _records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)

    def unavailable(*_args):
        raise ConnectionError("target unavailable")

    monkeypatch.setattr(campaign, "attest_device", unavailable)
    assert campaign.run_campaign(args) == 2
    assert launched == []
    summary = json.loads((output / "summary.json").read_text())
    assert summary["unstartedTaskIndexes"] == list(range(12))
    assert summary["actualAttemptStartCount"] == 0
    assert summary["pauseReason"] == "initial_readiness_unavailable_requires_coordinated_recovery"


@pytest.mark.parametrize("mutation", ["task", "protocol", "termination_policy", "scoring_policy"])
def test_manifest_rejects_changed_time_or_outcome_policy(tmp_path: Path, mutation: str) -> None:
    manifest = json.loads(json.dumps(build_manifest("changed-time-policy")))
    if mutation == "task":
        manifest["tasks"][0]["timeBudget"]["episodeSeconds"] += 1
    elif mutation == "protocol":
        manifest["protocol"]["timeBudget"]["cleanupWindowSeconds"] -= 1
    elif mutation == "termination_policy":
        manifest["protocol"]["terminationPolicy"]["unknown_termination"] = "evaluated_attempt"
    else:
        manifest["protocol"]["scoringPolicy"]["missingEvaluator"] = "zero"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))

    with pytest.raises(ValueError):
        _load_manifest(path)


@pytest.mark.parametrize("kind", ["rehearsal", "calibration", "full"])
def test_inherited_manifest_validates_without_generating_suite_parameters(tmp_path: Path, monkeypatch, kind: str) -> None:
    from fsq_androidworld_eval import campaign

    def forbidden_generation(*_args, **_kwargs):
        raise AssertionError("inherited manifests must never generate suite parameters")

    monkeypatch.setattr(campaign.suite_utils, "create_suite", forbidden_generation)
    gate = {"campaignId": "new-calibration", "manifestSha256": "1" * 64,
            "summaryIdentitySha256": "2" * 64, "evidenceSha256": "3" * 64}
    monkeypatch.setattr(campaign, "_calibration_gate", lambda *_args: gate)
    manifest = build_manifest(
        "new-r12-" + kind, kind=kind,
        calibration_campaign_dir=tmp_path / "calibration" if kind == "full" else None,
        inherit_manifest=FROZEN_SOURCE,
    )
    source = json.loads(FROZEN_SOURCE.read_text())
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    assert _load_manifest(path) == manifest
    assert manifest["protocol"]["campaignContinuation"] == CAMPAIGN_CONTINUATION
    assert manifest["inheritedManifest"]["tasksSha256"] == INHERITED_TASKS_SHA256
    if kind == "calibration":
        original = {task["name"]: task for task in source["tasks"]}
        assert manifest["tasks"] == [{**original[name], "index": index}
                                     for index, name in enumerate(CALIBRATION_TASKS)]
    else:
        assert manifest["tasks"] == source["tasks"]
        assert len(manifest["tasks"]) == 116
    for key in ("model", "timeBudget", "stepBudget", "scoringPolicy", "terminationPolicy"):
        assert manifest["protocol"][key] == source["protocol"][key]


def test_inherited_source_hash_checked_before_output_mutation(tmp_path: Path) -> None:
    from fsq_androidworld_eval import campaign

    changed = tmp_path / "changed-source.json"
    changed.write_bytes(FROZEN_SOURCE.read_bytes() + b"\n")
    output = tmp_path / "not-created" / "manifest.json"
    with pytest.raises(ValueError, match="file digest mismatch"):
        campaign.write_manifest(output, "new-r12", kind="rehearsal", inherit_manifest=changed)
    assert not output.parent.exists()


@pytest.mark.parametrize("mutation", ["task", "provenance", "model", "continuation"])
def test_inherited_manifest_rejects_any_frozen_spec_or_policy_drift(tmp_path: Path, mutation: str) -> None:
    manifest = build_manifest("new-r12", kind="rehearsal", inherit_manifest=FROZEN_SOURCE)
    if mutation == "task":
        manifest["tasks"][0]["tags"] = ["changed"]
    elif mutation == "provenance":
        manifest["inheritedManifest"]["tasksSha256"] = "f" * 64
    elif mutation == "model":
        manifest["protocol"]["model"] = "github-copilot/different-model"
    else:
        manifest["protocol"].pop("campaignContinuation")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        _load_manifest(path)


@pytest.mark.parametrize("field", ["ompVersion", "ompExecutableSha256", "amkernelExecutableSha256", "harnessDependencies", "installedAgentAssetsSha256"])
def test_inherited_manifest_rejects_frozen_runtime_drift(monkeypatch, field: str) -> None:
    from fsq_androidworld_eval import campaign

    runtime = campaign._runtime_identity(Path.cwd())
    runtime[field] = [] if field == "harnessDependencies" else "changed"
    monkeypatch.setattr(campaign, "_runtime_identity", lambda *_args: runtime)
    with pytest.raises(ValueError, match="frozen runtime mismatch"):
        build_manifest("new-r12", kind="rehearsal", inherit_manifest=FROZEN_SOURCE)


def test_original_r11_manifest_is_rejected_without_upgrade() -> None:
    with pytest.raises(ValueError, match="protocol mismatch"):
        _load_manifest(FROZEN_SOURCE)


def test_prepare_cli_exposes_inherited_source_without_resume_option() -> None:
    from fsq_androidworld_eval import campaign

    args = campaign.build_parser().parse_args([
        "prepare", "--kind", "rehearsal", "--campaign-id", "new-r12",
        "--output", "new/manifest.json", "--inherit-manifest", str(FROZEN_SOURCE),
    ])
    assert args.inherit_manifest == str(FROZEN_SOURCE)
    assert args.kind == "rehearsal"


def test_failed_evaluated_task_continues_after_fresh_attestation(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0]["officialReward"] = 0.0
    attestations = []

    def attest(*_args):
        attestations.append(True)
        return _fixture_attestation()

    monkeypatch.setattr(campaign, "attest_device", attest)
    assert campaign.run_campaign(args) == 0
    assert launched == [(index, 1) for index in range(12)]
    assert len(attestations) == 2
    summary = json.loads((output / "summary.json").read_text())
    assert summary["episodes"][0]["classification"] == "failed"
    assert summary["episodes"][0]["officialReward"] == 0.0
    assert len(summary["recoveryReferences"]) == 1
    assert summary["coverageAudit"]["valid"] is True


def test_core_service_probe_rejects_not_found_without_restart(monkeypatch) -> None:
    from fsq_androidworld_eval import campaign
    import grpc

    commands = []

    def run(command, **_kwargs):
        commands.append(command)
        if command[-1] == "get-state":
            value = "device"
        elif command[-1] == "sys.boot_completed":
            value = "1"
        elif command[-1] in {"system_server", "surfaceflinger"}:
            value = "333"
        elif command[-1] == "/proc/sys/kernel/random/boot_id":
            value = "0f36e370-012a-4423-a1f9-959beae8f90d"
        else:
            value = f"Service {command[-1]}: not found"
        return SimpleNamespace(stdout=value)

    class ReadyChannel:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

    monkeypatch.setattr(campaign.subprocess, "run", run)
    monkeypatch.setattr(campaign, "_request_json", lambda *_args: {"value": {"ready": True}})
    monkeypatch.setattr(grpc, "secure_channel", lambda *_args: ReadyChannel())
    monkeypatch.setattr(grpc, "channel_ready_future", lambda *_args: SimpleNamespace(result=lambda **_kwargs: None))
    from android_env.proto import emulator_controller_pb2_grpc
    monkeypatch.setattr(emulator_controller_pb2_grpc, "EmulatorControllerStub", lambda *_args: SimpleNamespace(
        getStatus=lambda *_args, **_kwargs: SimpleNamespace(booted=True)
    ))
    health = campaign._core_service_health({"target": {
        "serial": "fixture", "appiumUrl": "http://fixture", "grpcPort": 8554,
    }}, "/fake/adb")
    assert health["qualified"] is False
    assert health["activityService"] is False
    assert health["packageService"] is False
    assert len(commands) == 9
    assert all(command[0] == "/fake/adb" for command in commands)


def test_environment_mode_evidence_is_bound_and_rechecked(tmp_path: Path) -> None:
    mode_path = tmp_path / "environment-mode.json"
    mode = {"avd": "AndroidWorldAvd", "serial": "emulator-5554", "headless": True,
            "vulkan": "lavapipe", "gles": "swangle"}
    mode_path.write_text(json.dumps(mode))
    manifest = build_manifest("new-r12-headless", kind="rehearsal", inherit_manifest=FROZEN_SOURCE,
                              environment_mode_report=mode_path)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    assert _load_manifest(path) == manifest
    assert manifest["target"]["environmentMode"]["evidence"] == mode
    mode_path.write_text(json.dumps({**mode, "headless": False}))
    with pytest.raises(ValueError, match="environment mode evidence digest"):
        _load_manifest(path)


def test_readiness_cannot_omit_bound_environment_mode(tmp_path: Path) -> None:
    manifest = build_manifest("new-r12-mode", inherit_manifest=FROZEN_SOURCE)
    manifest["target"]["environmentMode"] = {"evidence": {"headless": True}, "sha256": "a" * 64}
    readiness = _fixture_readiness(manifest)
    readiness["target"] = {key: value for key, value in manifest["target"].items() if key != "environmentMode"}
    readiness.pop("identitySha256")
    readiness["identitySha256"] = _sha256(readiness)
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(readiness))
    with pytest.raises(ValueError, match="target/environment mode identity"):
        _readiness_identity(path, manifest)


@pytest.mark.parametrize("failure", ["missing", "malformed", "launch_exception"])
def test_runner_failure_retains_terminal_and_pauses_without_next_launch(tmp_path: Path, monkeypatch, failure: str) -> None:
    from fsq_androidworld_eval import campaign

    actual_attempt = campaign._run_attempt
    args, _manifest, _records, _launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(campaign, "_run_attempt", actual_attempt)
    processes = []

    def process(command, _timeout):
        events = [json.loads(line) for line in (output / "checkpoint.jsonl").read_text().splitlines()]
        assert events[-1]["event"] == "attempt_started"
        processes.append(command)
        if failure == "launch_exception":
            raise OSError("runner launch unavailable")
        if failure == "malformed":
            attempt_dir = Path(command[command.index("--output-dir") + 1])
            attempt_dir.mkdir()
            (attempt_dir / "result.json").write_text("{not-json")
        return 124

    monkeypatch.setattr(campaign, "_run_process", process)
    assert campaign.run_campaign(args) == 2
    assert len(processes) == 1
    events = [json.loads(line) for line in (output / "checkpoint.jsonl").read_text().splitlines()]
    assert [event["event"] for event in events] == ["attempt_started", "attempt_terminal", "recovery_before", "recovery", "pause"]
    assert events[1]["classification"] == "invalid_agent"
    assert events[1]["officialReward"] is None
    result = json.loads((output / events[1]["result"]).read_text())
    assert result["cleanup"]["agentSession"]["status"] == "unknown"
    assert result["recordSource"] == "campaign_missing_runner_result"
    if failure == "malformed":
        assert Path(result["preservedRunnerResult"]).read_text() == "{not-json"


def test_retryable_classification_after_agent_start_is_never_replayed(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0]["invalidReason"] = "invalid_infrastructure"
    records[0]["error"] = {"type": "InfrastructureError"}
    assert campaign.run_campaign(args) == 1
    assert launched == [(index, 1) for index in range(12)]
    assert json.loads((output / "summary.json").read_text())["episodes"][0]["attempts"] == 1


def test_initial_core_services_unusable_pauses_before_first_task(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, _records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(campaign, "_core_service_health", lambda *_args: {"qualified": False})
    assert campaign.run_campaign(args) == 2
    assert launched == []
    summary = json.loads((output / "summary.json").read_text())
    assert summary["unstartedTaskIndexes"] == list(range(12))
    assert summary["pauseReason"] == "initial_core_services_unavailable_requires_coordinated_recovery"


def test_recovery_retains_observed_boot_and_framework_pid_boundaries(tmp_path: Path, monkeypatch) -> None:
    from fsq_androidworld_eval import campaign

    args, _manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0]["invalidReason"] = "invalid_agent"
    records[0]["error"] = {"type": "AgentTerminated"}
    calls = []

    def health(*_args):
        calls.append(True)
        observed = _fixture_core_services()
        if len(calls) > 1:
            observed.update({"bootId": "833a7303-e95a-46d5-95b3-7d52c63bc526",
                             "systemServerPids": ["444"], "surfaceFlingerPids": ["600"]})
        return observed

    monkeypatch.setattr(campaign, "_core_service_health", health)
    assert campaign.run_campaign(args) == 1
    assert launched == [(index, 1) for index in range(12)]
    metadata = json.loads((output / "run-metadata.json").read_text())
    recovery = json.loads(next(path for path in (output / "recoveries").glob("*.json") if not path.name.endswith("-before.json")).read_text())
    assert metadata["initialCoreServices"]["bootId"] == _fixture_core_services()["bootId"]
    assert recovery["coreServices"]["bootId"] == "833a7303-e95a-46d5-95b3-7d52c63bc526"
    assert recovery["coreServices"]["systemServerPids"] == ["444"]
    assert recovery["coreServices"]["surfaceFlingerPids"] == ["600"]
    assert recovery["originalClassification"] == "invalid_agent"


@pytest.mark.parametrize("missing", [None, "onboardingCompleted", "quitReturned", "snapshotSavedAfterUi", "allFilesAuthorized"])
def test_readiness_rejects_incomplete_vlc_startup_snapshot_proof(tmp_path: Path, missing) -> None:
    manifest = {"target": {"serial": "emulator"}, "protocol": {
        "environmentArtifacts": {}, "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG},
        "tasks": [{"apps": ["vlc"]}]}
    proof = {key: True for key in ("mainActivityObserved", "quitReturned", "onboardingCompleted",
                                   "allFilesAuthorized", "snapshotSavedAfterUi")}
    if missing is not None:
        proof[missing] = False
    report = {"schemaVersion": 2, "qualified": True, "environmentClose": "closed",
              "manifestSha256": _sha256(manifest), "target": manifest["target"],
              "environmentArtifacts": {}, "adbOutputIsolated": True,
              "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
              "snapshotRestores": [{"app": "vlc", "status": "restored"}], "vlcStartup": proof}
    report["identitySha256"] = _sha256(report)
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(report))
    if missing is None:
        assert _readiness_identity(path, manifest) == report["identitySha256"]
    else:
        with pytest.raises(ValueError, match="VLC first-launch"):
            _readiness_identity(path, manifest)


@pytest.mark.parametrize("failure", [None, "setup", "close", "still_drifted", "unknown_cleanup", "services", "identity", "extra_drift", "sessions", "bootId", "systemServerPids", "surfaceFlingerPids"])
def test_timezone_recovery_preserves_terminal_and_requires_fresh_safety(tmp_path: Path, monkeypatch, failure) -> None:
    from android_world.utils import datetime_utils
    from fsq_androidworld_eval import campaign, environment

    args, manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    records[0]["officialReward"] = 0.0
    records[0]["cleanup"]["agentSession"].pop("verificationStatus", None)
    if failure == "unknown_cleanup":
        records[0]["cleanup"]["agentSession"]["status"] = "unknown"
    state = {"attests": 0, "restored": False}
    actions = []
    before_bytes = []
    terminal_bytes = []
    owner = SimpleNamespace(controller=SimpleNamespace(timezone="Asia/Shanghai"))

    def attest(*_args):
        state["attests"] += 1
        report = _fixture_attestation()
        if state["attests"] > 1 and (not state["restored"] or failure == "still_drifted"):
            report["qualified"] = False
            report["mismatches"] = {"timezone": {"expected": "UTC", "observed": "Asia/Shanghai"}}
            if failure == "extra_drift":
                report["mismatches"]["abi"] = {"expected": "arm64-v8a", "observed": "other"}
        return report

    def load(**kwargs):
        assert kwargs["freeze_datetime"] is False
        events = [json.loads(line) for line in (output / "checkpoint.jsonl").read_text().splitlines()]
        assert events[-1]["event"] == "recovery_before"
        path = output / events[-1]["evidence"]
        assert campaign._file_sha256(path) == events[-1]["evidenceSha256"]
        before_bytes.append((path, path.read_bytes()))
        terminal = output / events[-2]["result"]
        terminal_bytes.append((terminal, terminal.read_bytes()))
        actions.append("load")
        return owner

    def setup(env):
        actions.append("setup_datetime")
        if failure == "setup":
            raise RuntimeError("official datetime setup failed")
        env.timezone = "UTC"
        state["restored"] = owner.controller.timezone == "UTC"

    def close(env):
        assert env is owner
        actions.append("close")
        if failure == "close":
            raise RuntimeError("controller close failed")

    monkeypatch.setattr(campaign, "attest_device", attest)
    monkeypatch.setattr(environment, "load_environment", load)
    monkeypatch.setattr(environment, "close_environment", close)
    monkeypatch.setattr(datetime_utils, "setup_datetime", setup)
    if failure == "sessions":
        monkeypatch.setattr(campaign, "_appium_session_hashes", lambda *_args: ["unowned"])
    if failure == "services":
        monkeypatch.setattr(campaign, "_core_service_health", lambda *_args: _fixture_core_services() if not launched else {"qualified": False})
    if failure in {"bootId", "systemServerPids", "surfaceFlingerPids"}:
        def core_services(*_args):
            report = _fixture_core_services()
            if state["restored"]:
                report[failure] = "changed-boot" if failure == "bootId" else ["999"]
            return report
        monkeypatch.setattr(campaign, "_core_service_health", core_services)
    if failure == "identity":
        original = campaign._load_manifest
        def identity(*arguments):
            if launched:
                raise ValueError("global identity changed")
            return original(*arguments)
        monkeypatch.setattr(campaign, "_load_manifest", identity)
    assert campaign.run_campaign(args) == (1 if failure is None else 2)
    assert launched == ([(index, 1) for index in range(12)] if failure is None else [(0, 1)])
    final = json.loads((output / "recoveries" / f"{campaign._episode_slug(manifest['tasks'][0])}-attempt-1.json").read_text())
    before = output / final["beforeEvidence"]["path"]
    assert campaign._file_sha256(before) == final["beforeEvidence"]["sha256"]
    assert final["attestationBefore"]["mismatches"]["timezone"]["observed"] == "Asia/Shanghai"
    assert final["continuationAllowed"] is (failure is None)
    if failure in {"unknown_cleanup", "services", "identity", "extra_drift", "sessions"}:
        assert actions == []
        assert "remediation" not in final
    else:
        assert actions == ["load", "setup_datetime", "close"]
        assert state["attests"] >= 3
        assert final["remediation"]["outcome"] == ("failed" if failure in {"setup", "close"} else "completed")
        for path, original_bytes in before_bytes + terminal_bytes:
            assert path.read_bytes() == original_bytes
    result = json.loads((output / final["result"]).read_text())
    assert result["officialReward"] == 0.0
    assert result["cleanup"] == records[0]["cleanup"]


@pytest.mark.parametrize("unsafe", [None, "process", "pending", "unknown_creation"])
def test_agent_failure_without_created_session_continues_only_after_proven_exit_and_idle(tmp_path, monkeypatch, unsafe):
    from fsq_androidworld_eval import campaign
    args, manifest, records, launched, output = _scheduler_fixture(tmp_path, monkeypatch)
    record = records[0]
    record["invalidReason"] = "invalid_agent"
    record["officialReward"] = None
    record["agent"].update({"processExited": unsafe != "process", "exitCode": 1, "agentCompleted": False})
    record["cleanup"]["agentSession"] = {"status": "not_created", "attribution": "none", "verificationStatus": "absent"}
    audit = {key: 0 for key in ("createdSessionCount", "deletedSessionCount", "activeSessionCount",
                                "pendingRequestCount", "pendingCreateCount", "unknownCreationOutcomeCount")}
    audit.update({"errors": [], "createdSessionHashes": [], "deletedSessionHashes": []})
    if unsafe == "pending":
        audit["pendingRequestCount"] = 1
    elif unsafe == "unknown_creation":
        audit["unknownCreationOutcomeCount"] = 1
    record["appiumSessionAudit"] = audit
    code = campaign.run_campaign(args)
    summary = json.loads((output / "summary.json").read_text())
    assert summary["episodes"][0]["officialReward"] is None
    assert summary["episodes"][0]["classification"] == "invalid_agent"
    if unsafe is None:
        assert code == 1
        assert launched == [(index, 1) for index in range(12)]
    else:
        assert code == 2
        assert launched == [(0, 1)]
