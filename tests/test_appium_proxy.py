import ast
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from http import client as http_client
from http import server as http_server
import json
import socket
import struct
from threading import Condition, Event, Thread
import time
from urllib.parse import urlsplit

import pytest


from fsq_androidworld_eval.appium_proxy import AppiumAuditProxy
from fsq_androidworld_eval.action_budget import ActionGate
from fsq_androidworld_eval.lifecycle import EpisodeDeadlines


def test_audit_counts_every_created_and_deleted_session() -> None:
    with AppiumAuditProxy("http://127.0.0.1:4723") as proxy:
        proxy._observe(
            "POST",
            "/session",
            200,
            json.dumps({"value": {"sessionId": "one"}}).encode(),
        )
        proxy._observe(
            "POST",
            "/session",
            200,
            json.dumps({"value": {"sessionId": "two"}}).encode(),
        )
        proxy._observe("DELETE", "/session/one", 200, b'{"value":null}')
        audit = proxy.audit()

    assert audit["createdSessionCount"] == 2
    assert audit["deletedSessionCount"] == 1
    assert audit["ownedSessionCount"] == 2
    assert audit["activeSessionCount"] == 1
    assert len(set(audit["createdSessionHashes"])) == 2
    assert audit["deletedSessionHashes"] == [audit["createdSessionHashes"][0]]


def test_audit_records_malformed_session_creation_response() -> None:
    with AppiumAuditProxy("http://127.0.0.1:4723") as proxy:
        proxy._observe("POST", "/wd/hub/session", 200, b"not-json")
        audit = proxy.audit()

    assert audit["createdSessionCount"] == 0
    assert audit["errors"] == ["InvalidSessionResponse"]
    assert audit["unknownCreationOutcomeCount"] == 1


def test_client_disconnect_does_not_invalidate_observed_session() -> None:
    response_body = json.dumps(
        {"value": {"sessionId": "one", "padding": "x" * (1024 * 1024)}}
    ).encode()

    class UpstreamHandler(http_server.BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, format: str, *args: object) -> None:
            return

    upstream = http_server.ThreadingHTTPServer(("127.0.0.1", 0), UpstreamHandler)
    upstream_thread = Thread(target=upstream.serve_forever, daemon=True)
    upstream_thread.start()
    try:
        upstream_url = f"http://127.0.0.1:{upstream.server_address[1]}"
        with AppiumAuditProxy(upstream_url) as proxy:
            parsed = urlsplit(proxy.url)
            client = socket.create_connection((parsed.hostname, parsed.port))
            client.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_LINGER,
                struct.pack("ii", 1, 0),
            )
            client.sendall(
                b"POST /session HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n"
            )
            client.close()

            deadline = time.monotonic() + 5
            while proxy.audit()["createdSessionCount"] == 0 and time.monotonic() < deadline:
                time.sleep(0.01)
            audit = proxy.audit()
    finally:
        upstream.shutdown()
        upstream.server_close()
        upstream_thread.join(timeout=5)

    assert audit["createdSessionCount"] == 1
    assert audit["errors"] == []


class _DeviceState:
    """A stateful upstream: forbidden requests would really alter its UI state."""

    def __init__(self) -> None:
        self.condition = Condition()
        self.requests: list[tuple[str, str]] = []
        self.mutations: list[str] = []
        self.mutation_attempts: list[str] = []
        self.created = 0
        self.deleted = 0
        self.drop_next = False
        self.large_response = False
        self.sessions = {"baseline-session-secret"}
        self.fail_quit = False
        self.keep_session_on_quit = False
        self.creation_received = Event()
        self.creation_release = Event()
        self.creation_release.set()
        self.malformed_creation = False

    def snapshot(self) -> tuple[int, list[str], list[str], int, int]:
        with self.condition:
            return (len(self.requests), list(self.mutations), list(self.mutation_attempts), self.created, self.deleted)


