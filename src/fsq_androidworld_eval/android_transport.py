"""Project-local AndroidEnv composition; never recover the shared ADB server.

The pinned SDK has no controller factory argument. These narrow subclasses use
its simulator/parser seams instead of patching modules or installed sources.

Native `adb emu` ignores -P; scoped SMS uses the owned gateway RPC instead.
"""
from __future__ import annotations
from contextlib import nullcontext

import json
import os
import re
import shlex
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from android_env import environment as sdk_environment
from android_env.components import adb_call_parser, adb_controller, config_classes
from android_env.components import coordinator, device_settings, task_manager
from android_env.components import adb_log_stream
from android_env.components.simulators.emulator import emulator_simulator
from android_env.proto import adb_pb2, task_pb2
from android_env.wrappers import a11y_grpc_wrapper
from android_world.env import android_world_controller, interface
from fsq_androidworld_eval.adb_gateway import AdbGateway, AdbGatewayFailure, emulator_sms_command, safe_diagnostic


class AndroidTransportError(Exception):
    """Fatal for this environment, deliberately outside SDK retry error classes."""

    def __init__(self, kind: str, command: list[str], stdout: bytes | str = b"",
                 stderr: bytes | str = b"", returncode: int | None = None, *, gateway_failure=None):
        command = list(command)
        private_inputs = []
        if "shell" in command:
            start = command.index("shell")
            if command[start + 1:start + 3] == ["input", "text"]:
                private_inputs = command[start + 3:]
                command[start + 3:] = ["<redacted-input>"]
        if "emu" in command:
            start = command.index("emu")
            if command[start + 1:start + 3] == ["sms", "send"]:
                private_inputs += command[start + 3:]
                command[start + 3:] = ["<redacted-sms>"]
        def safe(value: bytes | str) -> str:
            text = value.decode("utf-8", "replace") if isinstance(value, bytes) else value
            for value in private_inputs:
                if value:
                    text = text.replace(value, "<redacted-input>")
            return safe_diagnostic(text)
        self.kind = kind
        self.returncode = returncode
        self.command = safe(shlex.join(command))
        self.stdout = safe(stdout)
        self.stderr = safe(stderr)
        self.gateway_failure = gateway_failure
        super().__init__(f"{kind}; exit={returncode}; command={self.command}; "
                         f"stdout={self.stdout!r}; stderr={self.stderr!r}"
                         + (f"; gateway={gateway_failure}" if gateway_failure is not None else ""))
        if gateway_failure is not None:
            self.__cause__ = gateway_failure


