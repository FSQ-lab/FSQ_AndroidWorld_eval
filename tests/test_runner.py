from datetime import datetime, timezone
import hashlib
import subprocess
from urllib import error as url_error

import fsq_androidworld_eval.runner as runner
import pytest
import json
from pathlib import Path

from fsq_androidworld_eval.runner import (
    _agent_prompt,
    _agent_protocol_violations,
    _normalize_agent_events,
    _required_apps,
    _task,
)


def test_normalizes_amkernel_call_without_retaining_code(tmp_path: Path) -> None:
    events = [
        {
            "type": "tool_execution_start",
            "toolCallId": "one",
            "toolName": "write",
            "args": {
                "path": "xd://mcp__amkernel_python_exec",
                "content": json.dumps({"code": "secret_source = 42"}),
            },
        },
        {
            "type": "tool_execution_end",
            "toolCallId": "one",
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "status": "completed",
                                "kernelState": "alive",
                                "executionCount": 1,
                                "durationMs": 2,
                                "result": {
                                    "ownedSessionId": "private-session-id",
                                    "quitReturned": True,
                                },
                            }
                        ),
                    }
                ]
            },
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "model": "model-id",
                "provider": "provider-id",
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "taskOutcome": "success",
                                "sessionCleanup": {
                                    "ownedSessionId": "private-session-id"
                                },
                            }
                        ),
                    }
                ],
            },
        },
    ]
    path = tmp_path / "events.jsonl"
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")

    normalized = _normalize_agent_events(path)

    assert normalized["model"] == "model-id"
    assert normalized["toolCalls"][0]["amkernel"] == {
        "status": "completed",
        "kernelState": "alive",
        "executionCount": 1,
        "durationMs": 2,
    }
    assert normalized["toolCalls"][0]["sessionCleanup"] == {
        "quitReturned": True,
        "sessionIdSha256": "e9cac695f668f1f8ebfcabf1b002a5659ae557231252907703b8db2b204f786f",
    }
    assert "private-session-id" not in json.dumps(normalized)
    assert "secret_source" not in json.dumps(normalized)


def test_appium_session_probe_falls_back_to_uiautomator2_processes(monkeypatch) -> None:
    def request_json(url: str, *, method: str = "GET"):
        raise url_error.HTTPError(url, 404, "not found", None, None)

    from fsq_androidworld_eval import android_transport
    monkeypatch.setattr(runner, "_request_json", request_json)
    monkeypatch.setattr(android_transport, "scoped_adb_output", lambda *a, **k:
                        "PID NAME\n4312 io.appium.uiautomator2.server\n52 unrelated.process\n")

    assert runner._appium_session_hashes("http://appium", "adb", "emulator") == [
        hashlib.sha256(b"io.appium.uiautomator2.server:4312").hexdigest()
    ]



def test_appium_session_probe_rejects_malformed_entries(monkeypatch) -> None:
    monkeypatch.setattr(runner, "_request_json", lambda url: {"value": [{}, {}]})

    with pytest.raises(RuntimeError, match="missing session ID"):
        runner._appium_session_hashes("http://appium")

def test_required_apps_come_from_task_contract() -> None:
    markor = _task(
        "MarkorCreateNote",
        json.dumps({"file_name": "evaluation.md", "text": "P0 evidence"}),
    )
    system = _task("SystemWifiTurnOff", None)

    assert [app.app_name for app in _required_apps(markor)] == ["markor"]
    assert [app.app_name for app in _required_apps(system)] == ["settings"]


def test_agent_prompt_separates_goal_from_runtime_facts() -> None:
    prompt = _agent_prompt(
        "Create a note with text: exact content",
        "http://127.0.0.1:4723",
        "emulator-5554",
        max_steps=10,
        task_time_context=runner.task_time_context(datetime(2023, 10, 15, 15, 34, tzinfo=timezone.utc)),
    )

    goal = prompt.split("BEGIN EXACT TASK GOAL\n", 1)[1].split(
        "\nEND EXACT TASK GOAL", 1
    )[0]
    assert goal == "Create a note with text: exact content"
    assert "Appium server" not in goal
    assert "emulator-5554" not in goal


def test_agent_protocol_rejects_filesystem_and_unrelated_tools() -> None:
    normalized = {
        "toolCalls": [
            {"tool": "read", "target": "skill://amkernel"},
            {"tool": "write", "target": "xd://mcp__amkernel_python_exec"},
            {"tool": "write", "target": "xd://report_issue"},
            {"tool": "read", "target": "xd://report_issue_private"},
            {"tool": "read", "target": "android_world/task_evals/secret.py"},
            {"tool": "bash", "target": None},
        ]
    }

    violations = _agent_protocol_violations(normalized)

    assert violations == [
        "forbidden target: xd://report_issue_private",
        "forbidden target: android_world/task_evals/secret.py",
        "forbidden tool: bash",
    ]


