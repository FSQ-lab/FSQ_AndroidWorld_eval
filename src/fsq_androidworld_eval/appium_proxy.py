"""Transparent session-audited HTTP transport with a fail-closed UI action gate.

The guarded surface follows installed Appium 3.7.0 W3C/base-driver routes,
UiAutomator2 8.7.0 and inherited Android execute-method maps, and official Python
Client 6.1.4 (whose app/key helpers use ``mobile:`` execute methods). It is a
native Android connection, not an arbitrary WebDriver/program execution tunnel.

Connect to an already initialized target with noReset=true, skipUnlock=true,
autoLaunch=false, no app/APK installation, permission grants or reset. Only when
no appPackage/appActivity is supplied may autoLaunch be omitted: the real driver
has no AUT to launch. Driver helper initialization remains session lifecycle;
capabilities that change task/device state are not supported. No capabilities or
requests are silently rewritten. Audit-only construction retains transparent
transport for existing consumers; real runs supply both gate and exact UDID.
"""

from __future__ import annotations

import hashlib
from http import client as http_client
from http import server as http_server
import json
import math
import re
import socket
from threading import Condition, Lock, Thread
from time import monotonic
from typing import Any, Callable
from urllib.parse import urlsplit

from fsq_androidworld_eval.action_budget import ActionGate, ActionPermit, StepBudgetExceeded
from fsq_androidworld_eval.lifecycle import EpisodeDeadlines


class _Denied(Exception):
    def __init__(self, error: str, message: str, status: int | None = None):
        self.error = error
        self.message = message
        self.status = status if status is not None else (500 if error == "unsupported operation" else 400)


def _parts(path: str) -> list[str]:
    try:
        parsed = urlsplit(path)
    except ValueError:
        raise _Denied("invalid argument", "Non-canonical Appium request path") from None
    # Reject aliases rather than guessing how Express, a plugin and UiA2 each
    # decode them. Normal official Client requests need none of these forms.
    if (
        parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
        or not parsed.path.startswith("/") or "%" in parsed.path
        or "\\" in parsed.path or "//" in parsed.path
    ):
        raise _Denied("invalid argument", "Non-canonical Appium request path")
    parts = parsed.path.rstrip("/").split("/")[1:]
    if any(part in {".", "..", ""} for part in parts):
        raise _Denied("invalid argument", "Non-canonical Appium request path")
    if parts[:2] == ["wd", "hub"]:
        parts = parts[2:]
    return parts


def _object(body: bytes | None) -> dict[str, Any]:
    try:
        value = json.loads(body or b"{}")
    except (ValueError, UnicodeDecodeError):
        raise _Denied("invalid argument", "Appium request requires a JSON object") from None
    if not isinstance(value, dict):
        raise _Denied("invalid argument", "Appium request requires a JSON object")
    return value