class SingleAttemptAdb(adb_controller.AdbController):
    """One fixed target, one subprocess per command, sticky first failure."""

    def __init__(self, config: config_classes.AdbControllerConfig):
        # Upstream __init__ deletes process-global environment variables and logs
        # the full environment. Keep configuration and child environment local.
        self._config = config
        parent_port = os.environ.get("FSQ_PARENT_ADB_GATEWAY")
        self._parent_gateway = parent_port is not None
        self._server_port = config.adb_server_port
        if parent_port is not None:
            if not parent_port.isdecimal() or not 1 <= int(parent_port) <= 65535 or int(parent_port) == 5037:
                raise AndroidTransportError("invalid_parent_gateway", [])
            self._server_port = int(parent_port)
        self._os_env_vars = dict(os.environ)
        self._os_env_vars.pop("ANDROID_HOME", None)
        self._os_env_vars.pop("ANDROID_ADB_SERVER_PORT", None)
        self._os_env_vars.pop("ADB_SERVER_SOCKET", None)
        self._lock = threading.RLock()
        self.failure: AndroidTransportError | None = None
        self._failure_lock = threading.Lock()
        self.launches: list[dict[str, Any]] = []
        self._gateway = None
        self._client_checked = False
        self._log_processes = set()
        self._initialization_profile = (os.environ.get("FSQ_EMULATOR_PROFILE", "")
                                        if os.environ.get("FSQ_INITIALIZATION_EVENTS") else None)

    def command_prefix(self, include_device_name: bool = True) -> list[str]:
        port = self._gateway.port if self._gateway is not None else self._server_port
        prefix = [self._config.adb_path, "-H", "127.0.0.1", "-P", str(port)]
        if include_device_name:
            prefix += ["-s", self._config.device_name]
        return prefix

    def _initialization_command(self, args, operation, *, timeout=None):
        if self._initialization_profile is None:
            return self.execute_command(args, timeout=timeout)
        from fsq_androidworld_eval.emulator_lifecycle import _initialization_event
        profile = json.loads(Path(self._initialization_profile).read_text())
        _initialization_event(profile, operation, "started",
                              gateway_port=self._gateway.port if self._gateway is not None else None)
        try:
            output = self.execute_command(args, timeout=timeout)
        except BaseException as error:
            try:
                _initialization_event(profile, operation, "failed",
                                      exit_code=getattr(error, "returncode", None), error_type=type(error).__name__,
                                      gateway_port=self._gateway.port if self._gateway is not None else None)
            except BaseException as evidence_error:
                raise BaseExceptionGroup("Initialization operation and evidence recording failed",
                                         [error, evidence_error]) from None
            raise
        identity = output.strip() == b"root" if operation in {"sdk_whoami_before_root", "sdk_whoami_verify"} else True
        _initialization_event(profile, operation, "returned", success=identity, exit_code=0,
                              gateway_port=self._gateway.port if self._gateway is not None else None)
        return output

    def _fail(self, kind: str, args: list[str], stdout=b"", stderr=b"", returncode=None):
        error = AndroidTransportError(kind, self.command_prefix() + args, stdout, stderr, returncode)
        with self._failure_lock:
            if self.failure is None:
                self.failure = error
        if self.failure.gateway_failure is not None:
            raise self.failure from self.failure.gateway_failure
        raise self.failure from None

    def check(self) -> None:
        if self.failure is not None:
            raise self.failure
        for process in tuple(self._log_processes):
            code = process.poll()
            if code is not None:
                self._fail("adb_logcat_exited", ["logcat"], returncode=code)

    def init_server(self, timeout: float | None = None):
        # No SDK devices/restart/init sequence. Require an existing daemon.
        self._require_server()
        self._prepare_client()

    def _require_server(self):
        self.check()
        try:
            with socket.create_connection(("127.0.0.1", self._server_port), timeout=1) as connection:
                if self._parent_gateway:
                    AdbGateway._send_request(connection, b"host:version")
                    if AdbGateway._exact(connection, 4) != b"OKAY" or int(AdbGateway._request(connection), 16) != 41:
                        self._fail("parent_gateway_rejected", [])
        except OSError as error:
            self._fail("adb_server_unavailable", [], stderr=str(error))

    def _gateway_failed(self, refusal: AdbGatewayFailure):
        with self._failure_lock:
            if self.failure is None:
                self.failure = AndroidTransportError("adb_gateway_" + refusal.evidence["cause"]["type"],
                                                     self.command_prefix(), gateway_failure=refusal)

    def _prepare_client(self):
        self.check()
        if not self._client_checked:
            try:
                version = subprocess.run([self._config.adb_path, "version"], capture_output=True,
                                         env=self._os_env_vars, timeout=10, check=False)
            except (OSError, subprocess.TimeoutExpired) as error:
                self._fail("adb_client_identity_failed", [], stderr=type(error).__name__)
            if version.returncode or not version.stdout.startswith(b"Android Debug Bridge version 1.0.41\n"):
                self._fail("unsupported_adb_protocol", [], version.stdout, version.stderr, version.returncode)
            self._client_checked = True
        if self._gateway is None:
            try:
                self._gateway = AdbGateway(self._server_port, self._config.device_name,
                                           self._gateway_failed, version=41,
                                           forward_emulator=self._parent_gateway)
            except Exception as error:
                self._fail("adb_gateway_start_failed", [], stderr=type(error).__name__)

    def close(self):
        if self._gateway is not None:
            self._gateway.close()
            self._gateway = None

    def _restart_server(self, timeout: float | None = None):
        self._fail("shared_server_recovery_forbidden", [])

    def _execute_emulator(self, args: list[str], timeout: float | None) -> bytes:
        # AOSP client/console.cpp opens the serial's console directly, ignoring
        # both -H and -P. Never invoke that CLI path, even after argv validation.
        deadline = time.time() + (self._config.default_timeout if timeout is None else timeout)

        def remaining():
            value = deadline - time.time()
            if value <= 0:
                raise TimeoutError("Scoped emulator RPC deadline expired")
            return value

        try:
            # Version admission must precede even a console-only first command.
            rpc = (b"fsq:emu:" + self._config.device_name.encode("ascii") + b":"
                   + json.dumps({"args": args[1:], "deadline": deadline}, ensure_ascii=True).encode("ascii"))
            if len(rpc) > 65535:
                raise ValueError("Scoped emulator RPC exceeds the ADB frame bound")
            for request in (b"host:version", rpc):
                with socket.create_connection(("127.0.0.1", self._gateway.port), timeout=remaining()) as connection:
                    connection.settimeout(remaining())
                    AdbGateway._send_request(connection, request)
                    status = AdbGateway._exact(connection, 4)
                    output = AdbGateway._request(connection)
                    if status != b"OKAY":
                        self.check()
                        self._fail("emulator_gateway_rejected", args)
                    if request == b"host:version" and output != b"0029":
                        self._fail("unsupported_adb_protocol", args)
            self.check()
            return output
        except TimeoutError:
            self._fail("adb_timeout", args)
        except (OSError, ValueError) as error:
            self._fail("emulator_gateway_failed", args, stderr=type(error).__name__)

    def execute_command(self, args: list[str], timeout: float | None = None,
                        device_specific: bool = True) -> bytes:
        with self._lock:
            self.check()
            args = list(args)
            if not device_specific or not args or args[0].startswith("-") or args[0] in {
                "kill-server", "start-server", "server", "devices", "reconnect", "connect", "disconnect",
                "fork-server", "nodaemon", "pair", "mdns",
            }:
                self._fail("unscoped_or_server_command_forbidden", args)
            if args[0] == "emu":
                try:
                    emulator_sms_command(args[1:])
                except (ValueError, UnicodeError):
                    self._fail("emulator_command_forbidden", args)
            self._require_server()
            self._prepare_client()
            if args[0] == "emu":
                return self._execute_emulator(args, timeout)
            try:
                result = subprocess.run(
                    self.command_prefix() + args, capture_output=True,
                    timeout=self._config.default_timeout if timeout is None else timeout,
                    env=self._os_env_vars, check=False,
                )
            except subprocess.TimeoutExpired as error:
                self._fail("adb_timeout", args, error.stdout or b"", error.stderr or b"")
            except OSError as error:
                self._fail("adb_spawn_failed", args, stderr=str(error))
            if result.returncode:
                self._fail("adb_nonzero", args, result.stdout, result.stderr, result.returncode)
            self.check()
            if args[:3] == ["shell", "am", "start"]:
                diagnostics = (result.stdout + b"\n" + result.stderr).decode("utf-8", "replace")
                if re.search(r"(?im)^\s*(?:Error\b|Exception\b|SecurityException\b|Activity not started|Status:\s*(?!ok\b)\S+)", diagnostics):
                    self._fail("activity_launch_failed", args, result.stdout, result.stderr, result.returncode)
            return result.stdout

    def launch(self, package: str, timeout: float | None = None) -> tuple[str, bytes]:
        with self._lock:
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+", package):
                self._fail("invalid_launch_package", [package])
            user_output = self.execute_command(["shell", "am", "get-current-user"], timeout)
            user = user_output.decode("utf-8", "replace").strip()
            if not user.isdecimal():
                self._fail("invalid_current_user", [], user_output)
            resolution = self.execute_command([
                "shell", "cmd", "package", "resolve-activity", "--brief", "--user", user,
                "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", package,
            ], timeout)
            components = [line.strip() for line in resolution.decode("utf-8", "replace").splitlines()
                          if re.fullmatch(re.escape(package) + r"/[A-Za-z0-9_.$]+", line.strip())]
            if len(components) != 1:
                self._fail("launcher_resolution_failed", [package], resolution)
            component = components[0]
            args = ["shell", "am", "start", "-W", "--user", user,
                    "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", "-n", component]
            output = self.execute_command(args, timeout)
            # am can exit zero while reporting framework launch failure. Existing
            # activity warnings are success, but an absent/failed Status is not.
            text = output.decode("utf-8", "replace")
            if re.search(r"(?im)^\s*(?:Error(?:\s+type\s+\d+)?\s*:|Exception|SecurityException|Status:\s*(?!ok\b)\S+)", text) or not re.search(r"(?im)^\s*Status:\s*ok\s*$", text):
                self._fail("activity_launch_failed", args, output)
            self.launches.append({"package": package, "user": int(user), "component": component})
            return component, output