@contextmanager
def _upstream():
    state = _DeviceState()

    class Handler(http_server.BaseHTTPRequestHandler):
        def _handle(self) -> None:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body or b"{}")
            path = urlsplit(self.path).path.removeprefix("/wd/hub").rstrip("/")
            route = "/".join(path.split("/")[3:])
            status = 200
            value: object = None
            with state.condition:
                state.requests.append((self.command, path))
                if self.command == "POST" and path == "/session":
                    state.created += 1
                    state.sessions.add("owned-session-secret")
                    caps = payload.get("capabilities", {}).get("alwaysMatch", {})
                    if caps.get("appium:appPackage") and caps.get("appium:autoLaunch", True):
                        state.mutations.append("session auto-launch")
                    if caps.get("appium:app"):
                        state.mutations.append("session install")
                    value = {"sessionId": "owned-session-secret", "capabilities": {"platformName": "Android"}}
                elif self.command == "DELETE" and path.startswith("/session/") and not route:
                    session_id = path.split("/")[2]
                    if session_id not in state.sessions:
                        status = 404
                        value = {"error": "invalid session id", "message": "Absent session", "stacktrace": ""}
                    elif state.fail_quit:
                        status = 500
                        value = {"error": "unknown error", "message": "Quit failed", "stacktrace": ""}
                    elif not state.keep_session_on_quit:
                        state.sessions.remove(session_id)
                        state.deleted += 1
                elif self.command == "GET" and path.startswith("/session/") and not route:
                    if path.split("/")[2] not in state.sessions:
                        status = 404
                        value = {"error": "invalid session id", "message": "Absent session", "stacktrace": ""}
                    else:
                        value = {"capabilities": {"platformName": "Android"}}
                elif self.command == "GET" and route != "business/save":
                    value = {"ui": list(state.mutations)}
                elif self.command == "POST" and (route in {"element", "elements"} or route.endswith("/elements")):
                    if "UiScrollable" in payload.get("value", ""):
                        state.mutations.append("hidden selector scroll")
                    value = {"element-6066-11e4-a52e-4f735466cecf": "element-secret"}
                elif self.command == "POST" and route in {"context", "timeouts", "appium/device/app_state"}:
                    value = 4
                elif self.command == "POST" and route == "execute/sync" and payload.get("script") in {
                    "mobile: queryAppState", "mobile: isKeyboardShown", "mobile: getCurrentPackage",
                }:
                    value = 4
                else:
                    state.mutation_attempts.append(route)
                    if state.drop_next:
                        state.drop_next = False
                        self.close_connection = True
                        self.connection.shutdown(socket.SHUT_RDWR)
                        state.condition.notify_all()
                        return
                    if "missing" in route:
                        status = 404
                        value = {"error": "no such element", "message": "Missing element", "stacktrace": ""}
                    else:
                        cycles = 1
                        if route == "actions":
                            cycles = sum(
                                action.get("type") == "pointerDown"
                                for source in payload.get("actions", [])
                                for action in source.get("actions", [])
                            )
                        state.mutations.extend([route] * cycles)
                if state.large_response and route:
                    value = {"padding": "x" * (1024 * 1024)}
                state.condition.notify_all()
            response = json.dumps({"value": value}).encode()
            if self.command == "POST" and path == "/session":
                state.creation_received.set()
                if not state.creation_release.wait(timeout=5):
                    return
                if state.malformed_creation:
                    response = b"not-json"
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            try:
                self.wfile.write(response)
            except (BrokenPipeError, ConnectionResetError):
                pass

        do_GET = _handle
        do_POST = _handle
        do_DELETE = _handle

        def log_message(self, format: str, *args: object) -> None:
            return

    server = http_server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", state
    finally:
        state.creation_release.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _request(url: str, method: str, path: str, payload: object = None) -> tuple[int, dict]:
    parsed = urlsplit(url)
    connection = http_client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    body = None if payload is None else json.dumps(payload).encode()
    try:
        connection.request(method, path, body=body, headers={"Content-Type": "application/json"})
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()


def _capabilities(**changes: object) -> dict:
    caps = {
        "platformName": "Android", "appium:automationName": "UiAutomator2",
        "appium:udid": "emulator-5554", "appium:noReset": True,
        "appium:skipUnlock": True, "appium:autoLaunch": False,
    }
    caps.update(changes)
    return {"capabilities": {"alwaysMatch": caps, "firstMatch": [{}]}}


def _connect(proxy: AppiumAuditProxy) -> str:
    status, payload = _request(proxy.url, "POST", "/session", _capabilities())
    assert status == 200
    return "/session/" + payload["value"]["sessionId"]


def _wait_queued(gate: ActionGate, count: int = 1) -> None:
    with gate._condition:
        assert gate._condition.wait_for(lambda: len(gate._pending) >= count, timeout=2)