# Explicit observations only: an unknown GET can also be a plugin backdoor.
_READ_ROUTES = {
    "", "source", "screenshot", "context", "contexts", "timeouts", "orientation",
    "rotation", "window", "window/handles", "window/rect", "window/current/size",
    "url", "title", "alert/text", "element/active", "location", "log/types",
    "appium/settings", "appium/device/current_activity", "appium/device/current_package",
    "appium/device/system_bars", "appium/device/display_density", "appium/device/pixel_ratio",
    "appium/device/info", "appium/device/battery_info", "network_connection",
    "appium/context", "appium/contexts", "appium/capabilities", "appium/commands",
    "appium/extensions", "appium/device/is_keyboard_shown", "appium/device/system_time",
    "appium/device/rotation", "appium/device/orientation",
}
_READ_MOBILE = {
    "viewportScreenshot", "viewportRect", "viewportElementRect", "batteryInfo", "deviceInfo",
    "getDeclaredOrientation", "screenshots", "getClipboard", "listWindows", "listDisplays",
    "getPermissions", "getDeviceTime", "getNotifications", "listSms", "isAppInstalled",
    "listApps", "queryAppState", "getContexts", "getChromeCapabilities", "isLocked",
    "isKeyboardShown", "getUiMode", "getPerformanceData", "getPerformanceDataTypes",
    "isGpsEnabled", "getDisplayDensity", "getSystemBars", "getCurrentActivity",
    "getCurrentPackage", "getGeolocation", "getAppStrings",
}
_GESTURE_MOBILE = {
    "clickGesture", "doubleClickGesture", "longClickGesture", "dragGesture", "flingGesture",
    "pinchCloseGesture", "pinchOpenGesture", "swipeGesture", "scrollGesture",
}
_UI_MOBILE = _GESTURE_MOBILE | {
    "type", "replaceElementValue", "pressKey", "hideKeyboard", "activateApp",
    "performEditorAction", "acceptAlert", "dismissAlert", "openNotifications",
}
_UI_ROUTES = {
    "back": "back", "keys": "input", "alert/accept": "acceptAlert",
    "alert/dismiss": "dismissAlert", "alert/text": "input",
    "appium/device/press_keycode": "key", "appium/device/long_press_keycode": "key",
    "appium/device/keyevent": "key", "appium/device/hide_keyboard": "hideKeyboard",
    "appium/device/open_notifications": "openNotifications",
    "appium/device/activate_app": "activateApp",
}
_READ_POST = {
    "appium/device/app_state", "appium/device/app_installed", "appium/device/is_locked",
    "appium/device/get_clipboard", "appium/device/system_time", "appium/events",
    "appium/app/strings", "appium/getPerformanceData", "appium/performanceData/types", "log",
}
_SAFE_CAPS = {
    "platformName", "automationName", "udid", "deviceName", "platformVersion", "noReset",
    "fullReset", "autoLaunch", "skipUnlock", "autoGrantPermissions", "forceAppLaunch",
    "shouldTerminateApp", "appPackage", "appActivity", "appWaitPackage", "appWaitActivity",
    "appWaitDuration", "newCommandTimeout", "adbExecTimeout",
    "uiautomator2ServerLaunchTimeout", "uiautomator2ServerInstallTimeout",
    "uiautomator2ServerReadTimeout", "skipDeviceInitialization", "skipServerInstallation",
    "skipLogcatCapture", "ignoreHiddenApiPolicyError", "printPageSourceOnFindFailure",
    "eventTimings", "browserName",
}
_SELECTOR_METHODS = (
    "text|textContains|textMatches|textStartsWith|description|descriptionContains|"
    "descriptionMatches|descriptionStartsWith|className|classNameMatches|resourceId|"
    "resourceIdMatches|packageName|packageNameMatches|index|instance|enabled|checked|"
    "checkable|clickable|longClickable|focusable|focused|scrollable|selected"
)
_PURE_SELECTOR = re.compile(
    r"\s*new\s+UiSelector\s*\(\s*\)"
    r"(?:\s*\.(?:" + _SELECTOR_METHODS + r")\s*\(\s*"
    r'(?:"(?:[^"\\]|\\.)*"|true|false|\d+)\s*\))*\s*;?\s*'
)


def _validate_session(payload: dict[str, Any], expected_udid: str | None) -> None:
    if set(payload) != {"capabilities"} or not isinstance(payload["capabilities"], dict):
        raise _Denied("invalid argument", "Only W3C capabilities are supported")
    capabilities = payload["capabilities"]
    if set(capabilities) - {"alwaysMatch", "firstMatch"}:
        raise _Denied("invalid argument", "Unsupported capability envelope")
    always = capabilities.get("alwaysMatch", {})
    first = capabilities.get("firstMatch", [{}])
    if not isinstance(always, dict) or not isinstance(first, list) or not first:
        raise _Denied("invalid argument", "Invalid W3C capability alternatives")
    for alternative in first:
        if not isinstance(alternative, dict) or set(always) & set(alternative):
            raise _Denied("invalid argument", "Conflicting W3C capability alternatives")
        raw = {**always, **alternative}
        options = raw.pop("appium:options", {})
        if not isinstance(options, dict):
            raise _Denied("invalid argument", "Invalid appium:options")
        caps: dict[str, Any] = {}
        for key, value in list(raw.items()) + list(options.items()):
            name = key.removeprefix("appium:")
            if name not in _SAFE_CAPS or name in caps:
                raise _Denied("invalid argument", "Unsupported or ambiguous connection capability")
            caps[name] = value
        if (
            not expected_udid or caps.get("udid") != expected_udid
            or str(caps.get("platformName", "")).lower() != "android"
            or str(caps.get("automationName", "")).lower() != "uiautomator2"
        ):
            raise _Denied("invalid argument", "Session must target the configured Android/UiAutomator2 device")
        if caps.get("noReset") is not True or caps.get("skipUnlock") is not True:
            raise _Denied("invalid argument", "Initialized tasks require noReset=true and skipUnlock=true")
        if "autoLaunch" in caps:
            if caps["autoLaunch"] is not False:
                raise _Denied("invalid argument", "Session autoLaunch must be false")
        elif caps.get("appPackage") or caps.get("appActivity"):
            raise _Denied("invalid argument", "An AUT connection requires explicit autoLaunch=false")
        for name in ("fullReset", "autoGrantPermissions", "forceAppLaunch", "shouldTerminateApp"):
            if name in caps and caps[name] is not False:
                raise _Denied("invalid argument", "Connection cannot reset, launch, terminate or grant permissions")
        if caps.get("browserName"):
            raise _Denied("invalid argument", "Only native Android sessions are supported")


