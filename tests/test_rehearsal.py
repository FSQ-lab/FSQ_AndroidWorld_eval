import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from android_world import suite_utils
from android_world.task_evals.information_retrieval import information_retrieval
from android_world.task_evals.information_retrieval.proto import task_pb2

from fsq_androidworld_eval import campaign, rehearsal
from fsq_androidworld_eval.runner import _sha256
from fsq_androidworld_eval.appium_proxy import SESSION_ACCESSIBILITY_CONFIG
from fsq_androidworld_eval.runner import HARNESS_REVISION


def _spec(index: int) -> dict:
    params = {"item": f"entry-{index}"}
    return {
        "index": index, "name": f"LifecycleTask{index:03d}",
        "family": "information_retrieval" if index == 0 else "general",
        "params": params, "paramsSha256": _sha256(params),
        "paramsTransport": "json", "instanceSeed": index,
        "maxSteps": suite_utils._allocate_step_budget(1.0), "apps": [],
    }


def _manifest(count: int = 116) -> dict:
    return {
        "schemaVersion": 2, "kind": "rehearsal",
        "protocol": {
            "harnessRevision": HARNESS_REVISION,
            "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
            "runtimeIdentity": {
                "runtimeSha256": "a" * 64,
                "mediaEncoder": {"sha256": "b" * 64, "version": "fixture-encoder"},
            },
            "environmentArtifacts": {"identitySha256": "c" * 64},
            "harnessRehearsal": deepcopy(rehearsal.REHEARSAL_POLICY),
        },
        "target": {
            "serial": "emulator-5554", "consolePort": 5554,
            "grpcPort": 8554, "appiumUrl": "http://127.0.0.1:4723",
        },
        "tasks": [_spec(index) for index in range(count)],
    }


def _host_media(manifest: dict) -> dict:
    return {
        "encoder": manifest["protocol"]["runtimeIdentity"]["mediaEncoder"],
        "mp3": "encoded_and_decoded", "mp4": "encoded_and_decoded",
    }


def _qualified_record(manifest: dict, spec: dict) -> dict:
    probe = {
        "implementation": "android_world.task_eval.is_successful",
        "initialStateReturn": 0.0,
    }
    if spec["family"] == "information_retrieval":
        probe["referenceAnswerReturn"] = 1.0
    return {
        "schemaVersion": 1, "kind": "harness_rehearsal_task",
        "manifestSha256": _sha256(manifest),
        "task": {"name": spec["name"], "paramsSha256": spec["paramsSha256"]},
        "qualified": True, "agentInvoked": False, "officialReward": None,
        "error": None,
        "stages": [
            {"name": name, "status": "completed"}
            for name in rehearsal.REHEARSAL_POLICY["requiredStages"]
        ],
        "evaluatorProbe": probe,
        "cleanup": {
            "taskTearDown": "completed", "environment": "closed", "sessions": "absent",
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True) + "\n")


def _seal_report(path: Path, report: dict) -> None:
    report.pop("identitySha256", None)
    report["identitySha256"] = _sha256(report)
    _write_json(path, report)