class CheckedAdbParser(adb_call_parser.AdbCallParser):
    """Intercept launcher requests, not arbitrary Monkey programs or app intents."""

    def parse(self, request: adb_pb2.AdbRequest) -> adb_pb2.AdbResponse:
        self._adb_controller.check()
        kind = request.WhichOneof("command")
        package = None
        if kind == "generic":
            args = list(request.generic.args)
            if args[:2] == ["shell", "monkey"]:
                # Official setup has exactly this launch-only form. Never run
                # future Monkey event streams or silently interpret their flags.
                if (len(args) in {5, 6, 7} and args[2] == "-p"
                        and args[4:] in (["1"], ["-candroid.intent.category.LAUNCHER", "1"],
                                         ["-c", "android.intent.category.LAUNCHER", "1"])):
                    package = args[3]
                else:
                    self._adb_controller._fail("non_launch_monkey_forbidden", args)
        elif kind == "start_activity":
            launch = request.start_activity
            # launch_app uses a bare mapped activity. Extra arguments encode
            # caller intent and must retain the official parser's semantics.
            if not launch.extra_args and not launch.force_stop and "/" in launch.full_activity:
                package = launch.full_activity.split("/", 1)[0]
        if package is not None:
            component, output = self._adb_controller.launch(package, request.timeout_sec or None)
            response = adb_pb2.AdbResponse(status=adb_pb2.AdbResponse.Status.OK)
            if kind == "generic":
                response.generic.output = output
            else:
                response.start_activity.full_activity = component
                response.start_activity.output = output
            return response
        return super().parse(request)


