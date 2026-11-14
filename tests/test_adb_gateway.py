import socket
import threading
from contextlib import contextmanager
import json
import time

import pytest

from fsq_androidworld_eval.adb_gateway import AdbGateway


@contextmanager
def upstream(handler):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.settimeout(0.1)
    stopped = threading.Event()
    seen = []
    errors = []
    def serve():
        while not stopped.is_set():
            try:
                connection, _ = listener.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                with connection:
                    connection.settimeout(2)
                    request = AdbGateway._request(connection)
                    seen.append(request)
                    handler(connection, request)
            except BaseException as error:
                errors.append(error)
    worker = threading.Thread(target=serve)
    worker.start()
    try:
        yield listener.getsockname()[1], seen
    finally:
        stopped.set()
        listener.close()
        worker.join(timeout=3)
        assert not worker.is_alive()
        assert errors == []


def exchange(port, request):
    with socket.create_connection(("127.0.0.1", port), timeout=2) as connection:
        AdbGateway._send_request(connection, request)
        status = AdbGateway._exact(connection, 4)
        payload = AdbGateway._request(connection)
        return status, payload


@pytest.mark.parametrize("service", [b"host:kill", b"host:devices", b"host:transport:emulator-5554", b"host-serial:emulator-5554:features"])
def test_forbidden_host_service_never_reaches_upstream(service):
    failures = []
    with upstream(lambda connection, request: None) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failures.append)
        try:
            status, error = exchange(gateway.port, service)
            assert status == b"FAIL"
            assert seen == []
            assert len(failures) == 1 and isinstance(failures[0].original_cause, PermissionError)
        finally:
            gateway.close()


@pytest.mark.parametrize("version,accepted", [(b"0029", True), (b"0028", False)])
def test_protocol_mismatch_is_failure_not_client_kill_trigger(version, accepted):
    def handler(connection, request):
        connection.sendall(b"OKAY")
        AdbGateway._send_request(connection, version)
    failures = []
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failures.append)
        try:
            status, output = exchange(gateway.port, b"host:version")
            assert status == (b"OKAY" if accepted else b"FAIL")
            if accepted:
                assert output == version
            assert seen == [b"host:version"]
            assert failures == [] if accepted else isinstance(failures[0].original_cause, ConnectionError)
        finally:
            gateway.close()


def test_upstream_loss_returns_failure_while_owned_listener_stays_live():
    absent = socket.socket()
    absent.bind(("127.0.0.1", 0))
    port = absent.getsockname()[1]
    absent.close()
    failures = []
    gateway = AdbGateway(port, "emulator-5560", failures.append)
    try:
        assert exchange(gateway.port, b"host:version")[0] == b"FAIL"
        assert len(failures) == 1 and isinstance(failures[0].original_cause, ConnectionRefusedError)
    finally:
        gateway.close()


def test_selected_target_service_and_payload_roundtrip():
    def handler(connection, request):
        assert request == b"host:tport:serial:emulator-5560"
        connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
        service = AdbGateway._request(connection)
        assert service == b"shell,v2,raw:printf evidence"
        connection.sendall(b"OKAY" + b"original bytes")
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", lambda error: pytest.fail(str(error)))
        try:
            with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as connection:
                AdbGateway._send_request(connection, b"host:tport:serial:emulator-5560")
                assert AdbGateway._exact(connection, 12) == b"OKAY" + (7).to_bytes(8, "little")
                AdbGateway._send_request(connection, b"shell,v2,raw:printf evidence")
                assert AdbGateway._exact(connection, 18) == b"OKAYoriginal bytes"
        finally:
            gateway.close()


def test_failed_gateway_thread_start_releases_bound_listener(monkeypatch):
    sockets = []
    real_socket = socket.socket
    def create(*args, **kwargs):
        connection = real_socket(*args, **kwargs)
        sockets.append(connection)
        return connection
    def fail(thread):
        raise RuntimeError("thread startup failed")
    monkeypatch.setattr(socket, "socket", create)
    monkeypatch.setattr(threading.Thread, "start", fail)
    with pytest.raises(RuntimeError, match="thread startup failed"):
        AdbGateway(5037, "emulator-5560", lambda kind: None)
    assert len(sockets) == 1 and sockets[0].fileno() == -1