def _single_gesture() -> dict:
    return {"actions": [{
        "type": "pointer", "id": "finger", "parameters": {"pointerType": "touch"},
        "actions": [
            {"type": "pointerMove", "duration": 0, "x": 30, "y": 40, "origin": "viewport"},
            {"type": "pointerDown", "button": 0},
            {"type": "pointerMove", "duration": 300, "x": 30, "y": 200, "origin": "viewport"},
            {"type": "pointerUp", "button": 0},
        ],
    }]}


def test_reference_steps_limit_actual_upstream_state_and_allow_read_and_quit() -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        with ThreadPoolExecutor(max_workers=1) as workers:
            # One continuous cell can issue many commands, but not forward them
            # all under one grant.
            def batch() -> list[int]:
                return [_request(proxy.url, "POST", session + "/element/element-secret/click", {})[0] for _ in range(3)]

            attempt = workers.submit(batch)
            try:
                for _ in range(2):
                    _wait_queued(gate)
                    assert len(state.snapshot()[1]) == gate.snapshot()["executedActionCount"]
                    assert gate.advance_step(timeout=2)["status"] == 200
                _wait_queued(gate)
            finally:
                gate.close_budget()
            assert attempt.result(timeout=2) == [200, 200, 500]
        assert state.snapshot()[1] == ["element/element-secret/click"] * 2
        assert _request(proxy.url, "GET", session + "/source")[0] == 200
        assert _request(proxy.url, "POST", session + "/elements", {"using": "id", "value": "safe"})[0] == 200
        assert _request(proxy.url, "POST", session + "/execute/sync", {"script": "mobile: queryAppState", "args": [{"appId": "org.example"}]})[0] == 200
        assert _request(proxy.url, "DELETE", session)[0] == 200
        assert state.snapshot()[3:] == (1, 1)
        audit = proxy.audit()
    assert gate.snapshot()["executedActionCount"] == 2
    assert gate.snapshot()["rejectedActionCount"] == 1
    assert audit["errors"] == []
    assert audit["deletedSessionHashes"] == audit["createdSessionHashes"]
    serialized = json.dumps({"audit": audit, "budget": gate.snapshot()})
    assert "owned-session-secret" not in serialized
    assert "element-secret" not in serialized


def test_concurrent_http_burst_cannot_cross_the_reference_grant_cap() -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        with ThreadPoolExecutor(max_workers=6) as workers:
            requests = [workers.submit(_request, proxy.url, "POST", session + "/back", {}) for _ in range(6)]
            try:
                _wait_queued(gate, 6)
                assert state.snapshot()[1] == []
                for _ in range(2):
                    gate.advance_step(timeout=2)
            finally:
                gate.close_budget()
            statuses = [request.result(timeout=2)[0] for request in requests]
        assert statuses.count(200) == 2
        assert statuses.count(500) == 4
        assert state.snapshot()[1] == ["back", "back"]
        assert len(state.snapshot()[2]) == 2
        assert gate.snapshot()["rejectedActionCount"] == 4


@pytest.mark.parametrize("changes", [
    {"appium:udid": "other-device"}, {"platformName": "iOS"},
    {"appium:automationName": "Espresso"}, {"appium:noReset": False},
    {"appium:skipUnlock": False}, {"appium:autoLaunch": True},
    {"appium:app": "/tmp/task.apk"}, {"appium:otherApps": ["/tmp/other.apk"]},
    {"appium:uninstallOtherPackages": "*"}, {"appium:fullReset": True},
    {"appium:autoGrantPermissions": True}, {"appium:forceAppLaunch": True},
    {"appium:shouldTerminateApp": True}, {"browserName": "Chrome"},
    {"appium:orientation": "LANDSCAPE"}, {"appium:gpsEnabled": False},
    {"appium:settings[ignoreUnimportantViews]": True},
    {"appium:systemPort": 9000}, {"appium:adbPort": 5038},
    {"appium:mjpegServerPort": 9001}, {"appium:remoteAdbHost": "other-host"},
    {"appium:options": {"udid": "other-device"}},
])
def test_unsafe_connections_are_denied_before_any_upstream_request(changes: dict) -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        status, response = _request(proxy.url, "POST", "/session", _capabilities(**changes))
        assert status == 400
        assert response["value"]["error"] == "invalid argument"
        assert state.snapshot() == (0, [], [], 0, 0)
        assert proxy.audit()["errors"] == []


