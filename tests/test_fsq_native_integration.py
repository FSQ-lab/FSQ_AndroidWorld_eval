"""Optional real FSQ consumer checks; run with the reviewed FSQ interpreter.

Only backend transport and the unused AI-assertion collaborator are replaced.
No device, provider, credentials, installation or model is required.
"""
import asyncio
import json
from types import SimpleNamespace
from xml.etree import ElementTree

import pytest

pytest.importorskip("fsq_agent")
from uiautomator2._selector import Selector, UiObject

from fsq_agent.adapters.coding_agent._harness_tools import HarnessToolAdapter
from fsq_agent.agent_engine import ToolCall
from fsq_agent.config import Settings
from fsq_agent.core import EvidenceRecorder, RuntimeSecretStore
from fsq_agent.drivers.android._uiautomator2 import UiAutomator2AndroidDriver

from fsq_androidworld_eval.fsq_native import NativeDispatchBudget, build_native_harness_factory


class OfflineControl:
    """The installed SDK's actual selector over one offline JSON-RPC control."""
    wait_timeout = 0.001

    def __init__(self, text):
        self.text = text
        self.jsonrpc = self
        self.writes = []
        self.info = {"displayWidth": 1080, "displayHeight": 1920}

    def __call__(self, **query):
        return UiObject(self, Selector(**query))

    def count(self, selector):
        return int(selector.get("resourceId") == "fixture.editor")

    def objInfo(self, selector):
        assert self.count(selector) == 1
        return {"text": self.text, "resourceId": "fixture.editor", "className": "android.widget.EditText",
                "packageName": "fixture.app", "enabled": True, "password": False,
                "bounds": {"left": 0, "top": 0, "right": 200, "bottom": 100}}

    def getText(self, selector):
        assert self.count(selector) == 1
        return self.text

    def shell(self, command):
        if command == ["am", "get-current-user"]:
            return SimpleNamespace(exit_code=0, output="0\n")
        if command[:3] == ["cmd", "package", "query-activities"]:
            return SimpleNamespace(exit_code=0, output="fixture.app/.Main\n")
        if command[:2] == ["am", "start"]:
            component = command[command.index("-n") + 1]
            self.writes.append(("launch", component.split("/", 1)[0]))
            return SimpleNamespace(exit_code=0, output="Status: ok\n")
        raise AssertionError(f"Unexpected offline shell command: {command!r}")

    def app_current(self):
        return {"package": "fixture.app", "activity": ".Main"}

    def app_list_running(self):
        return ["fixture.app"]

    def screenshot(self, *, format):
        from PIL import Image
        return Image.new("RGB", (2, 2))

    def dump_hierarchy(self):
        root = ElementTree.Element("hierarchy")
        ElementTree.SubElement(root, "node", {"text": self.text, "resource-id": "fixture.editor",
            "class": "android.widget.EditText", "bounds": "[0,0][200,100]", "enabled": "true"})
        return ElementTree.tostring(root, encoding="unicode")


def recorded_output(step):
    return next(phase["metadata"]["harness_output"] for phase in step["phase_reports"] if phase["phase"] == "invoke")


