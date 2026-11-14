#!/usr/bin/env python3
"""Owned emulator lifecycle. No raw ADB path, shared recovery, or stop fallback.

The executable is also the emulator's -adb-path. All non-version CLI requests
cross SingleAttemptAdb and the same parent gateway used by preparation.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import datetime
import hashlib
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import socket
import stat
import threading
import time

# Direct -adb-path execution must import the frozen release, not an editable repo.
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _authorize(profile_path, *, cleanup=False):
    from fsq_androidworld_eval.fsq_runner import load_authorization
    profile_path = Path(profile_path).resolve()
    profile = json.loads(profile_path.read_text())
    manifest_path = Path(profile["manifestPath"])
    manifest = json.loads(manifest_path.read_text())
    auth = load_authorization(manifest_path, manifest, "prepare-apps", Path(profile["authorizationPath"]), cleanup=cleanup)
    binding = auth["parentController"]
    if (auth["approvedStages"] != ["prepare-apps"] or auth["effectsGrant"].get("ownedEmulatorLifecycle") is not True
            or auth.get("integrationOwner") != profile["integrationOwner"]
            or auth.get("executionOwner") != profile["executionOwner"]
            or binding["profiles"].get(str(profile_path)) != _hash(profile_path)
            or Path(binding["path"]).resolve() != Path(__file__).resolve()
            or binding["sha256"] != _hash(__file__)):
        raise PermissionError("Parent lifecycle is not bound to the finite preparation grant")
    target = manifest["target"]
    if (target["serial"] != "emulator-5560" or target["consolePort"] != 5560 or target["grpcPort"] != 8556
            or profile["adbPort"] != 5561 or profile["serverPort"] != 5037
            or profile["adbPath"] != target["adbPath"]
            or _hash(profile["adbPath"]) != profile["adbSha256"]
            or _hash(profile["emulatorPath"]) != profile["emulatorSha256"]):
        raise PermissionError("Parent emulator target or installed binary identity mismatch")
    headless = Path(profile["emulatorPath"]).parent / "qemu/darwin-aarch64/qemu-system-aarch64-headless"
    if (profile.get("headlessPath") != str(headless.resolve())
            or not isinstance(profile.get("headlessSha256"), str)
            or len(profile["headlessSha256"]) != 64):
        raise PermissionError("Exact installed headless executable pin is required")
    epoch = auth["resource"].get("adbServerIdentity", {})
    if type(epoch.get("pid")) is not int or epoch["pid"] <= 0 or not epoch.get("birthArgv"):
        raise PermissionError("Current shared ADB server identity is unknown")
    return profile, manifest, auth


@contextmanager
def _owned_adb_scope(profile_path, *, timeout, native_child=False):
    """Exclude parent SDK commands/close from SDK root/reconnect/verify."""
    profile, manifest, auth = _authorize(profile_path)
    authorization_sha = _hash(profile["authorizationPath"])
    profile_sha = _hash(profile_path)
    deadline = auth["resource"]["validUntilUnix"]
    if timeout is not None:
        deadline = min(deadline, time.time() + timeout)
    descriptor = None
    try:
        resource = json.loads(Path(profile["resourceReceiptPath"]).read_text())
        owner = resource.get("processIdentity")
        if (not isinstance(owner, dict) or resource.get("pid") != owner.get("pid")
                or _pid_identity(resource["pid"]) != owner
                or (native_child and os.getppid() != owner["pid"])):
            raise PermissionError("ADB scope is not bound to the owned emulator lifecycle")
        identity = {"authorizationSha256": authorization_sha, "profileSha256": profile_sha,
                    "ownerIdentity": owner, "serial": manifest["target"]["serial"]}
        path = Path(profile["resourceReceiptPath"]).with_name("owned-adb-transition.lock")
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise PermissionError("Owned ADB synchronization file identity is invalid")
        waiter = threading.Event()
        while True:
            if (Path(profile["failurePath"]).exists() or Path(profile["stopRequestedPath"]).exists()
                    or _hash(profile["authorizationPath"]) != authorization_sha
                    or _hash(profile_path) != profile_sha):
                raise PermissionError("Owned ADB scope grant or lifecycle changed while waiting")
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError("Owned ADB synchronization deadline expired")
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                # Timed lock contention only: no ADB command is retried.
                waiter.wait(min(0.05, remaining))
        current = path.stat(follow_symlinks=False)
        if ((info.st_dev, info.st_ino) != (current.st_dev, current.st_ino)
                or _pid_identity(resource["pid"]) != owner
                or _hash(profile["authorizationPath"]) != authorization_sha
                or _hash(profile_path) != profile_sha
                or Path(profile["failurePath"]).exists() or Path(profile["stopRequestedPath"]).exists()
                or time.time() >= deadline):
            raise PermissionError("Owned ADB lifecycle changed before lock admission")
        data = os.read(descriptor, 4097)
        if data:
            if len(data) > 4096 or json.loads(data) != identity:
                raise PermissionError("Owned ADB lock belongs to another grant or lifecycle")
        else:
            payload = json.dumps(identity, separators=(",", ":")).encode()
            if os.write(descriptor, payload) != len(payload):
                raise OSError("Incomplete owned ADB lock identity write")
        yield deadline
    except BaseException as error:
        _record_failure(profile, error)
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)  # Kernel releases this process's lock, also on exit.


def _write(path, value, *, exclusive=False):
    path = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC)
    with os.fdopen(os.open(path, flags, 0o600), "w") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _initialization_event(profile, operation, state, *, success=None, exit_code=None,
                          error_type=None, gateway_port=None):
    """Fixed initialization-only facts; never command bodies, outputs or messages."""
    path = profile.get("initializationEventsPath")
    if path is None:
        return
    observed_ns = time.monotonic_ns()
    observed_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    auth_bytes = Path(profile["authorizationPath"]).read_bytes()
    auth = json.loads(auth_bytes)
    auth_sha = hashlib.sha256(auth_bytes).hexdigest()
    if (auth_sha != os.environ.get("FSQ_EXPECTED_AUTHORIZATION_SHA256")
            or auth.get("purpose") not in {"root_overlay_initialization_diagnostic", "native_root_binding_22app_validation"}
            or os.environ.get("FSQ_INITIALIZATION_EVENTS") != path
            or auth["parentController"]["profiles"].get(profile["profilePath"]) != _hash(profile["profilePath"])):
        raise PermissionError("Initialization evidence is not bound to the exact diagnostic grant")
    if operation not in {"owned_boot", "parent_registration", "parent_overlay_list", "first_failure",
                          "sdk_whoami_before_root", "sdk_root", "sdk_whoami_verify"}:
        raise ValueError("Unknown initialization evidence operation")
    if state not in {"started", "forwarded", "returned", "failed", "recorded"}:
        raise ValueError("Unknown initialization evidence state")
    record = {"operation": operation, "state": state, "monotonicNs": observed_ns,
              "utc": observed_utc,
              "pid": os.getpid(), "parentPid": os.getppid(), "authorizationSha256": auth_sha,
              "gatewayPort": gateway_port, "success": success, "exitCode": exit_code,
              "errorType": error_type}
    payload = (json.dumps(record, ensure_ascii=True, separators=(",", ":")) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
    try:
        if os.write(descriptor, payload) != len(payload):
            raise OSError("Incomplete initialization evidence write")
    finally:
        os.close(descriptor)


def _record_failure(profile, error, *, gateway=None):
    from fsq_androidworld_eval.adb_gateway import first_gateway_failure, safe_diagnostic

    def describe(current):
        node = {"type": type(current).__name__, "message": safe_diagnostic(str(current))}
        if isinstance(current, BaseExceptionGroup):
            node["exceptions"] = [describe(child) for child in current.exceptions]
        return node

    refusal = first_gateway_failure(error)
    record = {"fatal": True, **describe(error)}
    if refusal is not None:
        record["gatewayFailure"] = refusal.evidence
    errors = []
    try:
        _write(profile["failurePath"], record, exclusive=True)
        _initialization_event(profile, "first_failure", "recorded",
                              exit_code=getattr(error, "returncode", None), error_type=type(error).__name__)
    except FileExistsError:
        pass  # The first failure remains authoritative, never overwritten.
    except BaseException as evidence_error:
        errors.append(evidence_error)
    # Physical forwarding is fenced even when evidence storage fails. This is
    # an owned gateway control frame, never a request to the shared daemon.
    try:
        if gateway is not None:
            gateway.latch()
        elif "FSQ_PARENT_ADB_GATEWAY" in os.environ:
            from fsq_androidworld_eval.adb_gateway import AdbGateway
            port = int(os.environ["FSQ_PARENT_ADB_GATEWAY"])
            if not 1 <= port <= 65535 or port == profile["serverPort"]:
                raise PermissionError("Fatal signal cannot target the shared daemon")
            with socket.create_connection(("127.0.0.1", port), timeout=2) as connection:
                AdbGateway._send_request(connection, b"fsq:halt")
                if AdbGateway._exact(connection, 4) != b"OKAY" or AdbGateway._request(connection) != b"latched":
                    raise RuntimeError("Parent gateway did not acknowledge the failure fence")
    except BaseException as signal_error:
        errors.append(signal_error)
    if errors:
        raise BaseExceptionGroup("Parent failure and failure-fence reporting failed", [error, *errors]) from None


def _pid_birth(pid):
    result = subprocess.run(["/bin/ps", "-p", str(pid), "-o", "pid=,lstart=,command="],
                            capture_output=True, text=True, timeout=5, check=True)
    return result.stdout.strip()


def _pid_identity(pid):
    result = subprocess.run(["/bin/ps", "-p", str(pid), "-o", "pid=,ppid=,lstart="],
                            capture_output=True, text=True, timeout=5, check=True)
    fields = result.stdout.split()
    if len(fields) != 7 or int(fields[0]) != pid:
        raise PermissionError("Cannot establish owned process PID/parent/birth")
    return {"pid": pid, "parentPid": int(fields[1]), "birth": " ".join(fields[2:])}


def _process_image(pid):
    """Darwin kernel executable and argv; never infer argument boundaries from ps."""
    library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    library.proc_pidpath.restype = ctypes.c_int
    path = ctypes.create_string_buffer(4096)
    if library.proc_pidpath(pid, path, len(path)) <= 0:
        raise OSError(ctypes.get_errno(), "proc_pidpath failed")
    kernel = ctypes.CDLL(None, use_errno=True)
    kernel.sysctl.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_uint, ctypes.c_void_p,
                             ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p, ctypes.c_size_t]
    kernel.sysctl.restype = ctypes.c_int
    mib = (ctypes.c_int * 3)(1, 49, pid)  # CTL_KERN, KERN_PROCARGS2, original child PID
    size = ctypes.c_size_t()
    if kernel.sysctl(mib, 3, None, ctypes.byref(size), None, 0) != 0:
        raise OSError(ctypes.get_errno(), "Cannot size original child argv")
    if not 4 < size.value <= 1024 * 1024:
        raise PermissionError("Invalid kernel argv size")
    data = ctypes.create_string_buffer(size.value)
    if kernel.sysctl(mib, 3, data, ctypes.byref(size), None, 0) != 0:
        raise OSError(ctypes.get_errno(), "Cannot read original child argv")
    raw = data.raw[:size.value]
    argc = int.from_bytes(raw[:4], sys.byteorder, signed=True)
    if not 0 < argc < 4096:
        raise PermissionError("Invalid kernel argc")
    cursor = raw.index(b"\0", 4) + 1  # Skip the executable path and its padding.
    while cursor < len(raw) and raw[cursor] == 0:
        cursor += 1
    argv = []
    for _ in range(argc):
        end = raw.index(b"\0", cursor)
        argv.append(os.fsdecode(raw[cursor:end]))
        cursor = end + 1
    executable = os.fsdecode(path.value)
    return {"executable": executable, "sha256": _hash(executable), "argv": argv}


def _listener_pids(port):
    result = subprocess.run(["/usr/sbin/lsof", "-nP", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"],
                            capture_output=True, text=True, timeout=5, check=False)
    if result.returncode not in (0, 1):
        raise RuntimeError("Cannot establish listener ownership")
    return {int(value) for value in result.stdout.split() if value.isdecimal()}


def launch_spec(profile, target, gateway_port):
    """Pure construction; actual port is allocated only after finite admission."""
    command = [profile["emulatorPath"], "-avd", "FSQMarkorSmoke33", "-port", "5560", "-grpc", "8556",
               "-cores", "2", "-memory", "2048", "-no-snapshot", "-no-window",
               "-camera-back", "emulated", "-camera-front", "none", "-adb-path", str(Path(__file__).resolve())]
    environment = dict(os.environ)
    environment.update({"ANDROID_ADB_SERVER_PORT": str(gateway_port),
                        "ADB_SERVER_SOCKET": f"tcp:127.0.0.1:{gateway_port}",
                        "FSQ_PARENT_ADB_GATEWAY": str(gateway_port),
                        "FSQ_EMULATOR_PROFILE": profile["profilePath"],
                        "PYTHONDONTWRITEBYTECODE": "1"})
    # /usr/bin/env python3 in -adb-path resolves to the existing evaluator venv.
    environment["PATH"] = str(Path(profile["evaluatorPython"]).parent) + os.pathsep + environment.get("PATH", "")
    return command, environment


class ParentResourceController:
    def __init__(self, profile_path):
        self.profile_path = str(Path(profile_path).resolve())
        self.gateway = None
        self.process = None
        self.identity = None
        self.command = None
        self.owner_pid = os.getpid()
        self._popen = None
        self.backend_seen = False
        self.last_identity = None
        self.boot_qualified = False
        self.failed = None
        self.start_attempted = False
        self.stop_attempted = False
        self.log = None
        self.profile = None
        self.authorization_sha = None


    def _stable_identity(self):
        if (os.getpid() != self.owner_pid or self.process is None or self.process is not self._popen
                or self.process.poll() is not None):
            raise PermissionError("Original owned Popen child is not live")
        current = _pid_identity(self.process.pid)
        if current != self.identity or current["parentPid"] != self.owner_pid:
            raise PermissionError("Owned emulator PID/parent/birth identity changed")
        return current

    def verify_identity(self, *, backend=False, ready=False):
        stable = self._stable_identity()
        image = _process_image(self.process.pid)
        launcher = self.profile["emulatorPath"]
        headless = self.profile["headlessPath"]
        pins = {launcher: self.profile["emulatorSha256"], headless: self.profile["headlessSha256"]}
        require_backend = backend or ready or self.backend_seen
        if (image["executable"] not in pins or image["sha256"] != pins[image["executable"]]
                or image["argv"][1:] != self.command[1:]
                or image["argv"][0] not in pins
                or (require_backend and (image["executable"] != headless or image["argv"][0] != headless))):
            raise PermissionError("Owned emulator executable/hash/argv identity mismatch")
        # Before readiness, the two kernel reads may straddle the one legal exec.
        # Once the complete backend image is observed, downgrade is forbidden.
        if image["executable"] == headless and image["argv"][0] == headless:
            self.backend_seen = True
        listeners = {str(port): sorted(_listener_pids(port)) for port in (5560, 5561, 8556)}
        if any(owners and owners != [self.process.pid] for owners in listeners.values()):
            raise PermissionError("Owned emulator listener belongs to another process")
        if (ready and any(owners != [self.process.pid] for owners in listeners.values())) or (
                backend and listeners["8556"] != [self.process.pid]):
            raise PermissionError("Owned emulator required listener is absent")
        self._stable_identity()
        self.last_identity = {**stable, **image, "listeners": listeners}
        return self.last_identity

    def _wait_for_backend(self, remaining):
        while self.process.poll() is None:
            remaining()
            self._stable_identity()
            owners = _listener_pids(8556)
            if owners:
                return self.verify_identity(backend=True)
            time.sleep(min(0.2, remaining()))
        return None

    def wait_until_booted(self, *, timeout=180):
        """Qualify this exact owned backend before any preparation consumer."""
        try:
            profile, manifest, auth = _authorize(self.profile_path)
            deadline = min(time.time() + timeout, auth["resource"]["validUntilUnix"])

            def remaining():
                if (_hash(profile["authorizationPath"]) != self.authorization_sha
                        or self.failed is not None or Path(profile["failurePath"]).exists()):
                    raise PermissionError("Owned boot grant changed or failure is latched")
                budget = deadline - time.time()
                if budget <= 0:
                    raise TimeoutError("Owned boot deadline expired")
                return budget

            if self._wait_for_backend(remaining) is None:
                raise RuntimeError("Owned emulator exited before boot")
            import grpc
            from google.protobuf.empty_pb2 import Empty
            from android_env.proto import emulator_controller_pb2_grpc as rpc
            with grpc.insecure_channel("127.0.0.1:8556") as channel:
                while True:
                    remaining()
                    proof = self.verify_identity(backend=True)
                    status = rpc.EmulatorControllerStub(channel).getStatus(Empty(), timeout=min(10, remaining()))
                    if status.booted:
                        proof = self.verify_identity(ready=True)
                        resource = json.loads(Path(profile["resourceReceiptPath"]).read_text())
                        resource.update({"status": "owned_boot_qualified", "identity": proof})
                        _write(profile["resourceReceiptPath"], resource)
                        self.boot_qualified = True
                        return proof
                    time.sleep(min(0.5, remaining()))
        except BaseException as error:
            self.failed = error
            _record_failure(self.profile, error, gateway=self.gateway)
            raise

    def start(self):
        assert not self.start_attempted, "Emulator creation is one attempt"
        self.start_attempted = True
        profile, manifest, auth = _authorize(self.profile_path)
        self.profile = profile
        authorization_sha = _hash(profile["authorizationPath"])
        self.authorization_sha = authorization_sha
        if Path(profile["failurePath"]).exists():
            raise PermissionError("Parent lifecycle has a latched failure")
        if Path(profile["stopRequestedPath"]).exists() or Path(profile["stopReceiptPath"]).exists():
            raise PermissionError("Parent lifecycle is stopping or closed")
        if profile.get("requiresSmokeReceipt"):
            smoke = json.loads(Path(profile["requiresSmokeReceipt"]).read_text())
            if smoke.get("status") != "closed" or smoke.get("bootQualified") is not True:
                raise PermissionError("Preparation requires the new successful owned lifecycle smoke")
        if _hash(profile["headlessPath"]) != profile["headlessSha256"]:
            raise PermissionError("Installed headless executable differs from the approved pin before creation")
        from fsq_androidworld_eval.adb_gateway import AdbGateway
        epoch = auth["resource"]["adbServerIdentity"]

        def same_server():
            return (not Path(profile["failurePath"]).exists()
                    and not Path(profile["stopRequestedPath"]).exists()
                    and _hash(profile["authorizationPath"]) == authorization_sha
                    and _listener_pids(profile["serverPort"]) == {epoch["pid"]}
                    and _pid_birth(epoch["pid"]) == epoch["birthArgv"]
                    and auth["resource"]["notBeforeUnix"] <= time.time() < auth["resource"]["validUntilUnix"])

        def failed(refusal):
            self.failed = refusal
            _record_failure(profile, self.failed, gateway=self.gateway)

        def registration_event(state, *, success=None):
            _initialization_event(profile, "parent_registration", state,
                                  success=success, gateway_port=self.gateway.port)

        def root_event():
            _initialization_event(profile, "sdk_root", "forwarded", gateway_port=self.gateway.port)

        try:
            self.gateway = AdbGateway(profile["serverPort"], manifest["target"]["serial"], failed,
                                      emulator_port=profile["adbPort"], upstream_identity=same_server,
                                      registration_event=registration_event if profile.get("initializationEventsPath") else None,
                                      root_event=root_event if profile.get("initializationEventsPath") else None)
            # Admit the actual existing daemon before creating a guest. Native
            # registration is rejected until this version+epoch proof succeeds.
            with socket.create_connection(("127.0.0.1", self.gateway.port), timeout=15) as connection:
                AdbGateway._send_request(connection, b"host:version")
                if AdbGateway._exact(connection, 4) != b"OKAY" or int(AdbGateway._request(connection), 16) != 41:
                    raise PermissionError("Existing ADB daemon version/epoch admission failed")
            command, environment = launch_spec(profile, manifest["target"], self.gateway.port)
            _write(profile["resourceReceiptPath"], {"status": "starting", "gatewayPort": self.gateway.port,
                   "argv": command, "environment": {key: environment[key] for key in
                   ("ANDROID_ADB_SERVER_PORT", "ADB_SERVER_SOCKET", "FSQ_PARENT_ADB_GATEWAY", "FSQ_EMULATOR_PROFILE")}}, exclusive=True)
            self.log = open(profile["emulatorLogPath"], "xb")
            _authorize(self.profile_path)
            if _hash(profile["authorizationPath"]) != authorization_sha:
                raise PermissionError("Parent grant changed before emulator creation")
            self.process = subprocess.Popen(command, env=environment, stdin=subprocess.DEVNULL,
                                            stdout=self.log, stderr=subprocess.STDOUT)
            self._popen = self.process
            self.command = command
            self.identity = _pid_identity(self.process.pid)
            self.verify_identity()
            _write(profile["resourceReceiptPath"], {"status": "started_not_boot_qualified", "pid": self.process.pid,
                   "processIdentity": self.identity, "identity": self.last_identity,
                   "gatewayPort": self.gateway.port, "argv": command,
                   "environment": {key: environment[key] for key in
                   ("ANDROID_ADB_SERVER_PORT", "ADB_SERVER_SOCKET", "FSQ_PARENT_ADB_GATEWAY", "FSQ_EMULATOR_PROFILE")}})
        except BaseException as error:
            self.failed = error
            errors = [error]
            try:
                _record_failure(profile, error, gateway=self.gateway)
            except BaseException as evidence_error:
                errors.append(evidence_error)
            # A returned child is retained for normal owned stop; never orphan it.
            if self.process is None:
                for resource in (self.gateway, self.log):
                    if resource is not None:
                        try:
                            resource.close()
                        except BaseException as cleanup_error:
                            errors.append(cleanup_error)
            if len(errors) > 1:
                raise BaseExceptionGroup("Parent start and cleanup failed", errors) from None
            raise

    def stop(self):
        assert self.process is not None and not self.stop_attempted, "Only one normal stop of the owned child"
        self.stop_attempted = True
        profile = self.profile
        shutdown_requested = False
        try:
            profile, manifest, auth = _authorize(self.profile_path, cleanup=True)
            if self.authorization_sha is None or _hash(profile["authorizationPath"]) != self.authorization_sha:
                raise PermissionError("Owned cleanup must retain the original start grant")
            cleanup_deadline = min(auth["resource"]["cleanupUntilUnix"], time.time() + 120)
            def remaining():
                if _hash(profile["authorizationPath"]) != self.authorization_sha:
                    raise PermissionError("Owned cleanup grant changed before dispatch")
                budget = cleanup_deadline - time.time()
                if budget <= 0:
                    raise PermissionError("Owned cleanup deadline expired before dispatch")
                return budget
            self.gateway.latch()
            _write(profile["stopRequestedPath"], {"normalOwnedCleanupRequested": True}, exclusive=True)
            if self._wait_for_backend(remaining) is not None:
                import grpc
                from android_env.proto import emulator_controller_pb2 as pb
                from android_env.proto import emulator_controller_pb2_grpc as rpc
                with grpc.insecure_channel("127.0.0.1:8556") as channel:
                    self.verify_identity(backend=True)
                    shutdown_requested = True
                    rpc.EmulatorControllerStub(channel).setVmState(
                        pb.VmRunState(state=pb.VmRunState.RunState.SHUTDOWN), timeout=min(10, remaining()))
            code = self.process.wait(timeout=min(60, remaining()))
            if code != 0:
                raise RuntimeError(f"Owned emulator exited abnormally: {code}")
            errors = []
            for resource in (self.gateway, self.log):
                try:
                    if resource is self.gateway:
                        resource.close(deadline=cleanup_deadline)
                    else:
                        resource.close()
                except BaseException as cleanup_error:
                    errors.append(cleanup_error)
            if errors:
                raise BaseExceptionGroup("Owned emulator host cleanup failed", errors)
            remaining()
            _write(profile["stopReceiptPath"], {"status": "closed", "pid": self.process.pid, "exitCode": code,
                   "channel": "127.0.0.1:8556 EmulatorController.setVmState(SHUTDOWN)" if shutdown_requested else "already_exited",
                   "shutdownRequested": shutdown_requested, "adbInvocations": 0, "identity": self.last_identity,
                   "bootQualified": self.boot_qualified,
                   "deviceRestored": False})
        except BaseException as error:
            self.failed = error
            if profile is not None:
                _record_failure(profile, error, gateway=self.gateway)
                _write(profile["stopReceiptPath"], {"status": "unknown", "error": str(error)[:4096], "deviceRestored": False})
            # Keep the gateway alive if child/cleanup is unknown. No forced stop,
            # no raw adb fallback, no false resource-release receipt.
            raise


def sdk_adb_cli(profile_path, arguments):
    profile, manifest, auth = _authorize(profile_path)
    args = list(arguments)
    port = int(os.environ["FSQ_PARENT_ADB_GATEWAY"])
    try:
        if Path(profile["failurePath"]).exists():
            raise PermissionError("Parent lifecycle has a latched failure")
        if Path(profile["stopRequestedPath"]).exists() or Path(profile["stopReceiptPath"]).exists():
            raise PermissionError("Parent lifecycle is stopping or closed")
        receipt = json.loads(Path(profile["resourceReceiptPath"]).read_text())
        if receipt["gatewayPort"] != port or port == profile["serverPort"] or not 1 <= port <= 65535:
            raise PermissionError("Parent ADB gateway endpoint mismatch")
        while args and args[0] in {"-s", "-P", "-H"}:
            flag, value = args[:2]
            expected = {"-s": "emulator-5560", "-P": str(port), "-H": "127.0.0.1"}[flag]
            if value != expected:
                raise PermissionError("Emulator attempted an ADB target/server override")
            del args[:2]
        if args == ["version"]:
            # Local metadata does not touch adbd or need the target-transition lock.
            return subprocess.run([profile["adbPath"], "version"], capture_output=True,
                                  timeout=10, check=True).stdout
        with _owned_adb_scope(profile_path, timeout=30, native_child=True) as deadline:
            from android_env.components import config_classes
            from fsq_androidworld_eval.android_transport import SingleAttemptAdb
            transport = SingleAttemptAdb(config_classes.AdbControllerConfig(
                adb_path=profile["adbPath"], device_name=manifest["target"]["serial"], adb_server_port=port))
            command_error = None
            try:
                if args == ["shell", "cmd", "overlay", "list"]:
                    return transport._initialization_command(args, "parent_overlay_list", timeout=deadline - time.time())
                return transport.execute_command(args, timeout=deadline - time.time())
            except BaseException as error:
                try:
                    _record_failure(profile, error)
                finally:
                    command_error = sys.exception()
                raise
            finally:
                try:
                    transport.close()
                except BaseException as close_error:
                    if command_error is not None:
                        raise BaseExceptionGroup("SDK command and transport close failed",
                                                 [command_error, close_error]) from None
                    raise
    except BaseException as error:
        _record_failure(profile, error)
        raise


if __name__ == "__main__":
    try:
        sys.stdout.buffer.write(sdk_adb_cli(os.environ["FSQ_EMULATOR_PROFILE"], sys.argv[1:]))
    except BaseException as error:
        print(f"Scoped emulator ADB denied: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)