def test_close_owns_connecting_socket_and_blocks_late_forward(monkeypatch):
    connecting = threading.Event()
    interrupted = threading.Event()
    forwarded = []
    real_socket = socket.socket
    class ConnectingSocket(real_socket):
        blocked = False
        def connect(self, address):
            if address[1] == 1:
                self.blocked = True
                connecting.set()
                assert interrupted.wait(3)
                return
            return super().connect(address)
        def shutdown(self, how):
            if self.blocked:
                interrupted.set()
            return super().shutdown(how)
        def close(self):
            if self.blocked:
                interrupted.set()
            return super().close()
        def sendall(self, data, *args):
            if self.blocked:
                forwarded.append(data)
            return super().sendall(data, *args)
    monkeypatch.setattr(socket, "socket", ConnectingSocket)
    gateway = AdbGateway(1, "emulator-5560", lambda kind: None)
    try:
        with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
            AdbGateway._send_request(client, b"host:version")
            assert connecting.wait(2)
            gateway.close()
            assert interrupted.is_set() and forwarded == []
            assert not gateway._sockets and not gateway._threads
    finally:
        gateway.close()


@pytest.mark.parametrize("registration,requested,allowed", [(5561, 5561, True), (5561, 5555, False), (None, 5561, False)])
def test_parent_registration_is_exact_and_not_available_to_sdk_gateway(registration, requested, allowed):
    def handler(connection, service):
        connection.sendall(b"OKAY")
        AdbGateway._send_request(connection, b"0029" if service == b"host:version" else b"registered")
    failures = []
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failures.append, emulator_port=registration)
        try:
            assert exchange(gateway.port, b"host:version") == (b"OKAY", b"0029")
            status, payload = exchange(gateway.port, f"host:emulator:{requested}".encode())
            assert status == (b"OKAY" if allowed else b"FAIL")
            assert seen == [b"host:version"] + ([b"host:emulator:5561"] if allowed else [])
        finally:
            gateway.close()


def test_changed_upstream_epoch_sends_no_request_and_latches():
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.settimeout(2)
    received = []
    def receive():
        connection, _ = listener.accept()
        with connection:
            connection.settimeout(2)
            received.append(connection.recv(1))
    worker = threading.Thread(target=receive)
    worker.start()
    failures = []
    gateway = AdbGateway(listener.getsockname()[1], "emulator-5560", failures.append, upstream_identity=lambda: False)
    try:
        assert exchange(gateway.port, b"host:version")[0] == b"FAIL"
        worker.join(timeout=3)
        assert not worker.is_alive() and received == [b""]
        assert exchange(gateway.port, b"host:version")[0] == b"FAIL"
        assert isinstance(gateway.failure.original_cause, PermissionError)
        assert len(failures) == 1
    finally:
        gateway.close()
        listener.close()
        worker.join(timeout=3)


def test_parent_registration_without_version_admission_never_reaches_upstream():
    with upstream(lambda connection, service: None) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", lambda kind: None, emulator_port=5561)
        try:
            assert exchange(gateway.port, b"host:emulator:5561")[0] == b"FAIL"
            assert seen == [] and isinstance(gateway.failure.original_cause, PermissionError)
        finally:
            gateway.close()


def test_owned_halt_fences_registration_without_forwarding_control_frame():
    def handler(connection, service):
        connection.sendall(b"OKAY")
        AdbGateway._send_request(connection, b"0029")
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", lambda kind: None, emulator_port=5561)
        try:
            assert exchange(gateway.port, b"host:version") == (b"OKAY", b"0029")
            assert exchange(gateway.port, b"fsq:halt") == (b"OKAY", b"latched")
            assert exchange(gateway.port, b"host:emulator:5561")[0] == b"FAIL"
            assert seen == [b"host:version"] and gateway.failure == "ExternalFailure"
        finally:
            gateway.close()