def test_all_capability_alternatives_and_nested_options_are_validated() -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        capabilities = _capabilities()
        del capabilities["capabilities"]["alwaysMatch"]["appium:udid"]
        capabilities["capabilities"]["firstMatch"] = [{"appium:udid": "emulator-5554"}, {"appium:udid": "other-device"}]
        assert _request(proxy.url, "POST", "/session", capabilities)[0] == 400
        assert state.snapshot()[0] == 0
        nested = {"capabilities": {"alwaysMatch": {
            "platformName": "Android", "appium:options": {
                "automationName": "UiAutomator2", "udid": "emulator-5554",
                "noReset": True, "skipUnlock": True, "autoLaunch": False,
            },
        }}}
        assert _request(proxy.url, "POST", "/session", nested)[0] == 200
        assert _request(proxy.url, "POST", "/session", _capabilities())[0] == 500
        assert state.snapshot()[3] == 1


def test_autolaunch_default_is_safe_only_without_an_aut() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        capabilities = _capabilities(**{"appium:appPackage": "org.example"})
        del capabilities["capabilities"]["alwaysMatch"]["appium:autoLaunch"]
        assert _request(proxy.url, "POST", "/session", capabilities)[0] == 400
        assert state.snapshot()[0] == 0
        del capabilities["capabilities"]["alwaysMatch"]["appium:appPackage"]
        assert _request(proxy.url, "POST", "/session", capabilities)[0] == 200
        assert state.snapshot()[1] == []


@pytest.mark.parametrize("method, route, payload", [
    ("POST", "/execute/sync", {"script": "mobile: shell", "args": [{"command": "input", "args": ["tap", "1", "1"]}]}),
    ("POST", "/execute/sync", {"script": "mobile: scheduleAction", "args": [{"name": "x", "steps": []}]}),
    ("POST", "/execute/sync", {"script": "mobile: startActivity", "args": [{"component": "org.example/.Save"}]}),
    ("POST", "/execute/sync", {"script": "mobile: deepLink", "args": [{"url": "app://save"}]}),
    ("POST", "/execute/sync", {"script": "mobile: scroll", "args": [{"strategy": "id", "selector": "save", "maxSwipes": 20}]}),
    ("POST", "/execute/sync", {"script": "mobile: clearApp", "args": [{"appId": "org.example"}]}),
    ("POST", "/execute/sync", {"script": "mobile: installApp", "args": [{"appPath": "/tmp/x.apk"}]}),
    ("POST", "/execute/sync", {"script": "return saveBusinessObject()", "args": []}),
    ("POST", "/execute/async", {"script": "mobile: clickGesture", "args": [{}]}),
    ("POST", "/appium/execute_driver", {"script": "await driver.back(); await driver.back()"}),
    ("POST", "/appium/app/reset", {}), ("POST", "/appium/device/install_app", {"appPath": "/tmp/x.apk"}),
    ("POST", "/business/save", {}), ("GET", "/business/save", None),
    ("DELETE", "/cookie", None), ("DELETE", "/element/id", None), ("DELETE", "/actions", None),
    ("POST", "/context", {"name": "WEBVIEW_org.example"}),
    ("POST", "/element", {"using": "-android uiautomator", "value": 'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("save"))'}),
    ("POST", "/elements", {"using": "-android uiautomator", "value": 'new UiObject(new UiSelector()).click()'}),
])
def test_opaque_backdoors_and_mutating_searches_leave_upstream_untouched(method: str, route: str, payload: object) -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        before = state.snapshot()
        status, response = _request(proxy.url, method, session + route, payload)
        assert status == 500
        assert response["value"]["error"] == "unsupported operation"
        assert state.snapshot() == before
        assert proxy.audit()["deletedSessionCount"] == 0
        assert gate.snapshot()["executedActionCount"] == 0


@pytest.mark.parametrize("suffix", [
    "/back?alias=1", "/%62ack", "/%2562ack", "//back", "/x/../back", "/back%2f..%2fback",
])
def test_aliases_and_wrong_sessions_cannot_bypass_classification(suffix: str) -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        before = state.snapshot()
        assert _request(proxy.url, "POST", session + suffix, {})[0] == 400
        assert _request(proxy.url, "POST", "/session/not-owned/back", {})[0] == 404
        assert _request(proxy.url, "DELETE", "/session/not-owned")[0] == 404
        assert state.snapshot() == before


