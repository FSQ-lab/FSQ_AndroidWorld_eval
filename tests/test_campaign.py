import json
from pathlib import Path
import subprocess
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
                    },
                    "protocol": {
                        "harnessRevision": manifest["protocol"]["harnessRevision"],
                        "promptTemplateSha256": manifest["protocol"]["promptTemplateSha256"],
                    },
                    "agent": {
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
    assert loaded["protocol"]["harnessRevision"] == 3
    assert loaded["protocol"]["scoreContract"] == "official_reward_only"
    assert [task["name"] for task in loaded["tasks"]] == CALIBRATION_TASKS
    for task_spec in loaded["tasks"]:
        regenerated = _task(
            task_spec["name"], params_json=None, task_seed=task_spec["instanceSeed"]
        )
        assert _sha256(regenerated.params) == task_spec["paramsSha256"]


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
    with pytest.raises(ValueError, match="requires qualified calibration evidence"):
        build_manifest("full-without-gate", kind="full")
    calibration_dir = _qualified_calibration_campaign(tmp_path / "calibration")
    first_result = next(calibration_dir.glob("episodes/*/attempt-1/result.json"))
    record = json.loads(first_result.read_text())
    record["agent"]["normalized"]["toolCalls"] = []
    first_result.write_text(json.dumps(record))
    calibration_manifest = json.loads((calibration_dir / "manifest.json").read_text())
    _write_summary(calibration_dir, calibration_manifest)
    with pytest.raises(ValueError, match="lacks runner provenance"):
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


def test_cleanup_distinguishes_not_created_closed_unknown_and_leaked() -> None:
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
    assert _cleanup_failed({"cleanup": {**base, "agentSession": {"status": "unknown"}}}) is True
    assert _cleanup_failed({"cleanup": {**base, "agentSession": {"status": "leaked"}}}) is True


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
            sys.executable,
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