@pytest.mark.parametrize(
    "target",
    [
        "skill://appium-troubleshooting",
        "skill://appium-troubleshooting/SKILL.md",
        "skill://setup-uiautomator2",
        "skill://setup-uiautomator2/SKILL.md",
        "skill://amkernel/references/android-execution.md",
    ],
)
def test_agent_protocol_allows_installed_skill_documentation(target: str) -> None:
    normalized = {"toolCalls": [{"tool": "read", "target": target}]}

    assert _agent_protocol_violations(normalized) == []


@pytest.mark.parametrize(
    "target",
    [
        "skill://appium-troubleshooting-extra",
        "skill://setup-uiautomator2-extra/SKILL.md",
        "skill://setup-xcuitest",
    ],
)
def test_agent_protocol_rejects_unselected_skill_targets(target: str) -> None:
    normalized = {"toolCalls": [{"tool": "read", "target": target}]}

    assert _agent_protocol_violations(normalized) == [f"forbidden target: {target}"]


def test_agent_protocol_cannot_write_installed_skill_documentation() -> None:
    target = "skill://appium-troubleshooting/SKILL.md"
    normalized = {"toolCalls": [{"tool": "write", "target": target}]}

    assert _agent_protocol_violations(normalized) == [f"forbidden write target: {target}"]


def test_runner_preserves_frozen_parameters_when_official_initialization_mutates_them(tmp_path, monkeypatch):
    from contextlib import nullcontext
    from types import SimpleNamespace

    class RewordingTask:
        name = "RewordingTask"
        complexity = 1
        app_names = ()
        params = {"date": "October 24 2023", "nested": {"dates": ["October 17 2023"]}}
        goal = "Read events on October 24"
        device_time = datetime(2023, 10, 15, 15, 34, tzinfo=timezone.utc)

        def initialize_task(self, env):
            self.device_time = datetime(2024, 1, 1, 23, 55, tzinfo=timezone.utc)
            self.params["date"] = "October 24"
            self.params["nested"]["dates"][0] = "Tuesday"

        def tear_down(self, env):
            pass

    task = RewordingTask()
    expected = runner._json_safe(task.params)
    expected_hash = runner._sha256(expected)
    readiness = {"qualified": True, "environmentArtifacts": {},
                 "sessionAccessibilityConfig": runner.SESSION_ACCESSIBILITY_CONFIG}
    readiness["identitySha256"] = runner._sha256(readiness)
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(readiness))
    args = runner.build_parser().parse_args([
        "--project", str(tmp_path), "--artifact-root", str(tmp_path), "--output-dir", str(tmp_path / "output"),
        "--task", task.name, "--model", "github-copilot/gpt-5.6-sol", "--expected-amkernel-version", "0.1.3",
        "--sandbox-profile", str(tmp_path / "sandbox"), "--readiness-report", str(path),
        "--expected-readiness-sha256", readiness["identitySha256"], "--expected-max-steps", "1",
        "--expected-params-sha256", expected_hash,
    ])
    monkeypatch.setattr(runner, "artifact_identity", lambda root: {})
    monkeypatch.setattr(runner, "_request_json", lambda url: {})
    monkeypatch.setattr(runner, "_appium_session_hashes", lambda *args: [])
    monkeypatch.setattr(runner, "_task", lambda *args: task)
    monkeypatch.setattr(runner, "_required_apps", lambda task: [])
    monkeypatch.setattr(runner.suite_utils, "_allocate_step_budget", lambda complexity: 1)
    monkeypatch.setattr(runner, "load_environment", lambda **kwargs: SimpleNamespace(reset=lambda **kwargs: None))
    monkeypatch.setattr(runner, "restore_shared_assets", lambda *args: [])
    monkeypatch.setattr(runner, "strict_snapshot_restores", nullcontext)
    monkeypatch.setattr(runner, "close_environment", lambda env: None)

    def stop_before_agent(*args, **kwargs):
        raise RuntimeError("Non-scoring metadata probe stops before Agent creation")

    monkeypatch.setattr(runner, "AppiumAuditProxy", stop_before_agent)
    runner.run(args)
    record = json.loads((tmp_path / "output/result.json").read_text())
    assert task.params["date"] == "October 24"
    assert record["task"]["params"] == expected
    assert runner._sha256(record["task"]["params"]) == record["task"]["paramsSha256"] == expected_hash
    assert record["task"]["timeContext"] == {
        "referenceTime": "2024-01-01T23:55:00+00:00", "timezone": "UTC",
    }
    assert record["officialReward"] is None
    assert record["agent"] is None