def test_pure_queries_remain_available_after_exhaustion_and_no_delete_alias_is_quit() -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        gate.close_budget()
        for route, payload in [
            ("/element", {"using": "-android uiautomator", "value": 'new UiSelector().text("Save").clickable(true)'}),
            ("/context", {"name": "NATIVE_APP"}),
            ("/execute/sync", {"script": "mobile: isKeyboardShown", "args": []}),
            ("/timeouts", {"implicit": 0}),
        ]:
            assert _request(proxy.url, "POST", session + route, payload)[0] == 200
        assert state.snapshot()[1] == []
        assert _request(proxy.url, "POST", session + "/back", {})[0] == 500
        assert _request(proxy.url, "DELETE", session + "/cookie")[0] == 500
        assert proxy.audit()["deletedSessionCount"] == 0
        assert _request(proxy.url, "DELETE", session + "/")[0] == 200
        assert state.snapshot()[4] == 1


@pytest.mark.parametrize("route, payload", [
    ("/element/element-secret/click", {}), ("/element/element-secret/clear", {}),
    ("/element/element-secret/value", {"text": "private typed text"}),
    ("/back", {}), ("/actions", _single_gesture()),
    ("/execute/sync", {"script": "mobile: pressKey", "args": [{"keycode": 4}]}),
    ("/execute/sync", {"script": "mobile: hideKeyboard", "args": []}),
    ("/execute/sync", {"script": "mobile: activateApp", "args": [{"appId": "org.example", "bundleId": "org.example"}]}),
    ("/execute/sync", {"script": "mobile: doubleClickGesture", "args": [{"x": 2, "y": 3}]}),
    ("/execute/sync", {"script": "mobile: scrollGesture", "args": [{"left": 0, "top": 0, "width": 20, "height": 30, "direction": "down", "percent": 1}]}),
])
def test_supported_ui_command_requires_and_consumes_one_real_grant(route: str, payload: dict) -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        with ThreadPoolExecutor(max_workers=1) as workers:
            request = workers.submit(_request, proxy.url, "POST", session + route, payload)
            try:
                _wait_queued(gate)
                assert state.snapshot()[1] == []
                record = gate.advance_step(timeout=2)
                assert record["status"] == 200
                assert request.result(timeout=2)[0] == 200
            finally:
                gate.close_budget()
        assert len(state.snapshot()[1]) == 1
        before = state.snapshot()
        assert _request(proxy.url, "POST", session + route, payload)[0] == 500
        assert state.snapshot() == before
        assert gate.snapshot()["executedActionCount"] == 1
        serialized = json.dumps(gate.snapshot())
        assert "private typed text" not in serialized
        assert "owned-session-secret" not in serialized
        assert "element-secret" not in serialized


def test_bundled_or_unbounded_gestures_never_reach_the_device() -> None:
    gesture = _single_gesture()
    doubled = _single_gesture()
    doubled["actions"][0]["actions"] *= 2
    incomplete = _single_gesture()
    incomplete["actions"][0]["actions"].pop()
    multi_source = {"actions": gesture["actions"] + [{"type": "key", "id": "keyboard", "actions": [{"type": "keyDown", "value": "x"}]}]}
    too_long = _single_gesture()
    too_long["actions"][0]["actions"][2]["duration"] = 10001
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        before = state.snapshot()
        for payload in (doubled, incomplete, multi_source, too_long):
            assert _request(proxy.url, "POST", session + "/actions", payload)[0] == 500
        for payload in (
            {"script": "mobile: scrollGesture", "args": [{"direction": "down", "percent": 4}]},
            {"script": "mobile: longClickGesture", "args": [{"duration": 10001}]},
            {"script": "mobile: clickGesture", "args": [{"x": 1}, {"x": 2}]},
        ):
            assert _request(proxy.url, "POST", session + "/execute/sync", payload)[0] == 500
        assert state.snapshot() == before