@pytest.mark.parametrize("field", ["header", "version"])
def test_unlabelled_malformed_protocol_bytes_remain_private(tmp_path, field):
    import traceback
    from fsq_androidworld_eval import emulator_lifecycle

    secret = b"PRIV" if field == "header" else b"unlabelled-private-raw-value"
    def handler(connection, request):
        connection.sendall(b"OKAY")
        AdbGateway._send_request(connection, secret)

    failures = []
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failures.append)
        try:
            if field == "header":
                with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
                    client.sendall(secret)
                    assert AdbGateway._exact(client, 4) == b"FAIL"
            else:
                assert exchange(gateway.port, b"host:version")[0] == b"FAIL"
            refusal = failures[0]
            assert isinstance(refusal.original_cause, ValueError)
            assert secret.decode() in str(refusal.original_cause)
            path = tmp_path / "first.json"
            emulator_lifecycle._record_failure({"failurePath": str(path)}, refusal, gateway=gateway)
            public = path.read_text() + "".join(traceback.format_exception(refusal))
            assert secret.decode() not in public
            assert refusal.evidence["branch"] == ("read_host_request" if field == "header" else "read_upstream_version")
        finally:
            gateway.close()


@pytest.mark.parametrize("wait_request,selected,allowed", [
    (b"host-transport-id:7:wait-for-any-disconnect", True, True),
    (b"host-transport-id:8:wait-for-any-disconnect", True, False),
    (b"host-transport-id:7:wait-for-any-disconnect", False, False),
    (b"host-transport-id:7:features", True, False),
    (b"host-serial:emulator-5560:wait-for-any-device", False, True),
    (b"host-serial:emulator-5554:wait-for-any-device", True, False),
    (b"host:wait-for-any-device", True, False),
])
def test_native_root_waits_require_target_serial_or_admitted_transport_id(wait_request, selected, allowed):
    failures = []
    def handler(connection, service):
        if service == b"host:tport:serial:emulator-5560":
            connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
            assert AdbGateway._request(connection) == b"root:"
            connection.sendall(b"OKAY")
        else:
            assert service in {b"host-transport-id:7:wait-for-any-disconnect", b"host-serial:emulator-5560:wait-for-any-device"}
            connection.sendall(b"OKAYOKAY")
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failures.append)
        try:
            if selected:
                with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
                    AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
                    assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
                    AdbGateway._send_request(client, b"root:")
                    assert AdbGateway._exact(client, 4) == b"OKAY"
            with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
                AdbGateway._send_request(client, wait_request)
                assert AdbGateway._exact(client, 4) == (b"OKAY" if allowed else b"FAIL")
                if allowed:
                    assert AdbGateway._exact(client, 4) == b"OKAY"
            assert (wait_request in seen) is allowed
            assert bool(failures) is not allowed
        finally:
            gateway.close()


def test_learned_target_transport_id_does_not_bypass_changed_daemon_epoch():
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.settimeout(3)
    valid = [True]
    observed = []
    errors = []
    def peer():
        try:
            with listener.accept()[0] as connection:
                observed.append(AdbGateway._request(connection))
                connection.sendall(b"OKAY")
                AdbGateway._send_request(connection, b"0029")
            with listener.accept()[0] as connection:
                observed.append(AdbGateway._request(connection))
                connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
                assert AdbGateway._request(connection) == b"root:"
                connection.sendall(b"OKAY")
            with listener.accept()[0] as connection:
                connection.settimeout(2)
                observed.append(connection.recv(4))
        except BaseException as error:
            errors.append(error)
    worker = threading.Thread(target=peer)
    worker.start()
    failures = []
    gateway = AdbGateway(listener.getsockname()[1], "emulator-5560", failures.append, upstream_identity=lambda: valid[0])
    try:
        assert exchange(gateway.port, b"host:version") == (b"OKAY", b"0029")
        with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
            AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
            assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
            AdbGateway._send_request(client, b"root:")
            assert AdbGateway._exact(client, 4) == b"OKAY"
        valid[0] = False
        assert exchange(gateway.port, b"host-transport-id:7:wait-for-any-disconnect")[0] == b"FAIL"
        worker.join(timeout=3)
        assert not worker.is_alive() and not errors
        assert observed == [b"host:version", b"host:tport:serial:emulator-5560", b""]
        assert failures[0].evidence["branch"] == "upstream_identity"
    finally:
        gateway.close()
        listener.close()
        worker.join(timeout=3)


