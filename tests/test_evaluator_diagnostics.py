"""Offline consumer boundaries for private evaluator evidence; no device/process IO."""

from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import threading
from types import SimpleNamespace

from absl import logging as absl_logging
from android_world.task_evals.common_validators import sqlite_validators
import pytest

from fsq_androidworld_eval import evaluator_diagnostics as diagnostics
from fsq_androidworld_eval import runner
from fsq_androidworld_eval.scorer import record_classification
from fsq_androidworld_eval.submission import parse_submission


@pytest.fixture
def offline_attempt(tmp_path, monkeypatch):
    """Use the real runner, step adapter, reference loop and native row predicate.

    Host/device/process boundaries follow test_runner's offline readiness pattern.
    No Appium listener, MCP, OMP subprocess, device, initialization or frozen task
    is run. Native row validation operates only on synthetic in-memory rows.
    """
    count = 0

    def attempt(mode="reject", *, fail_write=False, provider="github-copilot",
                diagnostic_value=None, native_error=None, write_error=None):
        nonlocal count
        count += 1
        events = []
        hidden = f"hidden-expected-{count}"
        output = tmp_path / f"attempt-{count}"
        row = SimpleNamespace(name=hidden)

        class OfflineTask:
            name = f"OfflineDiagnostic{count}"
            complexity = 1
            app_names = ()
            params = {"requested": "ordinary-goal"}
            goal = "Complete the ordinary goal"
            device_time = datetime(2023, 10, 15, tzinfo=timezone.utc)
            start_on_home_screen = False
            calls = 0

            def initialize_task(self, env):
                events.append("initialize")
                logging.warning("outside-initialize")

            def is_successful(self, env):
                assert events[-1] == "proxy_exit"
                assert not (output / diagnostics.RECEIPT_PATH).exists()
                events.append("evaluate")
                self.calls += 1
                if diagnostic_value is not None:
                    logging.warning("native opaque values %s %s", diagnostic_value, diagnostic_value)
                if native_error is not None:
                    logging.error("native evaluator error", exc_info=(type(native_error), native_error, None))
                    raise native_error
                if mode == "silent":
                    return 0.5
                matched = sqlite_validators.validate_rows_addition_integrity(
                    [], [row] if mode == "pass" else [], [row], ["name"]
                )
                if mode == "raise":
                    raise ValueError(hidden)
                return (float(matched) + 1.0) / 2

            def tear_down(self, env):
                events.append("teardown")
                logging.warning("outside-teardown")

        task = OfflineTask()
        readiness = {"qualified": True, "environmentArtifacts": {},
                     "sessionAccessibilityConfig": runner.SESSION_ACCESSIBILITY_CONFIG}
        readiness["identitySha256"] = runner._sha256(readiness)
        readiness_path = tmp_path / f"readiness-{count}.json"
        readiness_path.write_text(json.dumps(readiness))
        args = runner.build_parser().parse_args([
            "--project", str(tmp_path), "--artifact-root", str(tmp_path), "--output-dir", str(output),
            "--task", task.name, "--model", "github-copilot/gpt-5.6-sol", "--expected-amkernel-version", "0.1.4",
            "--sandbox-profile", str(tmp_path / "sandbox"), "--readiness-report", str(readiness_path),
            "--expected-readiness-sha256", readiness["identitySha256"], "--expected-max-steps", "1",
            "--expected-params-sha256", runner._sha256(task.params),
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
        monkeypatch.setattr(runner, "close_environment", lambda env: events.append("environment_close"))

        class OfflineProxy:
            url = "http://offline-proxy.invalid"

            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                events.append("proxy_exit")

            def wait_for_idle(self, timeout):
                assert self.audit()["pendingRequestCount"] == 0

            def audit(self):
                return {"errors": [], "createdSessionCount": 0, "createdSessionHashes": [],
                        "deletedSessionHashes": [], "pendingRequestCount": 0,
                        "unknownCreationOutcomeCount": 0}

        monkeypatch.setattr(runner, "AppiumAuditProxy", OfflineProxy)
        agent_inputs = []

        def run_agent(**kwargs):
            assert not (output / diagnostics.RECEIPT_PATH).exists()
            agent_inputs.append(kwargs["prompt"])
            logging.warning("outside-agent")
            private = output / "raw-private"
            private.mkdir(mode=0o700)
            payload = json.dumps(parse_submission('{"taskOutcome":"done"}')).encode()
            submission_path = private / "business-submission.json"
            submission_path.write_bytes(payload)
            events.append("agent_exit")
            return {
                "processExited": True, "exitCode": 0, "agentCompleted": True,
                "completedBeforeBusinessDeadline": True, "termination": {"reason": "completed"},
                "normalized": {"model": "gpt-5.6-sol", "provider": provider, "parseErrors": 0,
                               "toolCalls": [], "finalText": "done"},
                "answerSubmission": {"path": "raw-private/business-submission.json",
                                     "sha256": hashlib.sha256(payload).hexdigest()},
            }

        monkeypatch.setattr(runner, "_run_agent", run_agent)
        if fail_write:
            original = diagnostics.os.replace

            def deny_diagnostic(source, destination):
                if Path(destination).name == "evaluator-diagnostics.json":
                    raise write_error if write_error is not None else PermissionError(hidden)
                return original(source, destination)

            monkeypatch.setattr(diagnostics.os, "replace", deny_diagnostic)
        exit_code = runner.run(args)
        record = json.loads((output / "result.json").read_bytes())
        receipt_path = output / diagnostics.RECEIPT_PATH
        receipt = json.loads(receipt_path.read_bytes()) if receipt_path.exists() else None
        return SimpleNamespace(task=task, output=output, record=record, receipt=receipt,
                               events=events, agent_inputs=agent_inputs, hidden=hidden, exit_code=exit_code)

    return attempt


@pytest.mark.parametrize("mode,reward,classification", [("reject", 0.5, "failed"), ("pass", 1.0, "passed")])
def test_native_rejection_evidence_is_private_without_changing_score_or_lifecycle(offline_attempt, mode, reward, classification):
    result = offline_attempt(mode)
    record, receipt = result.record, result.receipt
    reference = record["evaluator"]["diagnostics"]
    payload = (result.output / reference["path"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == reference["sha256"]
    assert len(payload) == reference["bytes"] <= diagnostics.MAX_RECEIPT_BYTES
    assert receipt["officialReward"] == record["officialReward"] == reward
    assert record_classification(record) == classification
    assert record["invalidReason"] is None and record["error"] is None
    assert result.task.calls == 1 and result.exit_code == 0
    assert result.events == ["initialize", "agent_exit", "proxy_exit", "evaluate", "teardown", "environment_close"]
    assert record["cleanup"]["taskTearDown"] == "completed"
    assert record["cleanup"]["environment"] == "closed"
    assert record["agent"]["termination"]["reason"] == "completed"
    assert receipt["task"]["paramsSha256"] == record["task"]["paramsSha256"]
    assert receipt["componentResults"]["status"] == "not_provided"
    private_logs = receipt["logCapture"]["records"]
    if mode == "reject":
        assert [Path(entry["file"]).name for entry in private_logs] == ["sqlite_validators.py"]
        assert private_logs[0]["arguments"]["items"][0]["omittedType"] == "SimpleNamespace"
    else:
        assert private_logs == []
    assert not any(marker in payload.decode() for marker in ["outside-initialize", "outside-agent", "outside-teardown"])
    public = json.dumps(record)
    assert result.hidden not in public and "messageTemplate" not in public
    assert "sqlite_validators.py" not in public
    assert result.hidden not in json.dumps(result.agent_inputs)
    assert "evaluator-diagnostics" not in json.dumps(result.agent_inputs)
    assert (result.output / "raw-private").stat().st_mode & 0o777 == 0o700
    assert (result.output / reference["path"]).stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("fail_write", [False, True])
def test_native_exception_details_stay_private_and_cleanup_still_runs(offline_attempt, fail_write):
    result = offline_attempt("raise", fail_write=fail_write)
    record = result.record
    assert result.task.calls == 1 and result.exit_code == 1
    assert record["officialReward"] is None
    assert record_classification(record) == "invalid_evaluator"
    assert record["error"] == {"type": "ValueError"}
    assert result.events[-2:] == ["teardown", "environment_close"]
    assert record["cleanup"]["taskTearDown"] == "completed"
    assert record["cleanup"]["environment"] == "closed"
    assert result.hidden not in json.dumps(record)
    assert result.hidden not in json.dumps(result.agent_inputs)
    if fail_write:
        assert record["evaluator"]["diagnostics"] == {"status": "write_failed", "errorType": "PermissionError"}
        assert result.receipt is None
        assert not (result.output / "raw-private/evaluator-diagnostics.json.tmp").exists()
    else:
        assert result.receipt["outcome"] == "raised"
        assert result.receipt["exception"]["arguments"]["items"] == [result.hidden]
        assert any(frame["function"] == "is_successful" for frame in result.receipt["exception"]["frames"])


def test_write_failure_does_not_invalidate_partial_reward(offline_attempt):
    result = offline_attempt(fail_write=True)
    assert result.record["officialReward"] == 0.5
    assert record_classification(result.record) == "failed"
    assert result.exit_code == 0 and result.record["error"] is None
    assert result.record["evaluator"]["diagnostics"]["status"] == "write_failed"
    assert result.events[-2:] == ["teardown", "environment_close"]


def test_scalar_only_task_does_not_invent_component_evidence(offline_attempt):
    first = offline_attempt()
    quiet = offline_attempt("silent")
    assert first.receipt["logCapture"]["records"][0]["file"].endswith("sqlite_validators.py")
    assert quiet.receipt["logCapture"]["records"] == []
    assert quiet.receipt["componentResults"] == {"status": "not_provided", "source": "scalar_return_interface"}
    assert quiet.receipt["officialReward"] == 0.5
    assert quiet.receipt["task"]["name"] != first.receipt["task"]["name"]
    assert quiet.record["evaluator"]["diagnostics"]["status"] == "written"


def test_no_evaluator_receipt_when_protocol_rejects_before_scoring(offline_attempt):
    result = offline_attempt(provider="wrong-provider")
    assert result.task.calls == 0
    assert result.record["officialReward"] is None
    assert record_classification(result.record) == "invalid_protocol"
    assert result.receipt is None and "evaluator" not in result.record
    assert result.events[-2:] == ["teardown", "environment_close"]


def test_log_flood_and_large_exception_are_bounded_without_swallowing_original(tmp_path, monkeypatch):
    root = logging.getLogger()
    monkeypatch.setattr(root, "handlers", [logging.NullHandler()])
    original_filters, original_level = list(root.filters), root.level
    error = ValueError("hidden\U0001f512" * 100000)
    capture = diagnostics.EvaluatorDiagnostics(tmp_path, task_name="OfflineFlood", params_sha256="a" * 64)
    with pytest.raises(ValueError) as caught:
        with capture:
            for i in range(1000):
                logging.warning("native diagnostic %s", "\U0001f512" * 4096)
            raise error
    assert caught.value is error
    payload = (tmp_path / diagnostics.RECEIPT_PATH).read_bytes()
    receipt = json.loads(payload)
    assert len(payload) <= diagnostics.MAX_RECEIPT_BYTES
    logs = receipt["logCapture"]
    assert len(logs["records"]) <= diagnostics.MAX_LOG_RECORDS
    assert len(logs["records"]) + logs["droppedRecords"] == 1000
    assert logs["droppedRecords"] > 0 and logs["omittedValues"] > 0
    assert receipt["captureStatus"] == capture.reference["status"] == "truncated"
    projected = receipt["exception"]["arguments"]["items"][0]
    assert len(projected["prefix"]) <= diagnostics.MAX_VALUE_CHARS
    assert projected["omittedCharacters"] == len(error.args[0]) - len(projected["prefix"])
    assert root.filters == original_filters and root.level == original_level


def test_capture_does_not_format_objects_or_change_existing_log_sinks(tmp_path, monkeypatch):
    root = logging.getLogger()
    sink = logging.NullHandler()
    monkeypatch.setattr(root, "handlers", [sink])
    handlers, filters, level = list(root.handlers), list(root.filters), root.level

    class DiagnosticObject:
        def __str__(self):
            raise AssertionError("capture must not stringify evaluator objects")

        __repr__ = __str__

    capture = diagnostics.EvaluatorDiagnostics(tmp_path, task_name="OfflineObject", params_sha256="a" * 64)
    with capture:
        absl_logging.warning("native object %s", DiagnosticObject())
    receipt = json.loads((tmp_path / diagnostics.RECEIPT_PATH).read_bytes())
    assert receipt["logCapture"]["records"][0]["arguments"]["items"][0]["omittedType"] == "DiagnosticObject"
    assert receipt["logCapture"]["captureErrors"] == 0
    assert root.handlers == handlers and root.filters == filters and root.level == level


def test_overlapping_attempts_capture_only_their_own_thread(tmp_path, monkeypatch):
    root = logging.getLogger()
    monkeypatch.setattr(root, "handlers", [logging.NullHandler()])
    prior_filters = list(root.filters)
    barrier = threading.Barrier(2)
    errors = []

    def attempt(name):
        try:
            with diagnostics.EvaluatorDiagnostics(tmp_path / name, task_name=name, params_sha256="a" * 64):
                barrier.wait(timeout=5)
                logging.warning("native rejection %s", name)
                barrier.wait(timeout=5)
        except BaseException as exc:
            errors.append(exc)

    for name in ("one", "two"):
        (tmp_path / name).mkdir()
    threads = [threading.Thread(target=attempt, args=(name,)) for name in ("one", "two")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()
    assert errors == []
    for name in ("one", "two"):
        receipt = json.loads((tmp_path / name / diagnostics.RECEIPT_PATH).read_bytes())
        assert [entry["arguments"]["items"] for entry in receipt["logCapture"]["records"]] == [[name]]
    assert root.filters == prior_filters


@pytest.mark.parametrize("source", ["root", "absl"])
def test_detaching_capture_preserves_inflight_other_attempt_and_foreign_filters(tmp_path, monkeypatch, source):
    logger = logging.getLogger() if source == "root" else absl_logging.get_absl_logger()
    observed_before, observed_late, sink_records = [], [], []

    class ForeignFilter(logging.Filter):
        def __init__(self, records):
            super().__init__()
            self.records = records

        def filter(self, record):
            self.records.append(record.args)
            return True

    class ForeignSink(logging.Handler):
        def emit(self, record):
            sink_records.append(record.args)

    before, late, sink = ForeignFilter(observed_before), ForeignFilter(observed_late), ForeignSink()
    monkeypatch.setattr(logger, "filters", [before])
    monkeypatch.setattr(logger, "handlers", [sink])
    monkeypatch.setattr(logger, "propagate", False)
    level = logger.level
    reached, resume = threading.Event(), threading.Event()
    errors = []
    owner_thread = threading.get_ident()
    a = diagnostics.EvaluatorDiagnostics(tmp_path / "A", task_name="A", params_sha256="a" * 64)
    b = diagnostics.EvaluatorDiagnostics(tmp_path / "B", task_name="B", params_sha256="b" * 64)
    (tmp_path / "A").mkdir()
    (tmp_path / "B").mkdir()
    original_filter = a.filter

    def pause_after_a(record):
        result = original_filter(record)
        if record.thread != owner_thread:
            reached.set()
            assert resume.wait(timeout=5)
        return result

    monkeypatch.setattr(a, "filter", pause_after_a)

    def run_b():
        try:
            with b:
                logger.warning("native rejection %s", "B")
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=run_b)
    try:
        with a:
            logger.warning("native rejection %s", "A")
            # A foreign addition made while capture is active must survive exit.
            logger.addFilter(late)
            worker.start()
            assert reached.wait(timeout=5)
        # A is detached while B is paused inside the stdlib filter iterator.
        assert logger.filters == [before, late, b]
    finally:
        resume.set()
        if worker.ident is not None:
            worker.join(timeout=10)
    assert not worker.is_alive() and errors == []
    for name in ("A", "B"):
        receipt = json.loads((tmp_path / name / diagnostics.RECEIPT_PATH).read_bytes())
        assert [entry["arguments"]["items"] for entry in receipt["logCapture"]["records"]] == [[name]]
        assert receipt["logCapture"]["droppedRecords"] == receipt["logCapture"]["captureErrors"] == 0
        assert receipt["captureStatus"] == "written"
    assert observed_before == sink_records == [("A",), ("B",)]
    assert observed_late == [("B",)]
    assert logger.filters == [before, late]
    assert logger.handlers == [sink] and logger.level == level and logger.propagate is False


def test_long_type_metadata_is_bounded_before_json_in_logs_and_native_exception(tmp_path, monkeypatch):
    monkeypatch.setattr(logging.getLogger(), "handlers", [logging.NullHandler()])
    long_name = "T" * 10000
    value = type(long_name, (), {})()
    error = type(long_name, (ValueError,), {})(value)
    capture = diagnostics.EvaluatorDiagnostics(tmp_path, task_name="LongType", params_sha256="a" * 64)
    for nodes, characters in ((64, 2048), (0, 17), (0, 0)):
        budget = [nodes, characters]
        projected = capture._value(value, budget=budget)
        count = len(projected["omittedType"])
        assert count == min(diagnostics.MAX_TYPE_NAME_CHARS, characters)
        assert budget[1] == characters - count

    original_dumps = json.dumps

    def check_metadata(value):
        if type(value) is dict:
            for key, child in value.items():
                if key == "omittedType" or key == "type":
                    if type(child) is str:
                        assert len(child) <= diagnostics.MAX_TYPE_NAME_CHARS
                check_metadata(child)
        elif type(value) is list or type(value) is tuple:
            for child in value:
                check_metadata(child)

    def bounded_dumps(value, *args, **kwargs):
        # Audit real serializer inputs, not merely the already-bounded file.
        check_metadata(value)
        return original_dumps(value, *args, **kwargs)

    monkeypatch.setattr(diagnostics.json, "dumps", bounded_dumps)
    with pytest.raises(ValueError) as caught:
        with capture:
            logging.warning("native opaque values %s %s", value, value)
            raise error
    assert caught.value is error
    payload = (tmp_path / diagnostics.RECEIPT_PATH).read_bytes()
    receipt = json.loads(payload)
    assert len(payload) <= diagnostics.MAX_RECEIPT_BYTES
    assert receipt["exception"]["type"] == long_name[:diagnostics.MAX_TYPE_NAME_CHARS]
    assert receipt["exception"]["arguments"]["items"][0]["omittedType"] == long_name[:diagnostics.MAX_TYPE_NAME_CHARS]
    assert receipt["captureStatus"] == "truncated"
    assert receipt["logCapture"]["omittedValues"] > 0
    assert receipt["logCapture"]["captureErrors"] == 0
    args = receipt["logCapture"]["records"][0]["arguments"]
    assert [len(item["omittedType"]) for item in args["items"]] == [128, 128]


def _hostile_metadata():
    events = []

    class HostileMeta(type):
        __hash__ = type.__hash__

        def __eq__(cls, other):
            events.append("equality")
            raise SystemExit("observer invoked metaclass equality")

        def __getattribute__(cls, name):
            if name == "__name__":
                events.append("name_lookup")
                raise SystemExit("observer invoked metaclass name lookup")
            return type.__getattribute__(cls, name)

        @property
        def __name__(cls):
            events.append("name_descriptor")
            raise SystemExit("observer invoked metaclass name descriptor")

    class Opaque(metaclass=HostileMeta):
        def __str__(self):
            events.append("str")
            raise SystemExit("observer formatted an evaluator object")

        __repr__ = __str__

    class NativeError(ValueError, metaclass=HostileMeta):
        pass

    class NativeIOError(OSError, metaclass=HostileMeta):
        pass

    return SimpleNamespace(value=Opaque(), error=NativeError, io_error=NativeIOError, events=events)


@pytest.mark.parametrize("outcome", ["return", "raise", "write_failure"])
def test_hostile_metaclass_hooks_do_not_change_scoring_terminal_or_cleanup(offline_attempt, monkeypatch, outcome):
    monkeypatch.setattr(logging.getLogger(), "handlers", [logging.NullHandler()])
    hostile = _hostile_metadata()
    result = offline_attempt(
        "pass", diagnostic_value=hostile.value,
        native_error=hostile.error(hostile.value) if outcome == "raise" else None,
        fail_write=outcome == "write_failure",
        write_error=hostile.io_error(hostile.value) if outcome == "write_failure" else None,
    )
    assert hostile.events == []
    record = result.record
    assert result.task.calls == 1
    assert record["agent"]["termination"]["reason"] == "completed"
    assert result.events == ["initialize", "agent_exit", "proxy_exit", "evaluate", "teardown", "environment_close"]
    assert record["cleanup"]["taskTearDown"] == "completed"
    assert record["cleanup"]["environment"] == "closed"
    if outcome == "raise":
        assert result.exit_code == 1 and record["officialReward"] is None
        assert record_classification(record) == "invalid_evaluator"
        assert record["error"] == {"type": "NativeError"}
        assert result.receipt["exception"]["type"] == "NativeError"
        logged_error = result.receipt["logCapture"]["records"][1]["exception"]
        assert logged_error["type"] == "NativeError"
        assert logged_error["arguments"]["items"][0]["omittedType"] == "Opaque"
    else:
        assert result.exit_code == 0 and record["officialReward"] == 1.0
        assert record_classification(record) == "passed" and record["error"] is None
    if outcome == "write_failure":
        assert record["evaluator"]["diagnostics"] == {"status": "write_failed", "errorType": "NativeIOError"}
        assert result.receipt is None
    else:
        assert result.receipt["captureStatus"] == "truncated"
        assert result.receipt["logCapture"]["captureErrors"] == 0
        assert [arg["omittedType"] for arg in result.receipt["logCapture"]["records"][0]["arguments"]["items"]] == ["Opaque", "Opaque"]