def test_failed_ui_attempt_and_upstream_disconnect_complete_permits_truthfully() -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        with ThreadPoolExecutor(max_workers=1) as workers:
            missing = workers.submit(_request, proxy.url, "POST", session + "/element/missing/click", {})
            _wait_queued(gate)
            assert gate.advance_step(timeout=2)["status"] == 404
            assert missing.result(timeout=2)[0] == 404
            state.drop_next = True
            dropped = workers.submit(_request, proxy.url, "POST", session + "/back", {})
            _wait_queued(gate)
            assert "status" not in gate.advance_step(timeout=2)
            assert dropped.result(timeout=2)[0] == 502
        gate.close_budget()
        assert gate.snapshot()["executedActionCount"] == 2
        assert len(state.snapshot()[2]) == 2
        assert state.snapshot()[1] == []
        assert proxy.audit()["errors"] == ["RemoteDisconnected"]


def test_client_disconnect_still_completes_the_granted_upstream_mutation() -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        state.large_response = True
        parsed = urlsplit(proxy.url)
        client = socket.create_connection((parsed.hostname, parsed.port))
        client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        client.sendall((f"POST {session}/back HTTP/1.1\r\nHost: localhost\r\nContent-Length: 2\r\n\r\n{{}}").encode())
        client.close()
        _wait_queued(gate)
        assert gate.advance_step(timeout=2)["status"] == 200
        gate.close_budget()
        assert state.snapshot()[1] == ["back"]
        assert proxy.audit()["errors"] == []


def test_session_audit_only_counts_exact_root_delete() -> None:
    with AppiumAuditProxy("http://127.0.0.1:4723") as proxy:
        for path in ("/session/one/cookie", "/session/one/element/x", "/session/one/actions", "/other/session/one"):
            proxy._observe("DELETE", path, 200, b'{"value":null}')
        assert proxy.audit()["deletedSessionCount"] == 0
        proxy._observe("DELETE", "/wd/hub/session/one/", 200, b'{"value":null}')
        assert proxy.audit()["deletedSessionCount"] == 1


def _execute_recovery(code: str, timeout_seconds: float) -> dict:
    """Exercise the generated official Client code in a fresh test namespace."""
    assert 0 < timeout_seconds <= 120
    tree = ast.parse(code)
    namespace: dict = {}
    exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), "<recovery>", "exec"), namespace)
    return eval(compile(ast.Expression(tree.body[-1].value), "<recovery>", "eval"), namespace)


def _disconnect_during_creation(proxy: AppiumAuditProxy, state: _DeviceState) -> None:
    state.creation_release.clear()
    parsed = urlsplit(proxy.url)
    client = socket.create_connection((parsed.hostname, parsed.port))
    body = json.dumps(_capabilities()).encode()
    client.sendall(
        (f"POST /session HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(body)}\r\n\r\n").encode() + body
    )
    assert state.creation_received.wait(timeout=2)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
    client.close()
    audit = proxy.audit()
    assert audit["pendingCreateCount"] == audit["pendingRequestCount"] == 1
    assert audit["createdSessionCount"] == 0


def test_deleted_session_is_rejected_but_ownership_history_survives() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        created = proxy.audit()["createdSessionHashes"]
        assert _request(proxy.url, "DELETE", session)[0] == 200
        before = state.snapshot()
        assert _request(proxy.url, "GET", session + "/source")[0] == 404
        assert _request(proxy.url, "DELETE", session)[0] == 404
        assert state.snapshot() == before
        audit = proxy.audit()
        assert audit["createdSessionHashes"] == audit["deletedSessionHashes"] == created
        assert audit["ownedSessionCount"] == 1
        assert audit["activeSessionCount"] == 0
        report = proxy.reclaim_owned(_execute_recovery)
        assert report["status"] == "unknown"
        assert report["sessions"][0]["alreadyAbsent"] is True
        assert report["sessions"][0]["absentVerified"] is True
        assert report["reclaimedSessionCount"] == 0
        assert state.snapshot()[4] == 1