@pytest.fixture
def evidence(tmp_path: Path, monkeypatch):
    saved = _manifest()
    root = tmp_path / "rehearsal"
    root.mkdir()
    _write_json(root / "manifest.json", saved)
    rows = []
    for spec in saved["tasks"]:
        relative = f"tasks/{spec['index']:03d}-{spec['name']}/result.json"
        path = root / relative
        path.parent.mkdir(parents=True)
        _write_json(path, _qualified_record(saved, spec))
        rows.append({
            "task": spec["name"], "result": relative, "qualified": True,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    report = {
        "schemaVersion": 1, "kind": "harness_rehearsal", "qualified": True,
        "agentInvoked": False, "officialReward": None, "error": None,
        "policy": deepcopy(rehearsal.REHEARSAL_POLICY), "hostMedia": _host_media(saved),
        "manifestSha256": _sha256(saved), "tasks": rows,
        "finalAttestation": {"qualified": True, "mismatches": []},
    }
    report_path = root / "report.json"
    _seal_report(report_path, report)
    formal = deepcopy(saved)
    formal["kind"] = "full"
    # Isolate host/runtime discovery, not report or task-evidence validation.
    monkeypatch.setattr(campaign, "_load_manifest", lambda path, project: json.loads(path.read_text()))
    return SimpleNamespace(
        root=root, path=report_path, report=report, saved=saved,
        formal=formal, project=tmp_path,
    )


@pytest.mark.parametrize("damage", [
    "partial", "duplicate", "reordered", "wrong_path", "modified_bytes", "missing_file",
    "row_name", "row_unqualified", "report_identity",
])
def test_all116_gate_rejects_partial_or_tampered_evidence_despite_qualified(evidence, damage):
    assert rehearsal.validate_report(evidence.path, evidence.formal, evidence.project) == evidence.report["identitySha256"]
    report = evidence.report
    if damage == "partial":
        report["tasks"].pop()
    elif damage == "duplicate":
        report["tasks"][-1] = deepcopy(report["tasks"][0])
    elif damage == "reordered":
        report["tasks"][0], report["tasks"][1] = report["tasks"][1], report["tasks"][0]
    elif damage == "wrong_path":
        report["tasks"][0]["result"] = "../result.json"
    elif damage == "modified_bytes":
        path = evidence.root / report["tasks"][0]["result"]
        path.write_text(path.read_text() + " ")
    elif damage == "missing_file":
        (evidence.root / report["tasks"][0]["result"]).unlink()
    elif damage == "row_name":
        report["tasks"][0]["task"] = report["tasks"][1]["task"]
    elif damage == "row_unqualified":
        report["tasks"][0]["qualified"] = False
    elif damage == "report_identity":
        report["identitySha256"] = "0" * 64
    else:
        raise AssertionError(damage)
    if damage == "report_identity":
        _write_json(evidence.path, report)
    else:
        _seal_report(evidence.path, report)
    assert report["qualified"] is True
    with pytest.raises((ValueError, FileNotFoundError)):
        rehearsal.validate_report(evidence.path, evidence.formal, evidence.project)


@pytest.mark.parametrize("damage", [
    "agent_invoked", "official_reward", "initial_bool", "initial_out_of_range",
    "reference_missing", "reference_bool", "teardown_failed", "close_failed", "session_leaked",
    "stage_missing", "stage_failed", "task_params", "manifest_identity", "task_error",
])
def test_all116_gate_rechecks_rehashed_task_lifecycle_instead_of_trusting_flags(evidence, damage):
    assert rehearsal.validate_report(evidence.path, evidence.formal, evidence.project) == evidence.report["identitySha256"]
    row = evidence.report["tasks"][0]
    result_path = evidence.root / row["result"]
    record = json.loads(result_path.read_text())
    if damage == "agent_invoked":
        record["agentInvoked"] = True
    elif damage == "official_reward":
        record["officialReward"] = 0.0
    elif damage == "initial_bool":
        record["evaluatorProbe"]["initialStateReturn"] = False
    elif damage == "initial_out_of_range":
        record["evaluatorProbe"]["initialStateReturn"] = 2.0
    elif damage == "reference_missing":
        del record["evaluatorProbe"]["referenceAnswerReturn"]
    elif damage == "reference_bool":
        record["evaluatorProbe"]["referenceAnswerReturn"] = True
    elif damage == "teardown_failed":
        record["cleanup"]["taskTearDown"] = "failed:RuntimeError"
    elif damage == "close_failed":
        record["cleanup"]["environment"] = "failed:RuntimeError"
    elif damage == "session_leaked":
        record["cleanup"]["sessions"] = "leaked"
    elif damage == "stage_missing":
        record["stages"].pop()
    elif damage == "stage_failed":
        record["stages"][0]["status"] = "failed"
    elif damage == "task_params":
        record["task"]["paramsSha256"] = "0" * 64
    elif damage == "manifest_identity":
        record["manifestSha256"] = "0" * 64
    elif damage == "task_error":
        record["error"] = {"stage": "task_initialization", "message": "restore failed"}
    else:
        raise AssertionError(damage)
    _write_json(result_path, record)
    row["sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
    _seal_report(evidence.path, evidence.report)
    assert evidence.report["qualified"] is row["qualified"] is record["qualified"] is True
    with pytest.raises(ValueError, match="lifecycle"):
        rehearsal.validate_report(evidence.path, evidence.formal, evidence.project)


@pytest.mark.parametrize("damage", [
    "agent_invoked", "official_reward", "schema", "kind", "error", "host_media",
    "policy", "final_attestation", "manifest_identity",
])
def test_all116_gate_rejects_resealed_report_contract_violations(evidence, damage):
    assert rehearsal.validate_report(evidence.path, evidence.formal, evidence.project) == evidence.report["identitySha256"]
    report = evidence.report
    if damage == "agent_invoked":
        report["agentInvoked"] = True
    elif damage == "official_reward":
        report["officialReward"] = 1.0
    elif damage == "schema":
        report["schemaVersion"] = 0
    elif damage == "kind":
        report["kind"] = "campaign"
    elif damage == "error":
        report["error"] = {"type": "RuntimeError", "message": "worker failed"}
    elif damage == "host_media":
        report["hostMedia"]["mp4"] = "not_probed"
    elif damage == "policy":
        report["policy"]["requiredTaskCount"] = 1
    elif damage == "final_attestation":
        report["finalAttestation"]["qualified"] = False
    elif damage == "manifest_identity":
        report["manifestSha256"] = "0" * 64
    else:
        raise AssertionError(damage)
    _seal_report(evidence.path, report)
    with pytest.raises(ValueError):
        rehearsal.validate_report(evidence.path, evidence.formal, evidence.project)


@pytest.mark.parametrize("change", ["protocol", "runtime", "artifacts", "target", "params"])
def test_all116_gate_cannot_authorize_changed_campaign_protocol_or_parameters(evidence, change):
    assert rehearsal.validate_report(evidence.path, evidence.formal, evidence.project) == evidence.report["identitySha256"]
    formal = evidence.formal
    if change == "protocol":
        formal["protocol"]["harnessRevision"] += 1
    elif change == "runtime":
        formal["protocol"]["runtimeIdentity"]["runtimeSha256"] = "d" * 64
    elif change == "artifacts":
        formal["protocol"]["environmentArtifacts"]["identitySha256"] = "d" * 64
    elif change == "target":
        formal["target"]["serial"] = "emulator-5556"
    elif change == "params":
        formal["tasks"][0]["params"]["item"] = "different-entry"
        formal["tasks"][0]["paramsSha256"] = _sha256(formal["tasks"][0]["params"])
    else:
        raise AssertionError(change)
    with pytest.raises(ValueError):
        rehearsal.validate_report(evidence.path, formal, evidence.project)


class _DeviceEnvironment:
    def __init__(self, owner):
        self.owner = owner
        self.interaction_cache = ""
        self.state = {}
        self.closed = False
        self.close_attempted = False
        self.task_name = None

    def reset(self, *, go_home):
        assert go_home is True
        assert not self.closed
        self.owner.events.append("reset")

    def close(self):
        self.close_attempted = True
        self.owner.events.append("close")
        if self.owner.failures.get(self.task_name) == "close":
            raise RuntimeError("controller close failed")
        self.closed = True


class _LifecycleTask:
    complexity = 1.0
    app_names = ()

    def __init__(self, name, params, owner):
        self.name = name
        self.params = params
        self.owner = owner
        self.initialized = False

    def initialize_task(self, env):
        assert not env.closed
        env.task_name = self.name
        env.state[self.name] = "partially_initialized"
        self.owner.events.append("initialize")
        if self.owner.failures.get(self.name) == "initialize":
            raise RuntimeError("snapshot initialization interrupted")
        self.initialized = True

    def is_successful(self, env):
        assert self.initialized and not env.closed
        self.owner.events.append("evaluate")
        return self.owner.initial_return

    def tear_down(self, env):
        assert not env.closed
        self.owner.events.append("teardown")
        if self.owner.failures.get(self.name) == "teardown":
            raise RuntimeError("snapshot teardown interrupted")
        env.state.pop(self.name)
        self.initialized = False


@pytest.fixture
def device(monkeypatch, tmp_path):
    manifest = _manifest()
    # These are lifecycle tasks, not stand-ins for the official IR answer checker.
    for spec in manifest["tasks"]:
        spec["family"] = "general"
    owner = SimpleNamespace(
        manifest=manifest, project=tmp_path, environments=[],
        reconstructed=[], events=[], failures={}, initial_return=0.0,
    )

    def reconstruct(name, params_json, seed):
        owner.reconstructed.append(name)
        return _LifecycleTask(name, json.loads(params_json), owner)

    def load(**kwargs):
        env = _DeviceEnvironment(owner)
        owner.environments.append(env)
        owner.events.append("create")
        return env

    monkeypatch.setattr(rehearsal, "_task", reconstruct)
    monkeypatch.setattr(rehearsal, "artifact_identity", lambda project: manifest["protocol"]["environmentArtifacts"])
    monkeypatch.setattr(rehearsal, "_appium_session_hashes", lambda *args: [])
    monkeypatch.setattr(rehearsal, "load_environment", load)
    monkeypatch.setattr(rehearsal, "close_environment", lambda env: env.close())
    return owner


def test_initialization_failure_still_tears_down_partial_state_and_closes_environment(device):
    spec = device.manifest["tasks"][0]
    device.failures[spec["name"]] = "initialize"

    record = rehearsal.run_task(device.manifest, spec, device.project, "fixture-adb")

    assert record["qualified"] is False
    assert record["agentInvoked"] is False and record["officialReward"] is None
    assert record["error"]["stage"] == "task_initialization"
    assert "snapshot initialization interrupted" in record["error"]["message"]
    assert device.events == ["create", "reset", "initialize", "teardown", "close"]
    assert device.environments[0].state == {}
    assert device.environments[0].closed is True
    assert record["cleanup"] == {
        "taskTearDown": "completed", "environment": "closed", "sessions": "absent",
    }


@pytest.mark.parametrize("invalid", [True, False, None, "0", {}, float("nan"), float("inf"), -float("inf"), -0.01, 1.01])
def test_invalid_evaluator_return_fails_instead_of_scoring_and_cleans_up(device, invalid):
    spec = device.manifest["tasks"][0]
    record = rehearsal.run_task(device.manifest, spec, device.project, "fixture-adb")
    assert record["qualified"] is True
    assert record["evaluatorProbe"]["initialStateReturn"] == 0.0
    assert record["officialReward"] is None and record["agentInvoked"] is False
    assert rehearsal._task_qualified(record, spec, _sha256(device.manifest)) is True
    device.initial_return = invalid

    failed = rehearsal.run_task(device.manifest, spec, device.project, "fixture-adb")

    assert failed["qualified"] is False
    assert failed["error"]["stage"] == "evaluator_probe"
    assert failed["error"]["type"] == "ValueError"
    assert "invalid reward" in failed["error"]["message"]
    assert failed["officialReward"] is None and failed["agentInvoked"] is False
    assert "evaluatorProbe" not in failed
    assert all(env.closed and not env.state for env in device.environments)


@pytest.mark.parametrize("failure", ["teardown", "close"])
def test_unproven_cleanup_halts_all116_rehearsal_before_later_tasks(device, monkeypatch, failure):
    manifest = device.manifest
    first, second, third = manifest["tasks"][:3]
    device.failures[second["name"]] = failure
    manifest_path = device.project / "manifest.json"
    _write_json(manifest_path, manifest)
    readiness_path = device.project / "readiness.json"
    readiness = {
        "schemaVersion": 2, "qualified": True, "environmentClose": "closed",
        "manifestSha256": _sha256(manifest),
        "target": manifest["target"],
        "environmentArtifacts": manifest["protocol"]["environmentArtifacts"],
        "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
        "adbOutputIsolated": True, "snapshotRestores": [],
    }
    readiness["identitySha256"] = _sha256(readiness)
    _write_json(readiness_path, readiness)
    monkeypatch.setattr(campaign, "_load_manifest", lambda path, project: json.loads(path.read_text()))
    monkeypatch.setattr(rehearsal, "attest_device", lambda readiness, adb: {"qualified": True, "mismatches": []})
    monkeypatch.setattr(rehearsal.shutil, "which", lambda command: "/usr/bin/sandbox-exec")
    monkeypatch.setattr(rehearsal, "probe_host_media", lambda *args, **kwargs: _host_media(manifest))

    def worker(command, timeout):
        index = int(command[command.index("--task-index") + 1])
        result_path = Path(command[command.index("--output") + 1])
        record = rehearsal.run_task(manifest, manifest["tasks"][index], device.project, "fixture-adb")
        _write_json(result_path, record)
        return 0 if record["qualified"] else 1

    monkeypatch.setattr(campaign, "_run_process", worker)
    output = device.project / "output"
    args = argparse.Namespace(
        project=str(device.project), manifest=str(manifest_path),
        readiness_report=str(readiness_path), output_dir=str(output), adb_path="fixture-adb",
    )

    assert rehearsal.run_rehearsal(args) == 2

    report = json.loads((output / "report.json").read_text())
    assert report["qualified"] is False
    assert report["agentInvoked"] is False and report["officialReward"] is None
    assert [row["task"] for row in report["tasks"]] == [first["name"], second["name"]]
    assert [row["qualified"] for row in report["tasks"]] == [True, False]
    assert device.reconstructed == [first["name"], second["name"]]
    assert len(device.environments) == 2
    assert all(env.close_attempted for env in device.environments)
    assert not (output / "tasks" / f"{third['index']:03d}-{third['name']}").exists()
    successful = json.loads((output / report["tasks"][0]["result"]).read_text())
    failed = json.loads((output / report["tasks"][1]["result"]).read_text())
    assert successful["evaluatorProbe"]["initialStateReturn"] == 0.0
    assert successful["qualified"] is True
    assert successful["agentInvoked"] is False and successful["officialReward"] is None
    assert failed["cleanup"]["taskTearDown" if failure == "teardown" else "environment"] == "failed:RuntimeError"
    assert failed["qualified"] is False
    assert "no next task started" in report["error"]["message"]
    assert report["identitySha256"] == _sha256({key: value for key, value in report.items() if key != "identitySha256"})


class _ReferenceTask(information_retrieval.InformationRetrieval):
    def __init__(self, template):
        self._template = template
        super().__init__({})
        self.initialized = True

    @property
    def task_template(self):
        return self._template

    @classmethod
    def generate_random_params(cls):
        return {}


def _answer_proto(answer_type):
    task = task_pb2.Task(complexity=1)
    types = task_pb2.Expectation
    if answer_type == "datetime":
        task.relevant_state.state.calendar.events.add(start_date="October 15 2023", start_time="12:30")
        task.relevant_state.state.calendar.events.add(start_date="October 16 2023", start_time="09:05")
        for field, match_type in [("start_date", types.DATE_MATCH), ("start_time", types.TIME_MATCH)]:
            expectation = task.success_criteria.expectations.add(match_type=match_type)
            expectation.field_transformation.field_name = field
            expectation.field_transformation.operation = task_pb2.FieldTransformation.IDENTITY
    else:
        match_type, value = {
            "number": (types.NUMBER_MATCH, "12.5"),
            "date": (types.DATE_MATCH, "October 15 2023"),
            "time": (types.TIME_MATCH, "09:05"),
        }[answer_type]
        task.success_criteria.expectations.add(match_type=match_type, expected_value=value)
    return task


@pytest.mark.parametrize("answer_type", ["number", "date", "time", "datetime"])
def test_real_ir_reference_answer_formats_typed_values_and_rejection_clears_cache(answer_type):
    task = _ReferenceTask(_answer_proto(answer_type))
    env = SimpleNamespace(interaction_cache="")

    probe = rehearsal._probe_evaluator(task, env)

    assert probe["initialStateReturn"] == 0.0
    assert probe["referenceAnswerReturn"] == 1.0
    assert env.interaction_cache == ""
    # An empty expected answer cannot prove that the real answer checker ran.
    task.task.ClearField("success_criteria")
    with pytest.raises(ValueError, match="reference answer"):
        rehearsal._probe_evaluator(task, env)
    assert env.interaction_cache == ""


@pytest.mark.parametrize("invalid", [True, None, "1", float("nan"), float("inf"), 0.0, 1.01])
def test_invalid_ir_reference_return_fails_and_always_clears_answer_cache(invalid):
    class ReferenceReturnTask(_ReferenceTask):
        reference_return = 1.0

        def is_successful(self, env):
            if env.interaction_cache:
                return self.reference_return
            return super().is_successful(env)

    task = ReferenceReturnTask(_answer_proto("number"))
    env = SimpleNamespace(interaction_cache="")
    assert rehearsal._probe_evaluator(task, env)["referenceAnswerReturn"] == 1.0
    task.reference_return = invalid

    with pytest.raises(ValueError, match="reference"):
        rehearsal._probe_evaluator(task, env)
    assert env.interaction_cache == ""
