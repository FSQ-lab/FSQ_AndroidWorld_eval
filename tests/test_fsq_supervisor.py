import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

import pytest

from fsq_androidworld_eval import fsq_supervisor as supervisor
from fsq_androidworld_eval.fsq_supervisor import _group_snapshot, _supervise, run_fsq_worker, sandbox_policy


def test_process_exit_is_observed_without_fabricated_completion(tmp_path):
    receipt = _supervise(
        [sys.executable, "-B", "-c", "raise SystemExit(7)"],
        cwd=tmp_path, environment=dict(os.environ), log_path=tmp_path / "worker.log",
        business_deadline=time.monotonic() + 10, cleanup_seconds=0.1, grace_seconds=0.1,
    )
    assert receipt["exitCode"] == 7
    assert receipt["workerExitObserved"] is True
    assert receipt["businessDeadlineReached"] is False
    assert receipt["spawnCount"] == 1
    assert receipt["groupCleanup"] == "settled"
    assert receipt["leaderCleanup"] == "reaped"
    assert receipt["pgid"] == receipt["pid"]


def test_deadline_terminates_one_worker_without_business_retry(tmp_path):
    receipt = _supervise(
        [sys.executable, "-B", "-c", "import time; time.sleep(60)"],
        cwd=tmp_path, environment=dict(os.environ), log_path=tmp_path / "worker.log",
        business_deadline=time.monotonic() + 0.03, cleanup_seconds=0.02, grace_seconds=0.05,
    )
    assert receipt["businessDeadlineReached"] is True
    assert receipt["terminated"] is True
    assert receipt["exitCode"] != 0
    assert receipt["workerExitObserved"] is True
    assert receipt["spawnCount"] == 1
    with pytest.raises(ProcessLookupError):
        os.kill(receipt["pid"], 0)


def test_oracle_tree_cannot_contain_worker_workspace(tmp_path):
    oracle = tmp_path / "oracle"
    with pytest.raises(ValueError, match="outside"):
        sandbox_policy([oracle], worker_root=oracle / "agent")
    with pytest.raises(ValueError, match="outside"):
        sandbox_policy([oracle], worker_root=oracle)


def test_invalid_window_fails_before_process_or_log(tmp_path):
    with pytest.raises(ValueError, match="negative"):
        _supervise([sys.executable], cwd=tmp_path, environment={},
                   log_path=tmp_path / "not-created", business_deadline=0,
                   cleanup_seconds=-1, grace_seconds=0)
    assert not (tmp_path / "not-created").exists()


def test_writable_root_cannot_contain_oracle_or_readonly_staging(tmp_path):
    with pytest.raises(ValueError, match="outside"):
        sandbox_policy([tmp_path / "owned" / "oracle"], worker_root=tmp_path / "owned")
    with pytest.raises(ValueError, match="outside"):
        sandbox_policy([tmp_path / "oracle"], worker_root=tmp_path / "worker",
                       write_roots=[tmp_path / "oracle" / "nested"])




@pytest.mark.parametrize("broad", [Path("/"), Path.home(), Path("/private"), Path("/tmp")])
def test_broad_runtime_root_is_not_a_read_allowlist(tmp_path, broad):
    with pytest.raises(ValueError, match="explicit"):
        sandbox_policy([], worker_root=tmp_path / "worker", read_roots=[broad])


def test_native_auth_permissions_are_precise_and_reject_oracle_overlap(tmp_path):
    native_root = tmp_path / "native-fsq-user"
    with pytest.raises(ValueError, match="separate"):
        sandbox_policy([native_root], worker_root=tmp_path / "worker",
                       native_user_config_root=native_root)
    with pytest.raises(ValueError, match="broaden"):
        sandbox_policy([], worker_root=tmp_path / "worker", read_roots=[tmp_path],
                       native_user_config_root=native_root)


