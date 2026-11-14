"""Owned loopback gateway: ADB clients never connect directly to shared 5037.

ADB itself sends host:kill on a version mismatch. Reject it, global services,
other serials, and incompatible server versions before they reach the daemon.
A live listener returns FAIL on upstream loss, preventing client auto-start.
After successful target selection, FIN before any next-service header byte is
client cancellation, not shared-daemon failure. Partial frames remain fatal.
The private fsq:emu RPC admits only the official SMS lifecycle shape. Native
`adb emu` bypasses -P and opens the console itself, so SDK gateways forward this
bounded RPC to their parent; only the owning gateway authenticates the exact
serial's loopback console. host:emulator:<port> remains ADB registration only.
"""
from __future__ import annotations

import json
import math
import re
import traceback
import select
import socket
import threading
import time
from pathlib import Path


def safe_diagnostic(text):
    text = re.sub(r"(?im)(authorization|token|password|api[_-]?key|cookie)[\"']?[\t :=]+[^\r\n]*",
                  r"\1=<redacted>", str(text))
    text = re.sub(r"(?i)\bBearer\s+\S+", "Bearer <redacted>", text)
    return re.sub(r"\b(?:gh[pousr]_|sk-)[A-Za-z0-9_-]+", "<redacted>", text)[-2048:]


def _request_evidence(payload):
    if payload is None:
        return None
    # Host control fields are useful evidence; shell/sync/app data never is.
    public = rb"(?:host:(?:version|host-features|features|kill|devices|track-devices)|host:(?:transport|tport:serial):emulator-[0-9]+|host:transport-id:[0-9]+|host-serial:emulator-[0-9]+:(?:features|get-state|get-serialno|get-devpath)|host:emulator:[0-9]+)"
    exact = re.fullmatch(public, payload) is not None
    return {"value": payload.decode("ascii") if exact else "<redacted-service-payload>",
            "bytes": len(payload), "redacted": not exact}


class AdbGatewayFailure(Exception):
    """One safe consumer record, with the original exception retained privately.

    Do not put the raw exception in the printable cause chain: arbitrary callback
    exceptions can echo device input or credentials. Transport chains this safe
    exception instead, while original_cause retains the actual Python cause.
    """

    def __init__(self, error, branch, request, service, gateway):
        message = str(error)
        for payload in (request, service):
            if payload is not None and _request_evidence(payload)["redacted"]:
                message = message.replace(repr(payload), "<redacted-service-payload>")
                message = message.replace(payload.decode("utf-8", "replace"), "<redacted-service-payload>")
        self.original_cause = getattr(error, "gateway_original_cause", error)
        self.evidence = {"cause": {"type": type(error).__name__, "message": safe_diagnostic(message)},
                         "branch": getattr(error, "gateway_branch", branch),
                         "request": _request_evidence(request), "selectedService": _request_evidence(service),
                         "gateway": {"port": gateway.port, "upstreamPort": gateway.server_port,
                                     "serial": gateway.serial, "versionAdmitted": gateway.version_admitted},
                         "origin": [{"file": frame.filename, "line": frame.lineno, "function": frame.name}
                                    for frame in traceback.extract_tb(error.__traceback__)[-12:]]}
        if hasattr(error, "gateway_frame"):
            self.evidence["frame"] = error.gateway_frame
        super().__init__(json.dumps(self.evidence, ensure_ascii=True))


def _deny(branch, message):
    error = PermissionError(message)
    error.gateway_branch = branch
    raise error


def first_gateway_failure(error):
    """Find the first causal refusal in original group order, never implicit context."""
    pending = [error]
    seen = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        refusal = getattr(current, "gateway_failure", current)
        if isinstance(refusal, AdbGatewayFailure):
            return refusal
        if current.__cause__ is not None:
            pending.append(current.__cause__)
        if isinstance(current, BaseExceptionGroup):
            pending.extend(reversed(current.exceptions))
    return None


def _protocol_hex(value, field):
    try:
        return int(value, 16)
    except ValueError as original:
        public = ValueError("Invalid ADB " + field + " hexadecimal encoding")
        public.gateway_original_cause = original
        raise public from None


def emulator_sms_command(args):
    """Validate console argv before joining; never accept console programs."""
    if (not isinstance(args, list) or len(args) != 4 or args[:2] != ["sms", "send"]
            or any(not isinstance(value, str) or not value
                   or any(ord(char) < 32 or ord(char) == 127 or char == ";" for char in value)
                   for value in args)
            or re.fullmatch(r"\+?[0-9]{1,20}", args[2]) is None):
        raise ValueError("Only the scoped emulator SMS send shape is permitted")
    command = " ".join(args).encode("utf-8") + b"\n"
    if len(command) > 65535:
        raise ValueError("Scoped emulator SMS command is too large")
    return command