def test_admitted_client_stream_reset_closes_without_latching_admission_failure():
    import struct
    closed = threading.Event()
    failures = []
    def handler(connection, service):
        connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
        assert AdbGateway._request(connection) == b"shell:logcat"
        connection.sendall(b"OKAY")
        assert connection.recv(1) == b""
        closed.set()
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failures.append)
        try:
            client = socket.create_connection(("127.0.0.1", gateway.port), timeout=2)
            AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
            assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
            AdbGateway._send_request(client, b"shell:logcat")
            assert AdbGateway._exact(client, 4) == b"OKAY"
            client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
            client.close()
            assert closed.wait(3)
            assert gateway.failure is None and failures == []
        finally:
            gateway.close()


def test_upstream_stream_reset_remains_a_fatal_gateway_failure():
    import struct
    reset = threading.Event()
    failed = threading.Event()
    failures = []
    def handler(connection, service):
        connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
        assert AdbGateway._request(connection) == b"shell:logcat"
        connection.sendall(b"OKAY")
        assert reset.wait(3)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
    def failure(error):
        failures.append(error)
        failed.set()
    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failure)
        try:
            with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
                AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
                assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
                AdbGateway._send_request(client, b"shell:logcat")
                assert AdbGateway._exact(client, 4) == b"OKAY"
                reset.set()
                assert failed.wait(3)
            assert failures[0].evidence["cause"]["type"] == "ConnectionResetError"
            assert failures[0].evidence["branch"] == "proxy_stream"
        finally:
            gateway.close()


@pytest.mark.parametrize("first_fin", ["client", "upstream"])
def test_two_gateways_preserve_both_directions_after_first_fin(first_fin):
    import struct
    from android_world.env import device_constants

    command = "test -d " + device_constants.AUDIORECORDER_DATA + " && echo present || echo missing"
    service = b"shell,v2,TERM=xterm-256color,raw:" + command.encode()
    stdout = b"\x01" + struct.pack("<I", 8) + b"present\n"
    stderr = b"\x02" + struct.pack("<I", 11) + b"diagnostic\n"
    exit_frame = b"\x03\x01\x00\x00\x00\x00"
    close_stdin = b"\x04\x00\x00\x00\x00"
    upstream_fin = threading.Event()
    drained = threading.Event()
    failures = []

    def handler(connection, request):
        assert request == b"host:tport:serial:emulator-5560"
        connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
        assert AdbGateway._request(connection) == service
        connection.sendall(b"OKAY" + stdout)
        if first_fin == "upstream":
            connection.sendall(stderr + exit_frame)
            connection.shutdown(socket.SHUT_WR)
            upstream_fin.set()
        assert AdbGateway._exact(connection, len(close_stdin)) == close_stdin
        assert connection.recv(1) == b""
        if first_fin == "client":
            connection.sendall(stderr + exit_frame)
            connection.shutdown(socket.SHUT_WR)
        drained.set()

    with upstream(handler) as (port, seen):
        parent = AdbGateway(port, "emulator-5560", failures.append)
        sdk = AdbGateway(parent.port, "emulator-5560", failures.append)
        try:
            with socket.create_connection(("127.0.0.1", sdk.port), timeout=2) as client:
                AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
                assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
                AdbGateway._send_request(client, service)
                assert AdbGateway._exact(client, 4 + len(stdout)) == b"OKAY" + stdout
                if first_fin == "upstream":
                    assert upstream_fin.wait(2)
                    assert AdbGateway._exact(client, len(stderr + exit_frame)) == stderr + exit_frame
                    assert client.recv(1) == b""
                client.sendall(close_stdin)
                client.shutdown(socket.SHUT_WR)
                if first_fin == "client":
                    assert AdbGateway._exact(client, len(stderr + exit_frame)) == stderr + exit_frame
                    assert client.recv(1) == b""
                assert drained.wait(2)
            assert failures == []
        finally:
            sdk.close()
            parent.close()