@pytest.mark.parametrize("leader_exits", [False, True])
def test_same_owned_group_child_is_settled_after_leader_exit_or_term(tmp_path, leader_exits):
    pid_file = tmp_path / "owned-pids.json"
    source = """
import json, os, signal, sys, time
from pathlib import Path
pid_file = Path(sys.argv[1])
child = os.fork()
if child == 0:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    pid_file.write_text(json.dumps({'leader': os.getppid(), 'child': os.getpid(), 'pgid': os.getpgrp()}))
    while True:
        time.sleep(1)
while not pid_file.exists():
    time.sleep(.005)
if sys.argv[2] == 'exit':
    raise SystemExit(0)
while True:
    time.sleep(1)
"""
    receipt = None
    try:
        receipt = _supervise(
            [sys.executable, "-B", "-c", source, str(pid_file), "exit" if leader_exits else "wait"],
            cwd=tmp_path, environment=dict(os.environ), log_path=tmp_path / "group.log",
            business_deadline=time.monotonic() + (10 if leader_exits else 0.5),
            cleanup_seconds=0.1, grace_seconds=0.15, receipt_path=tmp_path / "process.json",
        )
        pids = json.loads(pid_file.read_text())
        assert pids["pgid"] == receipt["pgid"] == receipt["pid"] == pids["leader"]
        assert receipt["businessDeadlineReached"] is not leader_exits
        assert receipt["workerExitObserved"] is True
        assert receipt["leaderCleanup"] == "reaped"
        assert receipt["terminated"] is True
        assert receipt["killed"] is True
        assert receipt["groupCleanup"] == "settled"
        assert receipt["groupObservation"]["runningPids"] == []
        assert any(pids["child"] in entry["observation"].get("runningPids", [])
                   for entry in receipt["groupObservations"])
        final = _group_snapshot(pids["pgid"], os.getuid())
        assert final["observed"] is True
        assert pids["child"] not in final["runningPids"]
        assert json.loads((tmp_path / "process.json").read_text()) == receipt
    finally:
        # Only the probe's freshly created process group can be signaled.
        group = receipt["pgid"] if receipt else None
        if group is None and (tmp_path / "process.json").is_file():
            group = json.loads((tmp_path / "process.json").read_text()).get("pgid")
        if group is not None:
            try:
                os.killpg(group, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_process_table_uncertainty_never_claims_group_cleanup(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "_group_snapshot", lambda *_: {
        "observed": False, "sameOwner": None, "members": None,
        "runningPids": None, "error": "ControlledUnavailable"})
    receipt = _supervise(
        [sys.executable, "-B", "-c", "raise SystemExit(0)"], cwd=tmp_path,
        environment=dict(os.environ), log_path=tmp_path / "unknown.log",
        business_deadline=time.monotonic() + 10, cleanup_seconds=0, grace_seconds=0,
        receipt_path=tmp_path / "process.json",
    )
    assert receipt["workerExitObserved"] is True
    assert receipt["leaderCleanup"] == "reaped"
    assert receipt["groupCleanup"] == "unknown"
    assert receipt["signals"] == []
    assert json.loads((tmp_path / "process.json").read_text()) == receipt


def test_unknown_process_table_cleans_known_leader_without_claiming_group_settled(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "_group_snapshot", lambda *_: {
        "observed": False, "sameOwner": None, "members": None,
        "runningPids": None, "error": "ControlledUnavailable"})
    receipt = _supervise(
        [sys.executable, "-B", "-c", "import time; time.sleep(60)"], cwd=tmp_path,
        environment=dict(os.environ), log_path=tmp_path / "unknown-running.log",
        business_deadline=time.monotonic() + 0.1, cleanup_seconds=0, grace_seconds=0.3,
        receipt_path=tmp_path / "process.json",
    )
    assert receipt["workerExitObserved"] is True
    assert receipt["groupCleanup"] == "unknown"
    assert receipt["terminated"] is True
    assert receipt["signals"][0]["ownershipBasis"] == "live_created_leader_pgid"
    assert receipt["signals"][0]["observedPids"] is None
    assert json.loads((tmp_path / "process.json").read_text()) == receipt


def test_supervision_exception_preserves_terminal_process_evidence(tmp_path, monkeypatch):
    original = supervisor._group_snapshot
    calls = 0
    def interrupt_once(*args):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("controlled supervisor interruption")
        return original(*args)
    monkeypatch.setattr(supervisor, "_group_snapshot", interrupt_once)
    receipt_path = tmp_path / "process.json"
    with pytest.raises(RuntimeError, match="controlled"):
        _supervise([sys.executable, "-B", "-c", "import time; time.sleep(60)"],
                   cwd=tmp_path, environment=dict(os.environ), log_path=tmp_path / "exception.log",
                   business_deadline=time.monotonic() + 10, cleanup_seconds=0,
                   grace_seconds=0.2, receipt_path=receipt_path)
    receipt = json.loads(receipt_path.read_text())
    assert receipt["spawnCount"] == 1
    assert receipt["phase"] == "terminal"
    assert receipt["supervisionError"]["type"] == "RuntimeError"
    assert receipt["workerExitObserved"] is True
    assert receipt["groupCleanup"] == "settled"
    assert receipt["killed"] is True


@pytest.mark.parametrize("payload,error_type", [('{"truncated":', "JSONDecodeError"),
                                              ("[]", "ValueError"), (None, "MissingWorkerResult")])
def test_malformed_result_keeps_consumer_visible_forced_receipt(tmp_path, monkeypatch, payload, error_type):
    real_is_file = Path.is_file
    monkeypatch.setattr(Path, "is_file", lambda path: path == Path("/usr/bin/sandbox-exec") or real_is_file(path))
    receipt = {"pid": 999999, "pgid": 999999, "exitCode": -9,
               "businessDeadlineReached": True, "terminated": True, "killed": True,
               "workerExitObserved": True, "spawnCount": 1, "groupCleanup": "unknown"}
    def controlled_supervisor(*args, **kwargs):
        assert Path(kwargs["environment"]["TMPDIR"]) == kwargs["log_path"].parent / "tmp"
        assert Path(kwargs["environment"]["TMPDIR"]).is_dir()
        kwargs["log_path"].write_text("controlled offline worker")
        if payload is not None:
            (kwargs["log_path"].parent / "worker-result.json").write_text(payload)
        return receipt
    monkeypatch.setattr(supervisor, "_supervise", controlled_supervisor)
    workspace = tmp_path / "owned" / "workspace"
    workspace.mkdir(parents=True)
    receipt_path = tmp_path / "evaluator-private" / "process.json"
    outcome = run_fsq_worker(
        {"workspace": str(workspace), "outputDir": str(tmp_path / "owned" / "worker"),
         "userConfigRoot": str(tmp_path / "native-fsq-user"), "businessDeadlineMonotonic": time.monotonic()},
        python=Path(sys.executable), worker_site=tmp_path / "owned" / "worker-site",
        private_dir=tmp_path / "owned" / "worker", oracle_roots=[tmp_path / "oracle"],
        process_receipt_path=receipt_path, runtime_read_roots=[Path(sys.prefix)],
    )
    assert outcome["process"] == receipt
    assert json.loads(receipt_path.read_text()) == receipt
    assert outcome["result"] is None
    assert outcome["resultError"]["type"] == error_type
    assert outcome["completionEvidence"] == "no_complete_worker_result"
    assert (outcome["resultReference"] is None) is (payload is None)


def test_receipt_must_be_outside_worker_writable_roots(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "is_file", lambda _: True)
    worker = tmp_path / "worker"
    with pytest.raises(ValueError, match="trusted process receipt"):
        run_fsq_worker(
            {"workspace": str(tmp_path / "workspace"), "outputDir": str(worker)},
            python=Path(sys.executable), worker_site=tmp_path / "worker-site", private_dir=worker,
            oracle_roots=[], process_receipt_path=worker / "receipt.json", runtime_read_roots=[],
        )
    assert not worker.exists()


@pytest.mark.skipif(sys.platform != "darwin" or not os.environ.get("FSQ_NATIVE_SANDBOX_SMOKE"),
                    reason="opt-in real macOS sandbox/native FileOps proof; no device/model")
def test_real_sandbox_native_fileops_allowlist(tmp_path, monkeypatch):
    """Set FSQ_NATIVE_PYTHON, FSQ_NATIVE_PACKAGE_ROOT and JSON FSQ_NATIVE_RUNTIME_READ_ROOTS.

    Runtime roots must be the frozen native venv/base Python and required library
    roots, not HOME/project. This only imports native code and reads owned probes;
    it never constructs a provider, Harness, device or model.
    """
    native_python = Path(os.environ["FSQ_NATIVE_PYTHON"]).absolute()
    package = Path(os.environ["FSQ_NATIVE_PACKAGE_ROOT"]).resolve()
    runtime = [Path(path) for path in json.loads(os.environ["FSQ_NATIVE_RUNTIME_READ_ROOTS"])]
    workspace = tmp_path / "owned" / "workspace"
    workspace.mkdir(parents=True)
    stage = tmp_path / "owned" / "worker-site" / "fsq_androidworld_eval"
    stage.mkdir(parents=True)
    for filename in ("__init__.py", "fsq_native.py", "fsq_worker.py"):
        shutil.copyfile(Path(supervisor.__file__).parent / filename, stage / filename)
    fake_home = tmp_path / "fake-home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda _: fake_home))
    targets = {
        "retained": tmp_path / "retained-corrected-source" / "android_world" / "tasks.textproto",
        "external": tmp_path / "external-results" / "raw-private" / "sentinel.txt",
        "omitted_retained": tmp_path / "unlisted-copy" / "tasks.textproto",
        "omitted_external": tmp_path / "unlisted-results" / "raw-private" / "sentinel.txt",
        "host_tmp_oracle": tmp_path / "host-shared-tmp" / "default.textproto",
        "omp": fake_home / ".omp" / "sentinel.txt",
        "copilot": fake_home / ".copilot" / "sentinel.txt",
    }
    for label, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("private-test-" + label)
    (workspace / "readable.txt").write_text("owned-readable")
    link = workspace / "oracle-link.txt"
    link.symlink_to(targets["retained"])
    policy = sandbox_policy(
        [tmp_path / "retained-corrected-source", tmp_path / "external-results"],
        worker_root=workspace,
        read_roots=[*runtime, native_python, native_python.resolve(), package, stage.parent],
        native_user_config_root=fake_home / ".fsq",
    )
    policy_path = workspace / "policy.sb"
    policy_path.write_text(policy)
    probe = """
import asyncio, json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
from fsq_agent.tools._file_ops import FileOps
from fsq_agent.config import activate_github_copilot_provider, load_user_provider_config
from fsq_androidworld_eval.fsq_worker import load_native_bindings
load_native_bindings()  # Import-only: proves real worker dependency imports survive.
native_root = Path(os.environ['HOME']) / '.fsq'
load_user_provider_config(native_root)
(native_root / 'auth' / 'openai.json').write_text('{"api_key":"fake-offline-only"}')
for _ in range(2):
    activate_github_copilot_provider(model='gpt-6.1-sol',
        github_token={'access_token': 'fake-offline-only'},
        provider_token={'token': 'fake-offline-only', 'plan': 'individual'}, user_config_root=native_root)
assert not (native_root / 'auth' / 'openai.json').exists()
for denied in (native_root / 'unrelated-secret.txt', native_root / 'auth' / '.unrecognized.abc.tmp'):
    try:
        denied.write_text('must-not-write')
    except PermissionError:
        pass
    else:
        raise AssertionError('native root received broad write permissions')
root = Path.cwd()
ops = FileOps(root=root)
async def probe():
    observed = {}
    owned = await ops.read_text({'path': 'readable.txt'})
    assert owned.status == 'success' and owned.output == 'owned-readable'
    written = await ops.write_text({'path': 'written.txt', 'content': 'owned-written'})
    assert written.status == 'success'
    for label, path in json.loads(sys.argv[3]).items():
        result = await ops.read_text({'path': os.path.relpath(path, root)})
        assert result.status == 'failed', label
        assert not result.output, label
        observed[label] = result.status
    linked = await ops.read_text({'path': 'oracle-link.txt'})
    assert linked.status == 'failed'
    try:
        Path(sys.argv[4]).write_text('must-not-write')
    except PermissionError:
        pass
    else:
        raise AssertionError('outside write unexpectedly allowed')
    print(json.dumps({'nativeImports': True, 'ownedReadWrite': True, 'denied': observed, 'symlinkDenied': True}))
asyncio.run(probe())
"""
    environment = {"HOME": str(fake_home), "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                   "TMPDIR": str(workspace), "PYTHONDONTWRITEBYTECODE": "1"}
    completed = subprocess.run(
        ["/usr/bin/sandbox-exec", "-f", str(policy_path), str(native_python), "-B", "-c", probe,
         str(package.parent), str(stage.parent), json.dumps({key: str(path.resolve()) for key, path in targets.items()}),
         str(tmp_path / "outside-write.txt")],
        cwd=workspace, env=environment, capture_output=True, text=True, timeout=30, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    observed = json.loads(completed.stdout.splitlines()[-1])
    assert observed["nativeImports"] is True
    assert observed["ownedReadWrite"] is True
    assert observed["denied"] == {label: "failed" for label in targets}
    assert (workspace / "written.txt").read_text() == "owned-written"
    assert not (tmp_path / "outside-write.txt").exists()