class AdbGateway:
    def __init__(self, server_port: int, serial: str, failed, version: int = 41,
                 emulator_port: int | None = None, upstream_identity=None, registration_event=None, root_event=None,
                 forward_emulator: bool = False):
        self.server_port = server_port
        self.serial = serial
        self.failed = failed
        self.version = version
        if emulator_port is not None and (not serial.startswith("emulator-") or emulator_port != int(serial[9:]) + 1):
            raise ValueError("ADB registration must match the exact emulator serial")
        self.emulator_port = emulator_port
        self.upstream_identity = upstream_identity
        self.registration_event = registration_event
        self.root_event = root_event
        self.forward_emulator = forward_emulator
        self.failure = None
        self.version_admitted = False
        # IDs are learned only from this serial's successful tport selection.
        # This gateway never adopts another upstream epoch; each forward still
        # passes its existing identity/deadline/failure admission.
        self._transport_ids = set()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._sockets = set()
        self._threads = set()
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._listener.bind(("127.0.0.1", 0))
            self._listener.listen()
            self._listener.settimeout(0.2)
            self.port = self._listener.getsockname()[1]
            self._acceptor = threading.Thread(target=self._accept, name="fsq-adb-gateway", daemon=True)
            self._acceptor.start()
        except BaseException:
            self._listener.close()
            raise

    @staticmethod
    def _exact(connection, count, *, allow_eof=False, direction=None, frame_part="fixed"):
        chunks = bytearray()
        while len(chunks) < count:
            data = connection.recv(count - len(chunks))
            if not data:
                if allow_eof and not chunks:
                    return None
                error = ConnectionError("ADB stream ended during handshake")
                error.gateway_frame = {"direction": direction, "part": frame_part,
                                       "expectedBytes": count, "receivedBytes": len(chunks)}
                raise error
            chunks.extend(data)
        return bytes(chunks)

    @classmethod
    def _request(cls, connection, *, allow_eof=False, direction=None):
        header = cls._exact(connection, 4, allow_eof=allow_eof,
                            direction=direction, frame_part="request_header")
        if header is None:
            return None
        count = _protocol_hex(header, "request length header")
        if count <= 0 or count > 65535:
            raise ValueError("Invalid ADB protocol request size")
        return cls._exact(connection, count, direction=direction, frame_part="request_payload")

    @staticmethod
    def _send_request(connection, payload):
        connection.sendall(f"{len(payload):04x}".encode() + payload)

    def latch(self):
        with self._lock:
            if self.failure is None:
                self.failure = "ExternalFailure"

    def _admit_locked(self):
        if self.upstream_identity is not None and not self.upstream_identity():
            _deny("upstream_identity", "Shared ADB admission changed or expired")
        if self._stop.is_set():
            raise ConnectionAbortedError("Owned gateway is closing")
        if self.failure is not None:
            _deny("latched_forward", "Owned gateway has a latched failure")

    def _forward_request(self, connection, payload):
        # Serialize first-request admission with close, not blocking connect.
        with self._lock:
            self._admit_locked()
            self._send_request(connection, payload)

    def _emulator_request(self, request):
        prefix = b"fsq:emu:" + self.serial.encode("ascii") + b":"
        if not request.startswith(prefix):
            _deny("emulator_target_filter", "Emulator RPC target differs from the owned serial")
        serial = re.fullmatch(r"emulator-([1-9][0-9]{0,4})", self.serial)
        if serial is None or not 1 <= int(serial[1]) <= 65535:
            _deny("emulator_target_filter", "Emulator RPC requires an exact console serial")
        try:
            payload = json.loads(request[len(prefix):])
        except (ValueError, UnicodeError):
            raise ValueError("Malformed scoped emulator RPC") from None
        if not isinstance(payload, dict) or set(payload) != {"args", "deadline"}:
            raise ValueError("Malformed scoped emulator RPC fields")
        deadline = payload["deadline"]
        if type(deadline) not in {int, float} or not math.isfinite(deadline):
            raise ValueError("Invalid scoped emulator RPC deadline")
        command = emulator_sms_command(payload["args"])
        return int(serial[1]), command, deadline

    def _emulator_remaining(self, deadline):
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("Scoped emulator RPC deadline expired")
        return min(10, remaining)

    def _console_sms(self, port, command, deadline):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with self._lock:
                self._admit_locked()
                connection.settimeout(self._emulator_remaining(deadline))
                self._sockets.add(connection)
            connection.connect(("127.0.0.1", port))
            pending = bytearray()

            def reply():
                response = bytearray()
                while len(response) < 65535:
                    end = pending.find(b"\n")
                    if end < 0:
                        budget = 65535 - len(response) - len(pending)
                        if budget <= 0:
                            raise ValueError("Emulator console response exceeds its bound")
                        with self._lock:
                            self._admit_locked()
                            connection.settimeout(self._emulator_remaining(deadline))
                        data = connection.recv(min(4096, budget))
                        if not data:
                            raise ConnectionError("Incomplete emulator console response")
                        pending.extend(data)
                        continue
                    line = bytes(pending[:end + 1])
                    del pending[:end + 1]
                    response.extend(line)
                    status = line.rstrip(b"\r\n")
                    if status == b"OK":
                        return bytes(response)
                    if status == b"KO" or status.startswith(b"KO:"):
                        raise ConnectionError("Emulator console rejected scoped operation")
                raise ValueError("Emulator console response exceeds its bound")

            def send(payload):
                with self._lock:
                    self._admit_locked()
                    connection.settimeout(self._emulator_remaining(deadline))
                    connection.sendall(payload)

            greeting = reply()
            if b"Android Console:" not in greeting:
                raise ConnectionError("Unexpected emulator console greeting")
            if b"Authentication required" in greeting:
                # Never trust a token path supplied by the socket peer.
                with (Path.home() / ".emulator_console_auth_token").open("rb") as token_file:
                    token = token_file.read(4097).strip()
                if re.fullmatch(rb"[A-Za-z0-9+/=_-]{1,4096}", token) is None:
                    raise ValueError("Invalid local emulator console authentication token")
                send(b"auth " + token + b"\n")
                reply()
            send(command)
            response = reply()
            with self._lock:
                self._admit_locked()
                self._emulator_remaining(deadline)
            return response
        finally:
            with self._lock:
                self._sockets.discard(connection)
            connection.close()

    def _accept(self):
        while not self._stop.is_set():
            try:
                client, _ = self._listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with self._lock:
                if self._stop.is_set():
                    client.close()
                    break
                self._sockets.add(client)
                worker = threading.Thread(target=self._serve, args=(client,), name="fsq-adb-client", daemon=True)
                self._threads.add(worker)
                worker.start()

    def _serve(self, client):
        upstream = None
        request = service = None
        branch = "read_host_request"
        try:
            client.settimeout(10)
            request = self._request(client)
            if request == b"fsq:halt":
                self.latch()
                client.sendall(b"OKAY")
                self._send_request(client, b"latched")
                return
            if (self.emulator_port is not None or self.upstream_identity is not None) and request != b"host:version" and not self.version_admitted:
                _deny("version_admission", "Upstream version admission is required before parent requests")
            emulator = None
            if request.startswith(b"fsq:emu:"):
                branch = "emulator_rpc_filter"
                if not self.version_admitted:
                    _deny("version_admission", "Emulator RPC requires upstream version admission")
                emulator = self._emulator_request(request)
                self._emulator_remaining(emulator[2])
                if not self.forward_emulator:
                    branch = "emulator_console"
                    response = self._console_sms(*emulator)
                    client.settimeout(self._emulator_remaining(emulator[2]))
                    client.sendall(b"OKAY")
                    self._send_request(client, response)
                    return
            target = self.serial.encode("ascii")
            transports = (b"host:transport:" + target, b"host:tport:serial:" + target)
            read_services = {b"host:version", b"host:host-features", b"host-serial:" + target + b":features",
                             b"host-serial:" + target + b":get-state", b"host-serial:" + target + b":get-serialno",
                             b"host-serial:" + target + b":get-devpath",
                             b"host-serial:" + target + b":wait-for-any-device"}
            if self.emulator_port is not None:
                read_services.add(f"host:emulator:{self.emulator_port}".encode("ascii"))
            disconnect = re.fullmatch(rb"host-transport-id:([0-9]{1,20}):wait-for-any-disconnect", request)
            with self._lock:
                scoped_disconnect = disconnect is not None and int(disconnect[1]) in self._transport_ids
            if emulator is None and request not in read_services and request not in transports and not scoped_disconnect:
                _deny("host_service_filter", "Unscoped ADB host service rejected")
            branch = "connect_upstream"
            upstream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream.settimeout(10 if emulator is None else self._emulator_remaining(emulator[2]))
            with self._lock:
                if self.failure is not None:
                    _deny("latched_connect", "Owned gateway has a latched failure")
                if self._stop.is_set():
                    raise ConnectionAbortedError("Owned gateway is closing")
                self._sockets.add(upstream)
            upstream.connect(("127.0.0.1", self.server_port))
            if emulator is not None:
                upstream.settimeout(self._emulator_remaining(emulator[2]))
            branch = "forward_host_request"
            self._forward_request(upstream, request)
            if emulator is not None:
                branch = "emulator_parent_reply"
                status = self._exact(upstream, 4, direction="upstream", frame_part="status")
                response = self._request(upstream, direction="upstream")
                if status != b"OKAY":
                    raise ConnectionError("Parent gateway rejected scoped emulator RPC")
                client.settimeout(self._emulator_remaining(emulator[2]))
                client.sendall(status)
                self._send_request(client, response)
                return
            registration_header = None
            if (self.registration_event is not None and self.emulator_port is not None
                    and request == f"host:emulator:{self.emulator_port}".encode("ascii")):
                registration_header = bytearray()
                self.registration_event("forwarded")
            if request == b"host:version":
                branch = "read_upstream_version"
                status = self._exact(upstream, 4, direction="upstream", frame_part="status")
                if status != b"OKAY":
                    raise ConnectionError("Shared ADB server did not return its protocol version")
                version = self._request(upstream, direction="upstream")
                if _protocol_hex(version, "protocol version") != self.version:
                    raise ConnectionError("Shared ADB protocol version differs from pinned client")
                self.version_admitted = True
                client.sendall(status)
                self._send_request(client, version)
                return
            if request in transports:
                branch = "select_target"
                status = self._exact(upstream, 4, direction="upstream", frame_part="status")
                client.sendall(status)
                if status != b"OKAY":
                    # Forward the original bounded device-selection error.
                    self._send_request(client, self._request(upstream, direction="upstream"))
                    return
                if request == transports[1]:
                    transport_bytes = self._exact(upstream, 8, direction="upstream", frame_part="transport_id")
                    transport_id = int.from_bytes(transport_bytes, "little")
                    if transport_id == 0:
                        raise ConnectionError("Selected target returned an invalid zero transport ID")
                    with self._lock:
                        self._transport_ids.add(transport_id)
                    client.sendall(transport_bytes)
                branch = "read_selected_service"
                # Selection is complete; the client may close without sending a
                # service. Only FIN before any new header byte is cancellation.
                # Partial frames, resets and all upstream reads remain fatal.
                service = self._request(client, allow_eof=True, direction="client")
                if service is None:
                    return
                if service.startswith(b"host"):
                    _deny("selected_service_filter", "ADB host service after target selection rejected")
                branch = "forward_selected_service"
                self._forward_request(upstream, service)
                if service == b"root:" and self.root_event is not None:
                    self.root_event()
            branch = "proxy_stream"
            client.settimeout(None)
            upstream.settimeout(None)
            readers = [client, upstream]
            while readers and not self._stop.is_set():
                ready, _, _ = select.select(readers, [], [], 0.2)
                for source in ready:
                    try:
                        data = source.recv(65536)
                    except ConnectionResetError:
                        if source is client:
                            return  # Native logcat stop cancels its client stream.
                        raise
                    destination = upstream if source is client else client
                    if not data:
                        # FIN ends only this read direction. The peer may still
                        # have response bytes or client control frames to drain.
                        readers.remove(source)
                        try:
                            destination.shutdown(socket.SHUT_WR)
                        except (BrokenPipeError, ConnectionResetError):
                            if destination is client:
                                return
                            raise
                        continue
                    if registration_header is not None and source is upstream and len(registration_header) < 4:
                        registration_header.extend(data[:4 - len(registration_header)])
                        if len(registration_header) == 4:
                            self.registration_event("returned", success=registration_header == b"OKAY")
                    try:
                        destination.sendall(data)
                    except (BrokenPipeError, ConnectionResetError):
                        if destination is client:
                            return
                        raise
        except Exception as error:
            if not self._stop.is_set():
                first = False
                with self._lock:
                    if self.failure is None:
                        self.failure = AdbGatewayFailure(error, branch, request, service, self)
                        first = True
                # Only the first causal refusal may publish. Later cached/fence
                # failures cannot replace it or trigger another callback.
                if first:
                    self.failed(self.failure)
                message = b"FSQ scoped ADB gateway rejected request or upstream unavailable"
                try:
                    client.sendall(b"FAIL" + f"{len(message):04x}".encode() + message)
                except OSError:
                    pass
        finally:
            for connection in (client, upstream):
                if connection is not None:
                    with self._lock:
                        self._sockets.discard(connection)
                    connection.close()
            with self._lock:
                self._threads.discard(threading.current_thread())

    def close(self, *, deadline: float | None = None):
        with self._lock:
            self._stop.set()
            sockets = list(self._sockets)
            threads = list(self._threads)
        self._listener.close()
        for connection in sockets:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()
        def join_timeout():
            return 2 if deadline is None else max(0, min(2, deadline - time.time()))
        self._acceptor.join(timeout=join_timeout())
        for worker in threads:
            worker.join(timeout=join_timeout())
        if self._acceptor.is_alive() or any(worker.is_alive() for worker in threads):
            raise RuntimeError("Owned ADB gateway did not close")