def test_selected_client_cancel_does_not_fence_later_two_gateway_command():
    failures = []
    cancelled = threading.Event()

    def handler(connection, request):
        assert request == b"host:tport:serial:emulator-5560"
        connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
        if not cancelled.is_set():
            assert connection.recv(1) == b""
            cancelled.set()
            return
        assert AdbGateway._request(connection) == b"shell:printf later-command"
        connection.sendall(b"OKAYlater-command")
        connection.shutdown(socket.SHUT_WR)
        assert connection.recv(1) == b""

    with upstream(handler) as (port, seen):
        parent = AdbGateway(port, "emulator-5560", failures.append)
        sdk = AdbGateway(parent.port, "emulator-5560", failures.append)
        try:
            with socket.create_connection(("127.0.0.1", sdk.port), timeout=2) as client:
                AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
                assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
                client.shutdown(socket.SHUT_WR)
                assert client.recv(1) == b""
            assert cancelled.wait(2)
            with socket.create_connection(("127.0.0.1", sdk.port), timeout=2) as client:
                AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
                assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
                AdbGateway._send_request(client, b"shell:printf later-command")
                client.shutdown(socket.SHUT_WR)
                assert AdbGateway._exact(client, 17) == b"OKAYlater-command"
                assert client.recv(1) == b""
            assert failures == []
        finally:
            sdk.close()
            parent.close()


def sms_rpc(serial, args=None, *, deadline=None):
    payload = {"args": ["sms", "send", "+15555550123", "It's café."] if args is None else args,
               "deadline": time.time() + 5 if deadline is None else deadline}
    return b"fsq:emu:" + serial.encode() + b":" + json.dumps(payload).encode()


@contextmanager
def emulator_console(handler):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.settimeout(0.1)
    stopped = threading.Event()
    accepted = []
    errors = []

    def serve():
        while not stopped.is_set():
            try:
                connection, address = listener.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            accepted.append(address)
            try:
                with connection:
                    connection.settimeout(2)
                    handler(connection)
            except BaseException as error:
                errors.append(error)

    worker = threading.Thread(target=serve)
    worker.start()
    try:
        yield listener.getsockname()[1], accepted
    finally:
        stopped.set()
        listener.close()
        worker.join(timeout=3)
        assert not worker.is_alive()
        assert errors == []


@pytest.mark.parametrize("authentication", [False, True])
def test_sms_rpc_crosses_both_gateways_before_exact_authenticated_console(monkeypatch, tmp_path, authentication):
    from fsq_androidworld_eval import adb_gateway

    (tmp_path / ".emulator_console_auth_token").write_text("private-test-token\n")
    monkeypatch.setattr(adb_gateway.Path, "home", lambda: tmp_path)
    commands = []

    def console(connection):
        with connection.makefile("rb") as reader:
            if authentication:
                connection.sendall(b"Android Console: Authentication required\r\nOK\r\n")
                commands.append(reader.readline())
                connection.sendall(b"Android Console: authenticated\r\nOK\r\n")
            else:
                connection.sendall(b"Android Console: type 'help' for a list of commands\r\nOK\r\n")
            commands.append(reader.readline())
            connection.sendall(b"OK\r\n")
            assert reader.readline() == b""

    def daemon(connection, request):
        assert request == b"host:version"
        connection.sendall(b"OKAY00040029")

    failures = []
    admissions = []
    with emulator_console(console) as (console_port, accepted), upstream(daemon) as (port, seen):
        serial = f"emulator-{console_port}"
        parent = AdbGateway(port, serial, failures.append, upstream_identity=lambda: admissions.append(True) or True)
        sdk = AdbGateway(parent.port, serial, failures.append, forward_emulator=True)
        try:
            assert exchange(sdk.port, b"host:version") == (b"OKAY", b"0029")
            assert exchange(sdk.port, sms_rpc(serial)) == (b"OKAY", b"OK\r\n")
            assert seen == [b"host:version"]
            assert len(accepted) == 1
            expected = [b"auth private-test-token\n"] if authentication else []
            assert commands == expected + ["sms send +15555550123 It's café.\n".encode()]
            assert len(admissions) >= 5 and failures == []
        finally:
            sdk.close()
            parent.close()