class OwnedAdbLogStream(adb_log_stream.AdbLogStream):
    def __init__(self, transport: SingleAttemptAdb, verbose: bool):
        super().__init__(transport.command_prefix(), verbose)
        self.transport = transport
        self._adb_subprocess = None

    def _get_stream_output(self):
        self.transport.execute_command(["logcat", "-b", "all", "-c"], timeout=100)
        self.transport._require_server()
        try:
            self._adb_subprocess = subprocess.Popen(
                self.transport.command_prefix() + ["logcat", "-v", "epoch"] + self._filters,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                env=self.transport._os_env_vars,
            )
        except OSError as error:
            self.transport._fail("adb_logcat_spawn_failed", ["logcat"], stderr=str(error))
        self.transport._log_processes.add(self._adb_subprocess)
        return self._adb_subprocess.stdout

    def stop_stream(self):
        if self._adb_subprocess is not None:
            process = self._adb_subprocess
            previous_code = process.poll()
            unexpected = None
            if previous_code is not None:
                unexpected = AndroidTransportError("adb_logcat_exited", self.transport.command_prefix() + ["logcat"],
                                                   returncode=previous_code)
                with self.transport._failure_lock:
                    if self.transport.failure is None:
                        self.transport.failure = unexpected
            self.transport._log_processes.discard(process)
            if previous_code is None:
                process.terminate()
            process.wait(timeout=10)
            if process.stdout is not None:
                process.stdout.close()
            self._adb_subprocess = None
            if unexpected is not None:
                raise unexpected


