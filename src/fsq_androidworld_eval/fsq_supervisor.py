"""Bound one complete native FSQ worker with a default-denied filesystem."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from typing import Any


def private_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(path.name + ".tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def artifact_reference(path: Path, relative_to: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": str(path.relative_to(relative_to)),
            "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _overlap(first: Path, second: Path) -> bool:
    return _inside(first, second) or _inside(second, first)


def sandbox_policy(
    oracle_roots: list[Path], *, worker_root: Path,
    read_roots: list[Path] | None = None, write_roots: list[Path] | None = None,
    native_user_config_root: Path | None = None,
) -> str:
    """Allow only explicit runtime reads and owned writes, after canonicalization.

    Callers supply frozen native package, venv prefix, base Python prefix, and
    required ADB executable/library roots, never HOME or an enclosing project.
    Worker modules are a separate read root. Native user config/auth remains at
    its original root, with exact lock/config/auth/atomic-temp grants only.
    Every actual evaluator/source-copy/result root is an explicit denial too.
    Complement denials preserve runtime grants without SBPL deny/allow ambiguity.
    """
    # Keep metadata for intermediate aliases (uv's version selector, for example)
    # even though data grants below use only their canonical targets.
    pending = [Path(os.path.abspath(root.expanduser()))
               for root in (worker_root, *(read_roots or []), *(write_roots or []))]
    lexical_metadata: set[Path] = set()
    seen: set[Path] = set()
    while pending:
        candidate = pending.pop()
        if candidate in seen:
            continue
        seen.add(candidate)
        for component in (candidate, *candidate.parents):
            lexical_metadata.add(component)
            if component.is_symlink():
                target = Path(os.readlink(component))
                if not target.is_absolute():
                    target = component.parent / target
                pending.append(Path(os.path.abspath(target)))
    worker_root = worker_root.expanduser().resolve()
    denied = {root.expanduser().resolve() for root in oracle_roots}
    denied.update((Path.home() / name).resolve() for name in (".omp", ".copilot"))
    writable = {worker_root, *(root.expanduser().resolve() for root in (write_roots or []))}
    readable = {root.expanduser().resolve() for root in (read_roots or [])} | writable
    for root in writable:
        if any(_overlap(root, oracle) for oracle in denied):
            raise ValueError("worker writable roots must be outside and not contain every oracle tree")
    home = Path.home().resolve()
    broad = {Path("/"), home, *home.parents, Path("/private"), Path("/private/var"),
             Path("/private/tmp"), Path("/tmp").resolve(), Path("/var").resolve()}
    if any(root in broad for root in readable):
        raise ValueError("runtime roots must be explicit, not broad HOME/system/temp roots")
    native_root = native_user_config_root.expanduser().resolve() if native_user_config_root is not None else None
    auth_paths: set[Path] = set()
    auth_directories: set[Path] = set()
    if native_root is not None:
        if native_root in broad or any(_overlap(native_root, root) for root in denied | writable):
            raise ValueError("native config/auth root must be separate from oracle and worker roots")
        # Native config/_user_provider.py: activation snapshots/removes these exact
        # native-provider files; rollback may restore each via _stage_write.
        auth_directories = {native_root, native_root / "auth"}
        auth_paths = {native_root / "config.yaml", native_root / ".config.lock"}
        auth_paths.update(native_root / "auth" / name for name in (
            "github-copilot-token.json", "github-copilot-provider-token.json",
            "azure-openai.json", "openai.json", "deepseek.json", "google-gemini.json", "kimi.json",
        ))
        for path in auth_directories | auth_paths:
            if path.resolve() != path:
                raise ValueError("native config/auth entries must not redirect outside their canonical root")
        if any(_overlap(root, native_root) for root in readable):
            raise ValueError("runtime read roots must not broaden native config/auth permissions")
    # These are OS runtime resources, not /usr, /Library, /private or HOME grants.
    readable.update(Path(path).resolve() for path in (
        "/System/Library", "/usr/lib", "/usr/share/zoneinfo", "/private/var/db/timezone",
        "/private/etc/ssl", "/private/etc/hosts", "/private/etc/resolv.conf",
        "/private/etc/localtime", "/dev/null", "/dev/random", "/dev/urandom",
    ))

    def alternatives(paths: set[Path], *, metadata: bool = False) -> str:
        filters = [f'({"literal" if metadata or path.is_file() else "subpath"} {json.dumps(str(path))})'
                   for path in sorted(paths)]
        return "(require-any " + " ".join(filters) + ")"

    # SBPL denials override grants. Deny only the complement of each allowed
    # path set; a blanket file-read/file-write denial would also deny Python.
    ancestors = {parent for root in readable | auth_paths for parent in root.parents} | lexical_metadata
    # dyld opens the root directory itself; never grant a root subpath.
    common_reads = [alternatives(readable), '(literal "/")']
    # FileFinder enumerates sys.path entries to discover an allowed package.
    # Directory-only literals do not authorize any sibling file's contents.
    package_search = {root.expanduser().resolve().parent for root in (read_roots or []) if root.is_dir()}
    common_reads.extend(f"(literal {json.dumps(str(path))})" for path in sorted(package_search))
    common_writes = [alternatives(writable), '(literal "/dev/null")']
    if native_root is not None:
        common_reads.append(alternatives(auth_paths, metadata=True))
        common_writes.extend((alternatives(auth_paths, metadata=True),
                              alternatives(auth_directories, metadata=True)))
        for path in sorted(auth_paths - {native_root / ".config.lock"}):
            # Native tempfile.mkstemp atomic replacement names, not an auth dir grant.
            pattern = "^" + re.escape(str(path.parent / ("." + path.name + "."))) + "[a-z0-9_]+\\.tmp$"
            # SBPL #"..." retains regex escapes, unlike an ordinary JSON string.
            quoted_pattern = json.dumps(pattern, ensure_ascii=False).replace("\\\\", "\\")
            predicate = f"(regex #{quoted_pattern})"
            common_reads.append(predicate)
            common_writes.append(predicate)
    data_reads = "(require-any " + " ".join(common_reads) + ")"
    metadata_reads = ("(require-any " + data_reads + " "
                      + alternatives(ancestors | auth_directories, metadata=True) + ")")
    writes = "(require-any " + " ".join(common_writes) + ")"
    rules = ["(version 1)", "(allow default)",
             f"(deny file-read-data file-read-xattr (require-not {data_reads}))",
             f"(deny file-read-metadata (require-not {metadata_reads}))",
             f"(deny file-write* (require-not {writes}))",
             f"(deny file-read* file-write* {alternatives(denied)})"]
    return "\n".join(rules) + "\n"


def _group_snapshot(pgid: int, uid: int) -> dict[str, Any]:
    """Observe the exact owned group, without process-name or shared-service kills."""
    try:
        result = subprocess.run(
            ["/bin/ps", "-axo", "pid=,ppid=,pgid=,uid=,stat=,lstart="],
            capture_output=True, text=True, timeout=2, check=False,
        )
        if result.returncode != 0:
            raise OSError("process table unavailable")
        members = []
        for line in result.stdout.splitlines():
            fields = line.split(None, 5)
            if len(fields) != 6:
                raise ValueError("incomplete process table row")
            pid, ppid, group, owner = map(int, fields[:4])
            if group == pgid:
                members.append({"pid": pid, "ppid": ppid, "pgid": group, "uid": owner,
                                "state": fields[4], "started": fields[5]})
        return {"observed": True, "sameOwner": all(member["uid"] == uid for member in members),
                "members": members,
                "runningPids": [member["pid"] for member in members if not member["state"].startswith("Z")]}
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return {"observed": False, "sameOwner": None, "members": None,
                "runningPids": None, "error": type(error).__name__}


def _supervise(
    command: list[str], *, cwd: Path, environment: dict[str, str],
    log_path: Path, business_deadline: float, cleanup_seconds: float,
    grace_seconds: float, receipt_path: Path | None = None,
) -> dict[str, Any]:
    """One owned session/group; leader exit alone never proves group cleanup.

    Process-table uncertainty remains unknown. Signals are restricted to the
    freshly created group after a same-UID membership observation. Descendants
    that create a different session/group are not claimed to have disappeared.
    """
    if cleanup_seconds < 0 or grace_seconds < 0:
        raise ValueError("cleanup/grace durations cannot be negative")
    receipt: dict[str, Any] = {
        "pid": None, "pgid": None, "uid": os.getuid(), "exitCode": None,
        "businessDeadlineReached": False, "terminated": False, "killed": False,
        "workerExitObserved": False, "spawnCount": 0, "elapsedSeconds": 0.0,
        "leaderCleanup": "not_started", "groupCleanup": "unknown",
        "groupOwnership": "not_started", "groupObservation": None,
        "groupObservations": [], "signals": [], "phase": "not_started",
    }
    started = time.monotonic()
    process: subprocess.Popen | None = None

    def persist() -> None:
        receipt["elapsedSeconds"] = round(time.monotonic() - started, 6)
        if receipt_path is not None:
            private_json(receipt_path, receipt)

    def observe() -> dict[str, Any]:
        assert process is not None
        process.poll()  # Reap our leader when possible, independently of children.
        receipt["exitCode"] = process.returncode
        receipt["workerExitObserved"] = process.returncode is not None
        receipt["leaderCleanup"] = "reaped" if process.returncode is not None else "running"
        snapshot = _group_snapshot(process.pid, receipt["uid"])
        receipt["groupObservation"] = snapshot
        # Record transitions, not every identical polling interval.
        if not receipt["groupObservations"] or snapshot != receipt["groupObservations"][-1]["observation"]:
            receipt["groupObservations"].append({"elapsedSeconds": round(time.monotonic() - started, 6),
                                                 "observation": snapshot})
        if snapshot["observed"] and snapshot["sameOwner"]:
            receipt["groupOwnership"] = "new_session_same_uid_observed"
        elif snapshot["observed"]:
            receipt["groupOwnership"] = "ownership_mismatch"
        return snapshot

    def settled(snapshot: dict[str, Any]) -> bool:
        return (snapshot["observed"] and snapshot["sameOwner"] is True
                and not snapshot["runningPids"] and receipt["workerExitObserved"])

    def wait_group(seconds: float) -> dict[str, Any]:
        end = time.monotonic() + seconds
        while True:
            snapshot = observe()
            if settled(snapshot) or time.monotonic() >= end:
                return snapshot
            time.sleep(min(0.05, max(0, end - time.monotonic())))

    def signal_owned(sig: signal.Signals) -> bool:
        assert process is not None
        snapshot = observe()
        leader_confirms_group = False
        if not snapshot["observed"] and process.returncode is None:
            try:
                leader_confirms_group = os.getpgid(process.pid) == process.pid
            except ProcessLookupError:
                pass
        if process.pid == os.getpgrp() or not (
            leader_confirms_group or (snapshot["observed"] and snapshot["sameOwner"] is True
                                      and snapshot["runningPids"])
        ):
            return False
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            receipt["signals"].append({"signal": sig.name, "sent": False, "reason": "group_not_found"})
            return False
        receipt["signals"].append({"signal": sig.name, "sent": True,
                                   "observedPids": snapshot["runningPids"],
                                   "ownershipBasis": "live_created_leader_pgid" if leader_confirms_group
                                                     else "new_session_same_uid_group_observation"})
        receipt["terminated" if sig == signal.SIGTERM else "killed"] = True
        persist()
        return True

    persist()
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as log:
            process = subprocess.Popen(
                command, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
            )
            receipt.update({"pid": process.pid, "pgid": process.pid, "spawnCount": 1,
                            "phase": "started", "leaderCleanup": "running",
                            "groupOwnership": "created_new_session"})
            persist()  # Trusted started evidence precedes any wait or result parsing.
            observe()
            try:
                process.wait(timeout=max(0.001, business_deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                receipt["businessDeadlineReached"] = True
                persist()
            cleanup_end = time.monotonic() + cleanup_seconds
            force_end = cleanup_end + grace_seconds
            kill_reserve = min(0.5, grace_seconds / 2)
            snapshot = wait_group(max(0, cleanup_end - time.monotonic()))
            if not settled(snapshot):
                signal_owned(signal.SIGTERM)
                snapshot = wait_group(max(0, force_end - kill_reserve - time.monotonic()))
            if not settled(snapshot):
                signal_owned(signal.SIGKILL)
                # Reserve final observation/reaping within the existing grace,
                # never append a second grace window to the frozen allocator.
                snapshot = wait_group(max(0, force_end - time.monotonic()))
            receipt["groupCleanup"] = "settled" if settled(snapshot) else "unknown"
            receipt["groupDisappearanceObserved"] = snapshot["observed"] and not snapshot["members"]
    except BaseException as error:
        receipt["supervisionError"] = {"type": type(error).__name__}
        if process is not None:
            # Cleanup on interruption follows the same observed-ownership policy.
            signal_owned(signal.SIGKILL)
            snapshot = wait_group(max(0.1, grace_seconds))
            receipt["groupCleanup"] = "settled" if settled(snapshot) else "unknown"
        raise
    finally:
        receipt["phase"] = "terminal"
        persist()
    return receipt


def run_fsq_worker(
    request: dict[str, Any], *, python: Path, worker_site: Path,
    private_dir: Path, oracle_roots: list[Path], process_receipt_path: Path,
    runtime_read_roots: list[Path], cleanup_seconds: float = 180, grace_seconds: float = 10,
    native_user_config_root: Path | None = None,
) -> dict[str, Any]:
    """Run native FSQ using explicit runtime reads and only owned writable roots.

    Required parent inputs: every canonical oracle/source-copy/result root,
    frozen native package/venv/base-Python/ADB read roots, and a trusted receipt
    path outside all worker writable roots. Native config/auth stays at the
    original native root (default ~/.fsq), with narrowly scoped writer grants.
    """
    sandbox = Path("/usr/bin/sandbox-exec")
    if not sandbox.is_file():
        raise RuntimeError("native FSQ worker requires the reviewed macOS sandbox")
    private_dir = private_dir.expanduser().resolve()
    workspace = Path(request["workspace"]).expanduser().resolve()
    output = Path(request["outputDir"]).expanduser().resolve()
    worker_site = worker_site.expanduser().resolve()
    process_receipt_path = process_receipt_path.expanduser().resolve()
    writable = [private_dir, workspace, output]
    if any(_inside(process_receipt_path, root) for root in writable):
        raise ValueError("trusted process receipt must be outside worker writable roots")
    if any(_overlap(worker_site, root) for root in writable):
        raise ValueError("staged worker modules must be outside worker writable roots")
    if any(_overlap(worker_site, root.expanduser().resolve()) for root in oracle_roots):
        raise ValueError("worker modules must be staged outside oracle trees")
    native_root = Path(request.get("userConfigRoot", Path.home() / ".fsq")).expanduser().resolve()
    if native_user_config_root is not None and native_user_config_root.expanduser().resolve() != native_root:
        raise ValueError("native auth policy root must match the unmodified native loader root")
    if _inside(process_receipt_path, native_root):
        raise ValueError("trusted process receipt must be outside native config/auth root")
    policy = sandbox_policy(
        [*oracle_roots, process_receipt_path], worker_root=private_dir,
        read_roots=[*runtime_read_roots, worker_site, python.absolute(), python.resolve()],
        write_roots=[workspace, output],
        native_user_config_root=native_root,
    )
    private_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    temporary_dir = private_dir / "tmp"
    temporary_dir.mkdir(mode=0o700)
    request_path = private_dir / "request.json"
    output_path = private_dir / "worker-result.json"
    policy_path = private_dir / "oracle-isolation.sb"
    private_json(request_path, request)
    descriptor = os.open(policy_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(policy)
    allowed_environment = (
        "HOME", "PATH", "LANG", "LC_ALL", "SSL_CERT_FILE", "SSL_CERT_DIR",
        "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY",
    )
    environment = {key: os.environ[key] for key in allowed_environment if key in os.environ}
    environment.update({"PYTHONPATH": str(worker_site), "PYTHONDONTWRITEBYTECODE": "1",
                        "TMPDIR": str(temporary_dir)})
    command = [str(sandbox), "-f", str(policy_path), str(python), "-B", "-m",
               "fsq_androidworld_eval.fsq_worker", "--request", str(request_path),
               "--output", str(output_path)]
    process = _supervise(
        command, cwd=workspace, environment=environment, log_path=private_dir / "worker.log",
        business_deadline=request["businessDeadlineMonotonic"], cleanup_seconds=cleanup_seconds,
        grace_seconds=grace_seconds, receipt_path=process_receipt_path,
    )
    # Persist independently even if a controlled supervisor adapter supplies the receipt.
    private_json(process_receipt_path, process)
    result: dict[str, Any] | None = None
    result_error: dict[str, str] | None = None
    result_reference = None
    try:
        if not output_path.is_file():
            result_error = {"type": "MissingWorkerResult", "reason": "no_worker_result"}
        else:
            if output_path.is_symlink():
                raise ValueError("FSQ worker result cannot be a symlink")
            result_reference = artifact_reference(output_path, private_dir)
            parsed = json.loads(output_path.read_text())
            if not isinstance(parsed, dict):
                raise ValueError("FSQ worker result must be an object")
            result = parsed
    except (OSError, ValueError) as error:
        result_error = {"type": type(error).__name__, "reason": "invalid_worker_result"}
    log_reference = None
    log_error = None
    try:
        log_reference = artifact_reference(private_dir / "worker.log", private_dir)
    except OSError as error:
        log_error = {"type": type(error).__name__, "reason": "unavailable_worker_log"}
    return {
        "process": process, "result": result, "resultError": result_error,
        "resultReference": result_reference,
        "logReference": log_reference, "logError": log_error,
        "sandboxSha256": hashlib.sha256(policy.encode()).hexdigest(),
        "completionEvidence": "worker_result_and_observed_exit" if result is not None and process["workerExitObserved"] else "no_complete_worker_result",
        "restoration": "not_provided_by_native_driver_close",
    }