def test_cancelled_creation_is_drained_before_targeted_recovery() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        _disconnect_during_creation(proxy, state)
        with ThreadPoolExecutor(max_workers=1) as workers:
            reclaim = workers.submit(proxy.reclaim_owned, _execute_recovery)
            try:
                # The server has created a session but has not disclosed its ID.
                # Recovery must wait, not classify it as not-created.
                assert not reclaim.done()
            finally:
                state.creation_release.set()
            report = reclaim.result(timeout=3)
        audit = proxy.audit()
        assert report["status"] == "harness_reclaimed"
        assert state.sessions == {"baseline-session-secret"}
        assert state.snapshot()[3:] == (1, 1)
        assert audit["createdSessionCount"] == audit["reclaimedSessionCount"] == 1
        assert audit["deletedSessionCount"] == 0
        assert audit["pendingCreateCount"] == audit["pendingRequestCount"] == 0
        assert audit["unknownCreationOutcomeCount"] == 0
        assert all("baseline-session-secret" not in path for _, path in state.requests)
        assert "owned-session-secret" not in json.dumps({"report": report, "audit": audit})


def test_shutdown_waits_for_pending_response_before_destroying_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    with _upstream() as (url, state):
        proxy = AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554")
        proxy.__enter__()
        stopped_accepting = Event()
        shutdown = proxy._server.shutdown

        def stop_accepting() -> None:
            shutdown()
            stopped_accepting.set()

        monkeypatch.setattr(proxy._server, "shutdown", stop_accepting)
        try:
            _disconnect_during_creation(proxy, state)
            with ThreadPoolExecutor(max_workers=1) as workers:
                closed = workers.submit(proxy.__exit__, None, None, None)
                try:
                    assert stopped_accepting.wait(timeout=2)
                    assert not closed.done()
                finally:
                    state.creation_release.set()
                closed.result(timeout=2)
            audit = proxy.audit()
            assert audit["createdSessionCount"] == 1
            assert audit["pendingCreateCount"] == audit["pendingRequestCount"] == 0
            assert audit["unknownCreationOutcomeCount"] == 0
            # Recovery is independent of the now-closed downstream listener.
            assert proxy.reclaim_owned(_execute_recovery)["status"] == "harness_reclaimed"
            assert state.sessions == {"baseline-session-secret"}
        finally:
            state.creation_release.set()
            if proxy._thread.is_alive():
                proxy.__exit__(None, None, None)


def test_forced_agent_exit_reclaims_only_confirmed_owned_survivor() -> None:
    gate = ActionGate()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=gate, expected_udid="emulator-5554") as proxy:
        _connect(proxy)
        gate.close_budget()
        report = proxy.reclaim_owned(_execute_recovery)
        audit = proxy.audit()
        assert report["status"] == "harness_reclaimed"
        assert report["sessions"][0]["quitReturned"] is True
        assert report["sessions"][0]["absentVerified"] is True
        assert audit["deletedSessionCount"] == 0
        assert audit["createdSessionCount"] == audit["ownedSessionCount"] == 1
        assert audit["reclaimedSessionHashes"] == audit["createdSessionHashes"]
        assert state.snapshot()[3:] == (1, 1)
        assert state.sessions == {"baseline-session-secret"}
        assert all("baseline-session-secret" not in path for _, path in state.requests)
        assert "owned-session-secret" not in json.dumps(report)


def test_failed_agent_and_recovery_quit_preserve_identity_and_errors() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        state.fail_quit = True
        assert _request(proxy.url, "DELETE", session)[0] == 500
        failed = proxy.reclaim_owned(_execute_recovery)
        assert failed["status"] == "leaked"
        assert failed["sessions"][0]["quitReturned"] is False
        assert failed["sessions"][0]["presentVerified"] is True
        errors = failed["sessions"][0]["errors"]
        assert any(error["phase"] == "quit" for error in errors)
        assert proxy.audit()["activeSessionCount"] == 1
        assert proxy.audit()["errors"] == ["SessionQuitFailed"]
        state.fail_quit = False
        recovered = proxy.reclaim_owned(_execute_recovery)
        assert recovered["status"] == "harness_reclaimed"
        assert recovered["sessions"][0]["errors"] == errors
        assert proxy.audit()["deletedSessionCount"] == 0
        assert proxy.audit()["createdSessionCount"] == 1
        assert proxy.audit()["errors"] == ["SessionQuitFailed"]
        assert state.sessions == {"baseline-session-secret"}


def test_false_successful_agent_delete_is_reclaimed_from_immutable_history() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        session = _connect(proxy)
        state.keep_session_on_quit = True
        assert _request(proxy.url, "DELETE", session)[0] == 200
        assert proxy.audit()["activeSessionCount"] == 0
        state.keep_session_on_quit = False
        report = proxy.reclaim_owned(_execute_recovery)
        assert report["status"] == "harness_reclaimed"
        assert report["sessions"][0]["alreadyAbsent"] is False
        assert report["sessions"][0]["quitReturned"] is True
        assert report["sessions"][0]["absentVerified"] is True
        assert proxy.audit()["ownedSessionCount"] == 1
        assert state.sessions == {"baseline-session-secret"}