class ExistingEmulator(emulator_simulator.EmulatorSimulator):
    def __init__(self, config, transport):
        self.transport = transport
        self._launcher = None
        self._channel = None
        self._interaction_thread = None
        self._streams: list[OwnedAdbLogStream] = []
        super().__init__(config)

    def create_adb_controller(self):
        return self.transport

    def create_log_stream(self):
        stream = OwnedAdbLogStream(self.transport, self._config.verbose_logs)
        self._streams.append(stream)
        return stream

    def close(self):
        errors = []
        for stream in self._streams:
            try:
                stream.stop_stream()
            except BaseException as error:
                errors.append(error)
        try:
            super().close()
        except BaseException as error:
            errors.append(error)
        if errors:
            raise BaseExceptionGroup("Simulator cleanup failed", errors)


class CheckedCoordinator(coordinator.Coordinator):
    def _create_adb_call_parser(self):
        return CheckedAdbParser(self._simulator.create_adb_controller())

    def _launch_simulator(self, max_retries=1):
        self._simulator.transport.check()
        return super()._launch_simulator(max_retries=1)


class LocalA11yWrapper(a11y_grpc_wrapper.A11yGrpcWrapper):
    def __init__(self, env, payload):
        self.payload = payload
        self._env = env
        self._server = None
        super().__init__(env, install_a11y_forwarding=True, start_a11y_service=True,
                         enable_a11y_tree_info=True, latest_a11y_info_only=True)

    def _install_a11y_forwarding_apk(self):
        request = adb_pb2.AdbRequest()
        request.install_apk.blob.contents = self.payload
        response = self.execute_adb_call(request)
        if response.status != adb_pb2.AdbResponse.Status.OK:
            raise AndroidTransportError("helper_install_failed", [], stderr=response.error_message)

    def close(self):
        failures = []
        if self._server is not None:
            try:
                if not self._server.stop(None).wait(timeout=10):
                    raise RuntimeError("Owned accessibility gRPC server did not stop")
            except BaseException as error:
                failures.append(error)
        try:
            self._env.close()
        except BaseException as error:
            failures.append(error)
        if failures:
            raise BaseExceptionGroup("Accessibility wrapper cleanup failed", failures)


def _build_backend(config, transport, payload):
    """Capture ownership before each constructor; independent cleanup on failure."""
    owners = []
    try:
        simulator = ExistingEmulator.__new__(ExistingEmulator)
        owners.append(simulator)
        simulator.__init__(config, transport)
        manager = task_manager.TaskManager(task_pb2.Task(id="default", name="Empty task", max_episode_sec=7200))
        coord = CheckedCoordinator.__new__(CheckedCoordinator)
        owners.append(coord)
        coord.__init__(simulator, manager, device_settings.DeviceSettings(simulator))
        raw = sdk_environment.AndroidEnv(simulator, coord, manager)
        owners.append(raw)
        wrapper = LocalA11yWrapper.__new__(LocalA11yWrapper)
        owners.append(wrapper)
        wrapper.__init__(raw, payload)
        wrapper.reset()
        return wrapper
    except BaseException as error:
        failures = [error]
        # These close methods are idempotent and do not send ADB commands.
        for owner in reversed(owners):
            try:
                owner.close()
            except BaseException as cleanup_error:
                failures.append(cleanup_error)
        if len(failures) > 1:
            raise BaseExceptionGroup("Environment construction and cleanup failed", failures) from None
        raise