@pytest.mark.parametrize("args", [
    ["kill"], ["avd", "snapshot", "load", "default"], ["gsm", "call", "+15555550123"],
    ["geo", "fix", "1", "2"], ["sms", "send", "+15555550123"],
    ["sms", "send", "+15555550123", "body", "kill"],
    ["sms", "send", "+15555550123", "body\nkill"],
    ["sms", "send", "+15555550123", "body\rkill"],
    ["sms", "send", "+15555550123", "body; kill"],
    ["sms", "send", "+15555550123", "body\x00kill"],
    ["sms", "send", "+1555;kill", "body"],
    ["sms", "send", "+15555550123", ""], ["sms", "send", "++1555", "body"],
    "sms send +15555550123 body", {"sms": "send"}, ["sms", "send", 1555, "body"],
])
def test_sms_rpc_rejects_management_injection_and_invalid_shapes_before_upstream(monkeypatch, args):
    def forbidden(*args):
        pytest.fail("Rejected RPC must not reach a console")

    monkeypatch.setattr(AdbGateway, "_console_sms", forbidden)
    failures = []
    with upstream(lambda connection, request: connection.sendall(b"OKAY00040029")) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", failures.append)
        try:
            assert exchange(gateway.port, b"host:version") == (b"OKAY", b"0029")
            assert exchange(gateway.port, sms_rpc("emulator-5560", args))[0] == b"FAIL"
            assert seen == [b"host:version"] and len(failures) == 1
            assert failures[0].evidence["request"]["redacted"] is True
            assert "body" not in str(failures[0])
        finally:
            gateway.close()


@pytest.mark.parametrize("rpc_request", [
    sms_rpc("emulator-5554"), sms_rpc("emulator-5560", deadline=0),
    sms_rpc("emulator-5560", deadline=float("inf")), sms_rpc("emulator-5560", deadline=True),
    b"fsq:emu:emulator-5560:{}", b"fsq:emu:emulator-5560:[]",
    b"fsq:emu:emulator-5560:not-json",
    b'fsq:emu:emulator-5560:{"args":["sms","send","1555","x"],"deadline":9999999999,"port":5554}',
])
def test_sms_rpc_target_deadline_and_schema_cannot_override_owned_boundary(monkeypatch, rpc_request):
    monkeypatch.setattr(AdbGateway, "_console_sms", lambda *args: pytest.fail("Invalid admission reached console"))
    with upstream(lambda connection, request: connection.sendall(b"OKAY00040029")) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", lambda error: None)
        try:
            assert exchange(gateway.port, b"host:version")[0] == b"OKAY"
            assert exchange(gateway.port, rpc_request)[0] == b"FAIL"
            assert seen == [b"host:version"]
        finally:
            gateway.close()


def test_sms_rpc_requires_version_even_without_parent_registration(monkeypatch):
    monkeypatch.setattr(AdbGateway, "_console_sms", lambda *args: pytest.fail("Unadmitted request reached console"))
    with upstream(lambda *args: pytest.fail("Unadmitted request reached daemon")) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", lambda error: None)
        try:
            assert exchange(gateway.port, sms_rpc("emulator-5560"))[0] == b"FAIL"
            assert seen == []
            assert gateway.failure.evidence["branch"] == "version_admission"
        finally:
            gateway.close()