def _validate_actions(payload: dict[str, Any]) -> None:
    sources = payload.get("actions")
    if not isinstance(sources, list) or len(sources) != 1:
        raise _Denied("unsupported operation", "Use one touch pointer and one contact cycle per step")
    source = sources[0]
    if (
        not isinstance(source, dict) or source.get("type") != "pointer"
        or not isinstance(source.get("parameters"), dict)
        or source.get("parameters", {}).get("pointerType") != "touch"
    ):
        raise _Denied("unsupported operation", "Only a single native touch pointer is supported")
    actions = source.get("actions")
    if not isinstance(actions, list) or not 2 <= len(actions) <= 256:
        raise _Denied("invalid argument", "A bounded single gesture is required")
    down = False
    ended = False
    duration = 0.0
    for action in actions:
        if not isinstance(action, dict):
            raise _Denied("invalid argument", "Invalid pointer action")
        kind = action.get("type")
        if not isinstance(kind, str):
            raise _Denied("invalid argument", "Invalid pointer action type")
        if kind == "pointerDown" and not down and not ended and action.get("button") == 0:
            down = True
        elif kind == "pointerUp" and down and action.get("button") == 0:
            down = False
            ended = True
        elif kind not in {"pointerMove", "pause"}:
            raise _Denied("unsupported operation", "Bundled or incomplete gestures are not supported")
        value = action.get("duration", 0)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise _Denied("invalid argument", "Invalid pointer duration")
        duration += value
    if down or not ended or duration > 10000:
        raise _Denied("unsupported operation", "Use one complete gesture lasting at most 10 seconds")