@pytest.mark.parametrize("wait_for", ["foreground", "running"])
def test_real_factory_budget_wrapper_preserves_safe_pagination_and_durable_consumers(tmp_path, monkeypatch, wait_for):
    import fsq_agent.ai_services

    # No AI assertion is used: do not even construct a provider session.
    monkeypatch.setattr(fsq_agent.ai_services, "build_ai_assertion_evaluator", lambda _: None)
    core_secret, sink_secret = 'canary-"证\\x', "sink-only-782"
    raw = json.dumps({"note": f"起😀 {core_secret} {sink_secret} 尾"}, ensure_ascii=True)
    expected = json.dumps({"note": "起😀 *** *** 尾"}, ensure_ascii=False)
    device = OfflineControl(raw)
    connections = []
    def connect(self, serial):
        connections.append(serial)
        return device
    monkeypatch.setattr(UiAutomator2AndroidDriver, "_connect", connect)
    settings = Settings()
    settings.harness.platform = "android"
    settings.harness.android.app_id = "fixture.app"
    settings.harness.android.serial = "offline-only"
    settings.output.runs_dir = tmp_path / "runs"
    settings.runtime_secrets.set_values({"CANARY": core_secret})
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1, journal=tmp_path / "dispatch.jsonl")
    harness = build_native_harness_factory(settings, budget)("budget-bridge")
    assert connections == []  # Real factory/schema admission is lazy.
    recorder = EvidenceRecorder(run_id="budget-bridge", output_dir=tmp_path / "evidence", secret_values=(sink_secret,))
    adapter = HarnessToolAdapter(harness, run_id="budget-bridge",
        runtime_secret_store=RuntimeSecretStore.from_settings(settings.runtime_secrets), evidence_sink=recorder)
    tools = {binding.name: binding for binding in adapter.build_tools()}

    async def invoke(name, params, call_id):
        response = json.loads(await tools[name].invoke(ToolCall(name, params, call_id)))
        assert response["status"] == "passed", response
        return response["result"]["output"]

    pieces = []
    try:
        for offset in range(0, len(expected), 2):
            output = asyncio.run(invoke("read_element", {"locator": {"resourceId": "fixture.editor"},
                "offset": offset, "max_chars": 2}, f"read-{offset}"))
            step_id = adapter.runner.last_step_result.step_id
            events_path = recorder.output_dir / "evidence-events.jsonl"
            events = [json.loads(line) for line in events_path.read_text().splitlines()]
            journal_event = next(row["event"]["payload"]["phase_report"]["metadata"]["harness_output"]
                for row in events if row.get("event") and row["event"]["step_id"] == step_id
                and row["event"]["event_type"] == "phase_finish" and row["event"]["phase"] == "invoke")
            journal_step = next(row["step_result"] for row in events if row.get("step_result") and row["step_result"]["step_id"] == step_id)
            manifest = json.loads((recorder.output_dir / "evidence-manifest.json").read_text())
            recovered = EvidenceRecorder.recover_bundle(recorder.output_dir)
            channels = [output, adapter.runner.last_capability_execution_result.output, journal_event,
                recorded_output(journal_step),
                recorded_output(next(item for item in manifest["steps"] if item["step_id"] == step_id)),
                recorded_output(next(item.model_dump(mode="json") for item in recorder.build_bundle().steps if item.step_id == step_id)),
                recorded_output(next(item.model_dump(mode="json") for item in recovered.steps if item.step_id == step_id))]
            for channel in channels:
                assert channel["text"] == expected[offset:offset + 2]
                assert channel["length"] == len(channel["text"])
                assert channel["total_chars"] == len(expected)
                assert channel["has_more_after"] is (offset + channel["length"] < len(expected))
                assert channel["text_complete"] is (offset == 0 and channel["length"] == len(expected))
            pieces.append(output["text"])
        assert "".join(pieces) == expected
        assert device.text == raw and device.writes == []
        assert budget.snapshot()["admitted"] == budget.snapshot()["attempted"] == 0
        # All available write budget remains: the real new schema crosses the
        # same factory/wrapper/Core boundary and consumes exactly one unit.
        output = asyncio.run(invoke("launch_app", {"wait_for": wait_for, "timeout_ms": 0}, "launch"))
        assert output["wait_for"] == wait_for and output["readiness"] == "ready"
        assert device.writes == [("launch", "fixture.app")]
        receipt = budget.snapshot()
        assert (receipt["admitted"], receipt["succeeded"], receipt["inFlight"]) == (1, 1, 0)
        assert connections == ["offline-only"]
    finally:
        harness.close()
    assert device.writes == [("launch", "fixture.app")]
    assert budget.snapshot()["events"][-1]["event"] == "close_succeeded"
    for path in recorder.output_dir.iterdir():
        if path.is_file():
            persisted = path.read_text()
            assert core_secret not in persisted and sink_secret not in persisted