def test_quit_return_without_verified_deletion_is_not_reclaimed() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        _connect(proxy)
        state.keep_session_on_quit = True
        report = proxy.reclaim_owned(_execute_recovery)
        assert report["status"] == "leaked"
        assert report["sessions"][0]["quitReturned"] is True
        assert report["sessions"][0]["absentVerified"] is False
        assert report["sessions"][0]["presentVerified"] is True
        assert proxy.audit()["reclaimedSessionCount"] == 0
        assert state.sessions == {"owned-session-secret", "baseline-session-secret"}


def test_already_absent_session_is_not_attributed_to_agent_or_harness_quit() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        _connect(proxy)
        state.sessions.remove("owned-session-secret")
        report = proxy.reclaim_owned(_execute_recovery)
        assert report["status"] == "unknown"
        assert report["sessions"][0]["alreadyAbsent"] is True
        assert report["sessions"][0]["quitReturned"] is False
        assert proxy.audit()["deletedSessionCount"] == proxy.audit()["reclaimedSessionCount"] == 0
        assert not any(method == "DELETE" for method, _ in state.requests)


def test_unknown_creation_outcome_never_deletes_unattributed_sessions() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        state.malformed_creation = True
        with pytest.raises(json.JSONDecodeError):
            _request(proxy.url, "POST", "/session", _capabilities())
        calls: list[str] = []
        report = proxy.reclaim_owned(lambda code, timeout: calls.append(code))
        assert report["status"] == "unknown"
        assert report["unknownCreationOutcomeCount"] == 1
        assert calls == []
        assert state.sessions == {"owned-session-secret", "baseline-session-secret"}
        assert not any(method == "DELETE" for method, _ in state.requests)
        assert proxy.audit()["errors"] == ["InvalidSessionResponse"]


def test_pending_creation_drain_is_finite_and_retains_unknown_outcome() -> None:
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554") as proxy:
        _disconnect_during_creation(proxy, state)
        started = time.monotonic()
        try:
            report = proxy.reclaim_owned(_execute_recovery, timeout_seconds=0.1)
            assert time.monotonic() - started < 1
            assert report["status"] == "unknown"
            assert report["unknownCreationOutcomeCount"] == 1
            assert report["ownedSessionCount"] == 0
            assert not any(method == "DELETE" for method, _ in state.requests)
        finally:
            state.creation_release.set()


def test_business_expiry_denies_creations_but_preserves_cleanup_reads_and_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [0.0]
    monkeypatch.setattr("fsq_androidworld_eval.lifecycle.monotonic", lambda: clock[0])
    deadlines = EpisodeDeadlines(1, cleanup_seconds=10, termination_grace_seconds=1)
    deadlines.start()
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554", deadlines=deadlines) as proxy:
        session = _connect(proxy)
        clock[0] = 2
        assert _request(proxy.url, "POST", "/session", _capabilities())[0] == 500
        assert _request(proxy.url, "GET", session + "/source")[0] == 200
        assert _request(proxy.url, "DELETE", session)[0] == 200
        clock[0] = 11
        assert _request(proxy.url, "GET", "/status")[0] == 503
        assert state.snapshot()[3:] == (1, 1)
        assert len(state.requests) == 3


def test_upstream_timeout_is_bounded_by_remaining_cleanup_window() -> None:
    deadlines = EpisodeDeadlines(0.5, cleanup_seconds=0.1, termination_grace_seconds=0.1)
    with _upstream() as (url, state), AppiumAuditProxy(url, action_gate=ActionGate(), expected_udid="emulator-5554", deadlines=deadlines) as proxy:
        state.creation_release.clear()
        deadlines.start()
        started = time.monotonic()
        try:
            status, _ = _request(proxy.url, "POST", "/session", _capabilities())
            assert status == 502
            assert time.monotonic() - started < 1.5
            assert proxy.audit()["unknownCreationOutcomeCount"] == 1
            assert proxy.audit()["createdSessionCount"] == 0
        finally:
            state.creation_release.set()