def _validate_gesture(name: str, args: dict[str, Any]) -> None:
    if name not in _GESTURE_MOBILE:
        return
    for key in ("percent", "duration", "speed"):
        if key not in args:
            continue
        value = args[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise _Denied("invalid argument", "Gesture bounds must be finite and positive")
        if (key == "percent" and value > 1) or (key == "duration" and value > 10000):
            raise _Denied("unsupported operation", "Gesture exceeds the single-interaction bounds")


def _recovery_code(upstream_url: str, session_ids: list[str], timeout_seconds: float) -> str:
    # This source is private transport input to a fresh python_exec namespace.
    # Its sole output is a bounded report containing hashes, never raw IDs.
    return f'''from hashlib import sha256 as _fsq_sha256
from time import monotonic as _fsq_monotonic
from appium.webdriver.webdriver import WebDriver as _FSQWebDriver
from appium.webdriver.client_config import AppiumClientConfig as _FSQClientConfig
from appium.options.android import UiAutomator2Options as _FSQOptions
from appium.webdriver.mobilecommand import MobileCommand as _FSQCommand
from selenium.common.exceptions import InvalidSessionIdException as _FSQInvalidSession

_fsq_recovery_deadline = _fsq_monotonic() + {timeout_seconds!r}
_fsq_recovery_url = {upstream_url!r}
_fsq_recovery_ids = {session_ids!r}
_fsq_recovery_report = {{"sessions": []}}

class _FSQOwnedSession(_FSQWebDriver):
    def __init__(self, owned_id):
        remaining = _fsq_recovery_deadline - _fsq_monotonic()
        if remaining <= 0:
            raise TimeoutError("Harness recovery deadline expired")
        self._fsq_owned_id = owned_id
        config = _FSQClientConfig(
            remote_server_addr=_fsq_recovery_url,
            timeout=min(30.0, remaining), keep_alive=False, direct_connection=False,
            init_args_for_pool_manager={{"init_args_for_pool_manager": {{"retries": 0}}}},
        )
        super().__init__(command_executor=_fsq_recovery_url, options=_FSQOptions(), client_config=config)

    def start_session(self, capabilities, browser_profile=None):
        # Constructor initialization is retained, but NEW_SESSION is impossible.
        self.session_id = self._fsq_owned_id
        self.caps = {{}}

for _fsq_owned_id in _fsq_recovery_ids:
    _fsq_result = {{
        "sessionHash": _fsq_sha256(_fsq_owned_id.encode()).hexdigest(),
        "quitReturned": False, "absentVerified": False,
        "presentVerified": False, "alreadyAbsent": False, "errors": [],
    }}
    _fsq_recovery_report["sessions"].append(_fsq_result)
    _fsq_driver = None
    try:
        _fsq_driver = _FSQOwnedSession(_fsq_owned_id)
        try:
            _fsq_driver.execute(_FSQCommand.GET_SESSION)
        except _FSQInvalidSession:
            _fsq_result["alreadyAbsent"] = True
            _fsq_result["absentVerified"] = True
        except Exception as _fsq_error:
            _fsq_result["errors"].append({{"phase": "probe", "error": type(_fsq_error).__name__}})
    except Exception as _fsq_error:
        _fsq_result["errors"].append({{"phase": "attach", "error": type(_fsq_error).__name__}})
    finally:
        if _fsq_driver is not None:
            _fsq_driver.command_executor.close()
    if _fsq_result["alreadyAbsent"]:
        continue
    _fsq_driver = None
    try:
        _fsq_driver = _FSQOwnedSession(_fsq_owned_id)
        _fsq_driver.quit()
        _fsq_result["quitReturned"] = True
    except Exception as _fsq_error:
        _fsq_result["errors"].append({{"phase": "quit", "error": type(_fsq_error).__name__}})
    finally:
        if _fsq_driver is not None:
            _fsq_driver.command_executor.close()
    _fsq_driver = None
    try:
        # A separate official Client, not a local session_id/caps check.
        _fsq_driver = _FSQOwnedSession(_fsq_owned_id)
        _fsq_driver.execute(_FSQCommand.GET_SESSION)
        _fsq_result["presentVerified"] = True
    except _FSQInvalidSession:
        _fsq_result["absentVerified"] = True
    except Exception as _fsq_error:
        _fsq_result["errors"].append({{"phase": "verify", "error": type(_fsq_error).__name__}})
    finally:
        if _fsq_driver is not None:
            _fsq_driver.command_executor.close()
_fsq_recovery_ids = []
_fsq_owned_id = None
_fsq_driver = None
_fsq_recovery_report
'''


class AppiumAuditProxy:
    def __init__(
        self, upstream_url: str, *, action_gate: ActionGate | None = None,
        expected_udid: str | None = None, deadlines: EpisodeDeadlines | None = None,
    ):
        upstream = urlsplit(upstream_url)
        if upstream.scheme != "http" or not upstream.hostname:
            raise ValueError("Appium audit proxy requires an http upstream URL")
        self._host = upstream.hostname
        self._port = upstream.port or 80
        self._base_path = upstream.path.rstrip("/")
        self._gate = action_gate
        self._expected_udid = expected_udid
        self._deadlines = deadlines
        self._guarded = action_gate is not None or expected_udid is not None
        self._lock = Lock()
        self._condition = Condition(self._lock)
        self._recovery_lock = Lock()
        self._closing = False
        self._pending: dict[object, dict[str, Any]] = {}
        self._unknown_creations: list[str] = []
        self._recovery_results: dict[str, dict[str, Any]] = {}
        self._created: list[str] = []
        self._deleted: list[str] = []
        self._errors: list[str] = []
        self._denials: list[dict[str, Any]] = []
        self._session_attempted = False
        self._owned: set[str] = set()
        # Ownership history survives DELETE and kernel/process death. Only the
        # active set controls ordinary commands; recovery never discovers IDs.
        self._active_owned: set[str] = set()
        self._reclaimed: set[str] = set()
        owner = self

        class Handler(http_server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def do_GET(self) -> None:
                self._forward()

            def do_POST(self) -> None:
                self._forward()

            def do_DELETE(self) -> None:
                self._forward()

            def do_PUT(self) -> None:
                self._forward()

            def do_PATCH(self) -> None:
                self._forward()

            def _error(self, status: int, error: str, message: str) -> None:
                payload = json.dumps({"value": {"error": error, "message": message, "stacktrace": ""}}).encode()
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def _forward(self) -> None:
                permit: ActionPermit | None = None
                status: int | None = None
                token: object | None = None
                connection: http_client.HTTPConnection | None = None
                try:
                    lengths = self.headers.get_all("Content-Length", [])
                    if self.headers.get("Transfer-Encoding") or len(lengths) > 1:
                        self.close_connection = True
                        raise _Denied("invalid argument", "Unsupported HTTP request framing")
                    try:
                        length = int(lengths[0]) if lengths else 0
                    except ValueError:
                        raise _Denied("invalid argument", "Invalid Content-Length") from None
                    if length < 0:
                        raise _Denied("invalid argument", "Invalid Content-Length")
                    body = self.rfile.read(length) if length else None
                    descriptor = owner._authorize(self.command, self.path, body) if owner._guarded else None
                    token = owner._begin_request(self.command, self.path)
                    if descriptor is not None:
                        if owner._gate is None:
                            raise _Denied("unsupported operation", "UI interactions require a reference-step gate")
                        permit = owner._gate.submit(descriptor)
                    headers = {
                        key: value for key, value in self.headers.items()
                        if key.lower() not in {"host", "connection", "content-length"}
                    }
                    connection = http_client.HTTPConnection(
                        owner._host, owner._port, timeout=owner._request_timeout()
                    )
                    with owner._lock:
                        owner._pending[token]["upstreamStarted"] = True
                    connection.request(self.command, owner._base_path + self.path, body=body, headers=headers)
                    with owner._lock:
                        owner._pending[token]["socket"] = connection.sock
                    response = connection.getresponse()
                    status = response.status
                    response_body = response.read()
                    response_headers = response.getheaders()
                    owner._observe(self.command, self.path, status, response_body)
                    with owner._lock:
                        owner._pending[token]["observed"] = True
                    try:
                        self.send_response(status)
                        for key, value in response_headers:
                            if key.lower() not in {"connection", "content-length", "transfer-encoding"}:
                                self.send_header(key, value)
                        self.send_header("Content-Length", str(len(response_body)))
                        self.end_headers()
                        self.wfile.write(response_body)
                    except (BrokenPipeError, ConnectionResetError):
                        # Observe upstream before touching the possibly dead client.
                        pass
                except StepBudgetExceeded:
                    owner._deny("step budget exhausted")
                    self._error(500, "unsupported operation", "Official reference step budget exhausted; observations and session quit remain available")
                except _Denied as exc:
                    owner._deny(exc.error)
                    self._error(exc.status, exc.error, exc.message)
                except Exception as exc:
                    with owner._lock:
                        owner._errors.append(type(exc).__name__)
                    self._error(502, "unknown error", type(exc).__name__)
                finally:
                    try:
                        if connection is not None:
                            connection.close()
                        if permit is not None:
                            permit.complete(status)
                    finally:
                        if token is not None:
                            owner._finish_request(token)

            def log_message(self, format: str, *args: Any) -> None:
                return

        self._server = http_server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        # server_close must not secretly join a stuck handler without a deadline.
        self._server.daemon_threads = True
        self._server.block_on_close = False
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> AppiumAuditProxy:
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self._quiesce()
        self._server.shutdown()
        self.wait_for_idle(self._drain_timeout())
        self._server.server_close()
        self._thread.join(timeout=5)

    def _quiesce(self) -> None:
        with self._lock:
            self._closing = True
        if self._gate is not None:
            self._gate.close_budget()

    def _request_timeout(self) -> float:
        # A 90-second creation cell needs transport overhead, but must still
        # finish inside the isolated 120-second MCP transport deadline.
        remaining = 110.0 if self._deadlines is None else min(110.0, self._deadlines.remaining("cleanup"))
        if remaining <= 0:
            raise _Denied("unsupported operation", "Episode cleanup deadline expired", 503)
        return remaining

    def _drain_timeout(self) -> float:
        return 110.0 if self._deadlines is None else min(110.0, self._deadlines.remaining("cleanup"))

    def _begin_request(self, method: str, path: str) -> object:
        try:
            parts = _parts(path)
        except _Denied:
            parts = []
        creating = method == "POST" and parts == ["session"]
        with self._condition:
            if self._closing:
                raise _Denied("unsupported operation", "Episode transport is draining", 503)
            if len(parts) >= 2 and parts[0] == "session" and parts[1] in self._owned and parts[1] not in self._active_owned:
                raise _Denied("invalid session id", "Task-owned session was deleted", 404)
            if self._deadlines is not None:
                if self._deadlines.expired("cleanup"):
                    raise _Denied("unsupported operation", "Episode cleanup deadline expired", 503)
                if creating and self._deadlines.expired("business"):
                    raise _Denied("session not created", "Episode business deadline expired", 500)
            token = object()
            self._pending[token] = {
                "creating": creating, "upstreamStarted": False,
                "observed": False, "unknownRecorded": False, "socket": None,
            }
            if creating:
                self._session_attempted = True
            self._condition.notify_all()
            return token

    def _unknown_creation(self, request: dict[str, Any], reason: str) -> None:
        if request["creating"] and request["upstreamStarted"] and not request["observed"] and not request["unknownRecorded"]:
            self._unknown_creations.append(reason)
            request["unknownRecorded"] = True

    def _finish_request(self, token: object) -> None:
        with self._condition:
            request = self._pending.pop(token)
            self._unknown_creation(request, "TransportOutcomeUnknown")
            self._condition.notify_all()

    def wait_for_idle(self, timeout_seconds: float) -> bool:
        """Observe accepted responses before teardown; never wait indefinitely.

        On expiry, interrupt only this proxy's in-flight sockets. A creation
        without a fully observed response remains unknown, never not-created.
        """
        if not math.isfinite(timeout_seconds) or timeout_seconds < 0:
            raise ValueError("Drain timeout must be finite and nonnegative")
        with self._condition:
            if self._condition.wait_for(lambda: not self._pending, timeout_seconds):
                return True
            sockets = [request["socket"] for request in self._pending.values() if request["socket"] is not None]
            for request in self._pending.values():
                self._unknown_creation(request, "ShutdownDrainTimeout")
            self._errors.append("ShutdownDrainTimeout")
        for upstream_socket in sockets:
            try:
                upstream_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        # Socket shutdown wakes getresponse/read; do not extend the drain window
        # waiting for a handler or downstream peer that still cannot finish.
        return False

    def reclaim_owned(
        self, execute_python: Callable[[str, float], dict[str, Any]], *,
        timeout_seconds: float = 120.0,
    ) -> dict[str, Any]:
        """Reclaim confirmed survivors using a fresh official-Client kernel.

        ``execute_python(code, timeout_seconds)`` must independently invoke
        AMKernel python_exec and return the code's final-expression dict only
        after a successful execution envelope. It must raise on MCP/kernel
        failure and enforce the supplied finite wall-clock timeout. Source and
        raw IDs are private transport input, not audit/log/output material.

        The recovery window is independent of the expired business/cleanup
        deadlines, so a dead former kernel/process cannot prevent reclamation.
        Only quit plus independently verified absence is harness_reclaimed;
        nothing in this report proves successful agent cleanup.
        """
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("Recovery timeout must be finite and positive")
        recovery_end = monotonic() + min(timeout_seconds, 120.0)
        with self._recovery_lock:
            self._quiesce()
            drained = self.wait_for_idle(min(self._drain_timeout(), max(0.0, recovery_end - monotonic())))
            if not drained:
                # Give interrupted reads a bounded chance to publish their
                # final observation before taking the ownership snapshot.
                with self._condition:
                    self._condition.wait_for(lambda: not self._pending, min(1.0, max(0.0, recovery_end - monotonic())))
            with self._lock:
                pending = bool(self._pending)
                # Agent DELETE responses deactivate commands, but do not prove
                # remote absence. Reconcile history, not just active ownership.
                owned = sorted(
                    session_id for session_id in self._owned
                    if not self._recovery_results.get(
                        hashlib.sha256(session_id.encode()).hexdigest(), {}
                    ).get("absentVerified", False)
                )
            if not pending and owned:
                expected = {hashlib.sha256(value.encode()).hexdigest(): value for value in owned}
                try:
                    for session_id in owned:
                        if _parts("/session/" + session_id) != ["session", session_id]:
                            raise ValueError("Non-canonical owned session identity")
                    remaining = recovery_end - monotonic()
                    if remaining <= 0:
                        raise TimeoutError("Harness recovery deadline expired")
                    host = f"[{self._host}]" if ":" in self._host else self._host
                    upstream_url = f"http://{host}:{self._port}{self._base_path}"
                    payload = execute_python(
                        _recovery_code(upstream_url, owned, max(0.001, remaining - 2.0)), remaining
                    )
                    results = payload.get("sessions") if isinstance(payload, dict) else None
                    if not isinstance(results, list) or len(results) != len(expected):
                        raise ValueError("Invalid harness recovery response")
                    normalized: dict[str, dict[str, Any]] = {}
                    for result in results:
                        if not isinstance(result, dict) or result.get("sessionHash") not in expected:
                            raise ValueError("Unexpected harness recovery identity")
                        session_hash = result["sessionHash"]
                        if session_hash in normalized:
                            raise ValueError("Duplicate harness recovery identity")
                        flags = ("quitReturned", "absentVerified", "presentVerified", "alreadyAbsent")
                        if any(type(result.get(flag)) is not bool for flag in flags):
                            raise ValueError("Invalid harness recovery evidence")
                        if (result["absentVerified"] and result["presentVerified"]) or (
                            result["alreadyAbsent"] and (not result["absentVerified"] or result["quitReturned"])
                        ):
                            raise ValueError("Contradictory harness recovery evidence")
                        errors = result.get("errors")
                        if not isinstance(errors, list) or any(
                            not isinstance(error, dict)
                            or error.get("phase") not in {"attach", "probe", "quit", "verify"}
                            or not isinstance(error.get("error"), str)
                            or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,79}", error["error"])
                            for error in errors
                        ):
                            raise ValueError("Invalid harness recovery errors")
                        normalized[session_hash] = {
                            "sessionHash": session_hash,
                            **{flag: result[flag] for flag in flags},
                            "errors": [{"phase": error["phase"], "error": error["error"]} for error in errors],
                        }
                except Exception as exc:
                    normalized = {
                        session_hash: {
                            "sessionHash": session_hash, "quitReturned": False,
                            "absentVerified": False, "presentVerified": False,
                            "alreadyAbsent": False,
                            "errors": [{"phase": "execute", "error": type(exc).__name__}],
                        }
                        for session_hash in expected
                    }
                with self._lock:
                    for session_hash, result in normalized.items():
                        previous = self._recovery_results.get(session_hash)
                        if previous is not None:
                            result["errors"] = previous["errors"] + result["errors"]
                        self._recovery_results[session_hash] = result
                        if result["absentVerified"]:
                            self._active_owned.discard(expected[session_hash])
                            if result["quitReturned"]:
                                self._reclaimed.add(expected[session_hash])
            return self._recovery_report()

    def _recovery_report(self) -> dict[str, Any]:
        audit = self.audit()
        with self._lock:
            results = [
                {**result, "errors": [dict(error) for error in result["errors"]]}
                for _, result in sorted(self._recovery_results.items())
            ]
        if any(result["presentVerified"] for result in results):
            status = "leaked"
        elif (
            audit["pendingRequestCount"] or audit["unknownCreationOutcomeCount"]
            or audit["activeSessionCount"]
            # Absence alone does not establish an idle timeout or its actor.
            or any(not result["absentVerified"] or not result["quitReturned"] for result in results)
        ):
            status = "unknown"
        elif audit["reclaimedSessionCount"]:
            status = "harness_reclaimed"
        else:
            status = "not_needed" if audit["createdSessionCount"] else "not_created"
        return {
            "status": status,
            "ownedSessionCount": audit["ownedSessionCount"],
            "attemptedSessionCount": len(results),
            "reclaimedSessionCount": audit["reclaimedSessionCount"],
            "reclaimedSessionHashes": audit["reclaimedSessionHashes"],
            "activeSessionCount": audit["activeSessionCount"],
            "pendingRequestCount": audit["pendingRequestCount"],
            "pendingCreateCount": audit["pendingCreateCount"],
            "unknownCreationOutcomeCount": audit["unknownCreationOutcomeCount"],
            "sessions": results,
        }

    def _deny(self, reason: str) -> None:
        # Never retain raw paths, session/element IDs, scripts or request bodies.
        with self._lock:
            self._denials.append({"reason": reason})

    def _authorize(self, method: str, path: str, body: bytes | None) -> dict[str, Any] | None:
        parts = _parts(path)
        if parts == ["session"] and method == "POST":
            _validate_session(_object(body), self._expected_udid)
            if self._deadlines is not None and self._deadlines.expired("business"):
                raise _Denied("session not created", "Episode business deadline expired", 500)
            with self._lock:
                if self._session_attempted:
                    raise _Denied("session not created", "Only one task-owned session creation is supported", 500)
                # A lost create response may still have created a real session.
                self._session_attempted = True
            return None
        if method == "GET" and parts == ["status"]:
            return None
        if len(parts) < 2 or parts[0] != "session":
            raise _Denied("unsupported operation", "Unsupported Appium command")
        with self._lock:
            if parts[1] not in self._active_owned:
                raise _Denied("invalid session id", "Command does not address an active task-owned session", 404)
        route = "/".join(parts[2:])
        if not route and method == "DELETE":
            return None
        if method == "GET" and (
            route in _READ_ROUTES
            or re.fullmatch(r"element/[^/]+/(?:text|name|rect|size|location|enabled|displayed|selected|screenshot|computedrole|computedlabel)", route)
            or re.fullmatch(r"element/[^/]+/(?:attribute|property)/[^/]+", route)
        ):
            return None
        if method != "POST":
            raise _Denied("unsupported operation", "Unsupported or opaque Appium mutation")
        payload = _object(body)
        if route in {"element", "elements"} or re.fullmatch(r"element/[^/]+/elements?", route):
            using = payload.get("using")
            if not isinstance(using, str):
                raise _Denied("invalid argument", "Invalid locator strategy")
            if using == "-android uiautomator":
                selector = payload.get("value")
                if not isinstance(selector, str) or not _PURE_SELECTOR.fullmatch(selector):
                    raise _Denied("unsupported operation", "Only pure UiSelector observations are supported; scrolling searches consume multiple interactions")
            elif using not in {"id", "accessibility id", "class name", "xpath", "name", "tag name", "css selector", "link text", "partial link text"}:
                raise _Denied("unsupported operation", "Unsupported locator strategy")
            return None
        if route in _READ_POST or route in {"timeouts", "timeouts/implicit_wait"}:
            return None
        if route in {"context", "appium/context"}:
            if payload.get("name") != "NATIVE_APP":
                raise _Denied("unsupported operation", "Only native Android context is supported")
            return None
        template = "/session/:sessionId/" + route
        match = re.fullmatch(r"element/[^/]+/(click|clear|value)", route)
        if match:
            kind = {"click": "click", "clear": "clear", "value": "input"}[match[1]]
            template = "/session/:sessionId/element/:elementId/" + match[1]
        elif route in _UI_ROUTES:
            kind = _UI_ROUTES[route]
        elif route == "actions":
            _validate_actions(payload)
            kind = "actions"
        elif route == "execute/sync":
            script = payload.get("script")
            if not isinstance(script, str) or not script.startswith("mobile: "):
                raise _Denied("unsupported operation", "Arbitrary execute scripts are not supported")
            name = script.removeprefix("mobile: ")
            args = payload.get("args", [])
            if not isinstance(args, list) or len(args) > 1 or (args and not isinstance(args[0], dict)):
                raise _Denied("unsupported operation", "One named mobile command is required")
            if name in _READ_MOBILE:
                return None
            if name not in _UI_MOBILE:
                raise _Denied("unsupported operation", "Unsupported or opaque mobile command")
            _validate_gesture(name, args[0] if args else {})
            kind = "mobile: " + name
        else:
            raise _Denied("unsupported operation", "Unsupported or opaque Appium mutation")
        return {"kind": kind, "path": template}

    def _observe(self, method: str, path: str, status: int, body: bytes) -> None:
        try:
            parts = _parts(path)
        except _Denied:
            return
        if status >= 400:
            with self._lock:
                if method == "POST" and parts == ["session"] and status >= 500:
                    self._unknown_creations.append("SessionCreationFailedWithoutIdentity")
                elif method == "DELETE" and len(parts) == 2 and parts[0] == "session":
                    self._errors.append("SessionQuitFailed")
            return
        if method == "POST" and parts == ["session"]:
            try:
                payload = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                with self._lock:
                    self._errors.append("InvalidSessionResponse")
                    self._unknown_creations.append("InvalidSessionResponse")
                return
            value = payload.get("value") if isinstance(payload, dict) else None
            session_id = value.get("sessionId") if isinstance(value, dict) else None
            if session_id is None and isinstance(payload, dict):
                session_id = payload.get("sessionId")
            with self._lock:
                if isinstance(session_id, str) and session_id:
                    if session_id not in self._owned:
                        self._created.append(session_id)
                        self._owned.add(session_id)
                        self._active_owned.add(session_id)
                else:
                    self._errors.append("MissingCreatedSessionId")
                    self._unknown_creations.append("MissingCreatedSessionId")
        elif method == "DELETE" and len(parts) == 2 and parts[0] == "session":
            with self._lock:
                self._deleted.append(parts[1])
                self._active_owned.discard(parts[1])

    def audit(self) -> dict[str, Any]:
        with self._lock:
            created = list(self._created)
            deleted = list(self._deleted)
            errors = list(self._errors)
            denials = [dict(value) for value in self._denials]
            active = sorted(self._active_owned)
            reclaimed = sorted(self._reclaimed)
            pending_requests = len(self._pending)
            pending_creates = sum(request["creating"] for request in self._pending.values())
            unknown_creations = list(self._unknown_creations)

        def digest(value: str) -> str:
            return hashlib.sha256(value.encode()).hexdigest()

        return {
            "createdSessionCount": len(created),
            "createdSessionHashes": [digest(value) for value in created],
            "deletedSessionCount": len(deleted),
            "deletedSessionHashes": [digest(value) for value in deleted],
            "ownedSessionCount": len(created),
            "activeSessionCount": len(active),
            "activeSessionHashes": [digest(value) for value in active],
            "reclaimedSessionCount": len(reclaimed),
            "reclaimedSessionHashes": [digest(value) for value in reclaimed],
            "pendingRequestCount": pending_requests,
            "pendingCreateCount": pending_creates,
            "unknownCreationOutcomeCount": len(unknown_creations),
            "unknownCreationOutcomes": unknown_creations,
            "errors": errors,
            "deniedCommandCount": len(denials),
            "deniedCommands": denials,
        }