class LocalAndroidWorldController(android_world_controller.AndroidWorldController):
    def __init__(self, config, payload):
        self.transport = SingleAttemptAdb(config.adb_controller)
        self._config = config
        self._payload = payload
        self._retired = []
        from fsq_androidworld_eval.emulator_lifecycle import _owned_adb_scope, _record_failure
        profile_path = os.environ.get("FSQ_EMULATOR_PROFILE") if self.transport._parent_gateway else None
        if self.transport._parent_gateway and not profile_path:
            raise PermissionError("Owned SDK root requires the bound parent lifecycle profile")
        scope = (_owned_adb_scope(profile_path, timeout=config.adb_controller.default_timeout)
                 if profile_path else nullcontext())
        with scope:
            try:
                # Registration/reconnect uses the gateway directly, never this lock.
                identity = self.transport._initialization_command(["shell", "whoami"], "sdk_whoami_before_root").strip()
                if identity != b"root":
                    self.transport._initialization_command(["root"], "sdk_root")
                    identity = self.transport._initialization_command(["shell", "whoami"], "sdk_whoami_verify").strip()
                if identity != b"root":
                    self.transport._fail("adb_root_not_established", ["shell", "whoami"])
            except BaseException as error:
                if profile_path:
                    try:
                        from fsq_androidworld_eval.emulator_lifecycle import _authorize
                        profile, _, _ = _authorize(profile_path)
                        _record_failure(profile, error)
                    except BaseException as reporting_error:
                        error = BaseExceptionGroup("Root transition and failure reporting failed", [error, reporting_error])
                try:
                    self.transport.close()
                except BaseException as cleanup_error:
                    raise BaseExceptionGroup("Root transition and gateway cleanup failed", [error, cleanup_error]) from None
                raise error
        try:
            self._env = _build_backend(config, self.transport, payload)
        except BaseException as error:
            try:
                self.transport.close()
            except BaseException as cleanup_error:
                raise BaseExceptionGroup("Construction and gateway cleanup failed", [error, cleanup_error]) from None
            raise
        self._original_env = self._env
        self._a11y_method = android_world_controller.A11yMethod.A11Y_FORWARDER_APP

    def refresh_env(self):
        self.transport.check()
        replacement = _build_backend(self._config, self.transport, self._payload)
        previous = self._env
        self._retired.append(previous)
        self._env = replacement
        previous.close()
        self._retired.remove(previous)

    def close(self):
        failures = []
        for owner in [self._env, *self._retired]:
            try:
                owner.close()
            except BaseException as error:
                failures.append(error)
        try:
            self.transport.close()
        except BaseException as error:
            failures.append(error)
        if failures:
            raise BaseExceptionGroup("Environment cleanup failed", failures)


def create_environment(console_port: int, adb_path: str, grpc_port: int, payload: bytes,
                       adb_server_port: int = 5037) -> interface.AsyncEnv:
    launcher = config_classes.EmulatorLauncherConfig(
        emulator_console_port=console_port, adb_port=console_port + 1, grpc_port=grpc_port,
    )
    config = config_classes.EmulatorConfig(
        emulator_launcher=launcher,
        adb_controller=config_classes.AdbControllerConfig(
            adb_path=adb_path, adb_server_port=adb_server_port, device_name=f"emulator-{console_port}",
        ),
    )
    return interface.AsyncAndroidEnv(LocalAndroidWorldController(config, payload))


def launch_package(controller, package: str, timeout: float = 30) -> tuple[str, bytes]:
    """Shared entry for setup probes outside the AndroidWorld request parser."""
    return controller.transport.launch(package, timeout)


def scoped_adb_output(adb_path: str, serial: str, *args: str,
                      server_port: int = 5037, timeout: float = 30) -> str:
    transport = SingleAttemptAdb(config_classes.AdbControllerConfig(
        adb_path=adb_path, device_name=serial, adb_server_port=server_port,
    ))
    try:
        output = transport.execute_command(list(args), timeout=timeout)
    except BaseException as error:
        try:
            transport.close()
        except BaseException as cleanup_error:
            raise BaseExceptionGroup("ADB probe and cleanup failed", [error, cleanup_error]) from None
        raise
    transport.close()
    return output.decode("utf-8", "replace").strip()
