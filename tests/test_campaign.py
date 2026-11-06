import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import sys

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
from fsq_androidworld_eval.runner import _sha256, _task
from fsq_androidworld_eval.lifecycle import TIME_BUDGET_PROTOCOL, episode_time_budget

def _qualified_calibration_campaign(root: Path) -> Path:
    root.mkdir(parents=True)
    manifest = build_manifest("calibration-proof")
    (root / "manifest.json").write_text(json.dumps(manifest))
    for task in manifest["tasks"]:
        result_path = (
            root
            / "episodes"
            / f"{task['index']:03d}-{task['name']}"
            / "attempt-1"
            / "result.json"
        )
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 3,
                    "androidWorld": {"revision": manifest["protocol"]["androidWorldRevision"]},
                    "amkernel": {
                        "version": manifest["protocol"]["runtimeIdentity"]["amkernelVersion"],
                        "tool": "python_exec",
                    },
                    "target": {"serial": manifest["target"]["serial"]},
                    "task": {
                        "name": task["name"],
                        "paramsSha256": task["paramsSha256"],
                        "complexity": task["complexity"],
                    },
                    "protocol": {
                        "harnessRevision": manifest["protocol"]["harnessRevision"],
                        "promptTemplateSha256": manifest["protocol"]["promptTemplateSha256"],
                        "mcpRequestTimeoutMs": manifest["protocol"]["mcpRequestTimeoutMs"],
                        "sessionCreationTimeoutSeconds": manifest["protocol"]["sessionCreationTimeoutSeconds"],
                        "timeBudget": manifest["protocol"]["timeBudget"],
                    },
                    "timeBudget": task["timeBudget"],
                    "agent": {
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
                    "appiumSessionAudit": {
                        "createdSessionCount": 1,
                        "createdSessionHashes": ["b" * 64],
                        "deletedSessionCount": 1,
                        "deletedSessionHashes": ["b" * 64],
                        "errors": [],
                    },
                    "budget": {"pythonExecCalls": 1, "exceededAdvisory": False},
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
                        },
                        "taskTearDown": "completed",
                        "environment": "closed",
                    },
                }
            )
        )
    _write_summary(root, manifest)
    return root


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


def test_readiness_identity_binds_report_to_manifest(tmp_path: Path) -> None:
    manifest = build_manifest("readiness-campaign")
    report = {
        "schemaVersion": 1,
        "campaignId": manifest["campaignId"],
        "manifestSha256": _sha256(manifest),
        "qualified": True,
        "environmentClose": "closed",
    }
    report["identitySha256"] = _sha256(report)
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(report))

    assert _readiness_identity(path, manifest) == report["identitySha256"]


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


@pytest.mark.parametrize("max_steps,business", [(1, 600), (8, 600), (9, 660), (20, 1320)])
def test_runner_invocation_uses_frozen_per_task_time_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, max_steps: int, business: int
) -> None:
    from fsq_androidworld_eval import campaign

    manifest = build_manifest("time-envelope")
    task = {
        **manifest["tasks"][0], "maxSteps": max_steps,
        "timeBudget": episode_time_budget(max_steps),
    }
    captured = {}

    def fake_run(command: list[str], timeout: int) -> int:
        captured.update(command=command, timeout=timeout)
        return 0

    monkeypatch.setattr(campaign, "_run_process", fake_run)
    result = campaign._run_attempt(
        manifest, task, tmp_path / "attempt", SimpleNamespace(adb_path="/fake/adb"),
        tmp_path / "workspace", tmp_path / "readiness.json", "readiness-sha",
    )

    budget = task["timeBudget"]
    assert budget["businessSeconds"] == business
    assert budget["cleanupWindowSeconds"] == 180
    assert budget["terminationGraceSeconds"] == 10
    assert budget["forceSeconds"] == business + 190
    assert budget["recoveryWindowSeconds"] == 120
    assert budget["episodeSeconds"] == business + 610
    assert captured["timeout"] == budget["episodeSeconds"]
    command = captured["command"]
    assert command[command.index("--expected-max-steps") + 1] == str(max_steps)
    assert "--agent-timeout" not in command
    assert result["agent"]["agentCompleted"] is False
    assert result["agent"]["termination"]["reason"] == "unknown_termination"
    assert result["officialReward"] is None


@pytest.mark.parametrize("resume", [False, True])
def test_harness_reclaim_never_allows_the_next_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, resume: bool
) -> None:
    from fsq_androidworld_eval import campaign

    evidence = _qualified_calibration_campaign(tmp_path / "evidence")
    manifest = json.loads((evidence / "manifest.json").read_text())
    manifest["tasks"] = manifest["tasks"][:2]
    first_result = evidence / "episodes" / campaign._episode_slug(manifest["tasks"][0]) / "attempt-1/result.json"
    record = json.loads(first_result.read_text())
    record["cleanup"]["agentSession"]["status"] = "harness_reclaimed"
    record["cleanup"]["agentSession"]["harnessRecovery"] = {"status": "closed"}
    output = tmp_path / "campaign-run"
    source_manifest = tmp_path / "manifest.json"
    source_manifest.write_text(json.dumps(manifest))
    readiness = tmp_path / "readiness.json"
    readiness.write_text("{}")
    if resume:
        first = output / "episodes" / campaign._episode_slug(manifest["tasks"][0]) / "attempt-1/result.json"
        first.parent.mkdir(parents=True)
        first.write_text(json.dumps(record))
    launched = []

    def fake_attempt(_manifest, task, *_args):
        launched.append(task["index"])
        return record

    monkeypatch.setattr(campaign, "_load_manifest", lambda *_args: manifest)
    monkeypatch.setattr(campaign, "_readiness_identity", lambda *_args: "readiness-sha")
    monkeypatch.setattr(campaign, "attest_device", lambda *_args: {"qualified": True})
    monkeypatch.setattr(campaign, "_prepare_agent_workspace", lambda *_args: {"fileCount": 0})
    monkeypatch.setattr(campaign, "_run_attempt", fake_attempt)
    args = SimpleNamespace(
        project=str(tmp_path), manifest=str(source_manifest), output_dir=str(output),
        readiness_report=str(readiness), adb_path="/fake/adb",
    )

    assert campaign.run_campaign(args) == 2
    assert launched == ([] if resume else [0])
    summary = campaign._write_summary(output, manifest)
    assert summary["episodes"][0]["officialReward"] == 1.0
    assert summary["episodes"][0]["classification"] == "passed"
    assert summary["cleanupFailureCount"] == 1
    assert summary["qualified"] is False
    assert summary["completedEpisodeCount"] == 1
    assert not (output / "episodes" / campaign._episode_slug(manifest["tasks"][1])).exists()


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