@pytest.mark.parametrize("boundary", ["epoch", "deadline"])
def test_sms_rpc_rechecks_admission_after_console_auth_and_latches(monkeypatch, tmp_path, boundary):
    from fsq_androidworld_eval import adb_gateway

    (tmp_path / ".emulator_console_auth_token").write_text("private-test-token")
    monkeypatch.setattr(adb_gateway.Path, "home", lambda: tmp_path)
    valid = [True]
    clock = [time.time()]
    monkeypatch.setattr(adb_gateway.time, "time", lambda: clock[0])
    commands = []

    def console(connection):
        with connection.makefile("rb") as reader:
            connection.sendall(b"Android Console: Authentication required\r\nOK\r\n")
            commands.append(reader.readline())
            if boundary == "epoch":
                valid[0] = False
            else:
                clock[0] += 10
            connection.sendall(b"OK\r\n")
            assert reader.readline() == b""

    failures = []
    with emulator_console(console) as (console_port, accepted), upstream(
        lambda connection, request: connection.sendall(b"OKAY00040029")
    ) as (port, seen):
        serial = f"emulator-{console_port}"
        gateway = AdbGateway(port, serial, failures.append, upstream_identity=lambda: valid[0])
        try:
            assert exchange(gateway.port, b"host:version")[0] == b"OKAY"
            assert exchange(gateway.port, sms_rpc(serial))[0] == b"FAIL"
            first = gateway.failure
            assert first.evidence["branch"] == ("upstream_identity" if boundary == "epoch" else "emulator_console")
            valid[0] = True
            assert exchange(gateway.port, sms_rpc(serial))[0] == b"FAIL"
            assert gateway.failure is first and len(failures) == 1
            assert commands == [b"auth private-test-token\n"] and len(accepted) == 1
            assert "private-test-token" not in str(first)
            assert seen == [b"host:version"]
        finally:
            gateway.close()


@pytest.mark.parametrize("service", [b"sync:", b"exec:cmd package install -r -t -g -S 12", b"root:"])
def test_official_sync_install_and_root_selected_services_remain_scoped(service):
    observed = []

    def handler(connection, request):
        assert request == b"host:tport:serial:emulator-5560"
        connection.sendall(b"OKAY" + (7).to_bytes(8, "little"))
        observed.append(AdbGateway._request(connection))
        connection.sendall(b"OKAY")

    with upstream(handler) as (port, seen):
        gateway = AdbGateway(port, "emulator-5560", lambda error: pytest.fail(str(error)))
        try:
            with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
                AdbGateway._send_request(client, b"host:tport:serial:emulator-5560")
                assert AdbGateway._exact(client, 12) == b"OKAY" + (7).to_bytes(8, "little")
                AdbGateway._send_request(client, service)
                assert AdbGateway._exact(client, 4) == b"OKAY"
            assert observed == [service]
        finally:
            gateway.close()


@pytest.mark.parametrize("rejection", ["auth", "sms"])
def test_console_ko_is_sticky_and_never_reported_as_success(monkeypatch, tmp_path, rejection):
    from fsq_androidworld_eval import adb_gateway

    (tmp_path / ".emulator_console_auth_token").write_text("private-test-token")
    monkeypatch.setattr(adb_gateway.Path, "home", lambda: tmp_path)
    commands = []

    def console(connection):
        with connection.makefile("rb") as reader:
            connection.sendall(b"Android Console: Authentication required\r\nOK\r\n")
            commands.append(reader.readline())
            if rejection == "sms":
                connection.sendall(b"OK\r\n")
                commands.append(reader.readline())
            connection.sendall(b"KO: private-test-token It's caf\xc3\xa9.\r\n")
            assert reader.readline() == b""

    with emulator_console(console) as (console_port, accepted), upstream(
        lambda connection, request: connection.sendall(b"OKAY00040029")
    ) as (port, seen):
        serial = f"emulator-{console_port}"
        gateway = AdbGateway(port, serial, lambda error: None)
        try:
            assert exchange(gateway.port, b"host:version")[0] == b"OKAY"
            assert exchange(gateway.port, sms_rpc(serial))[0] == b"FAIL"
            assert isinstance(gateway.failure.original_cause, ConnectionError)
            assert len(commands) == (1 if rejection == "auth" else 2)
            assert "private-test-token" not in str(gateway.failure)
            assert "caf" not in str(gateway.failure)
        finally:
            gateway.close()
