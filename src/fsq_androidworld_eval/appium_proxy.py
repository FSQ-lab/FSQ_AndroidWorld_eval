from __future__ import annotations

import hashlib
from http import client as http_client
from http import server as http_server
import json
from threading import Lock, Thread
from typing import Any
from urllib.parse import urlsplit


class AppiumAuditProxy:
    def __init__(self, upstream_url: str):
        upstream = urlsplit(upstream_url)
        if upstream.scheme != "http" or not upstream.hostname:
            raise ValueError("Appium audit proxy requires an http upstream URL")
        self._host = upstream.hostname
        self._port = upstream.port or 80
        self._base_path = upstream.path.rstrip("/")
        self._lock = Lock()
        self._created: list[str] = []
        self._deleted: list[str] = []
        self._errors: list[str] = []
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

            def _forward(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length) if length else None
                headers = {
                    key: value
                    for key, value in self.headers.items()
                    if key.lower() not in {"host", "connection", "content-length"}
                }
                connection = http_client.HTTPConnection(owner._host, owner._port, timeout=60)
                path = owner._base_path + self.path
                try:
                    connection.request(self.command, path, body=body, headers=headers)
                    response = connection.getresponse()
                    response_body = response.read()
                    response_headers = response.getheaders()
                except Exception as exc:
                    with owner._lock:
                        owner._errors.append(type(exc).__name__)
                    payload = json.dumps(
                        {"value": {"error": "proxy error", "message": type(exc).__name__}}
                    ).encode()
                    try:
                        self.send_response(502)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(payload)))
                        self.end_headers()
                        self.wfile.write(payload)
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                    return
                finally:
                    connection.close()
                owner._observe(self.command, self.path, response.status, response_body)
                try:
                    self.send_response(response.status)
                    for key, value in response_headers:
                        if key.lower() not in {
                            "connection",
                            "content-length",
                            "transfer-encoding",
                        }:
                            self.send_header(key, value)
                    self.send_header("Content-Length", str(len(response_body)))
                    self.end_headers()
                    self.wfile.write(response_body)
                except (BrokenPipeError, ConnectionResetError):
                    # The upstream response was observed completely. A caller that times
                    # out while receiving it does not invalidate the session audit.
                    pass

            def log_message(self, format: str, *args: Any) -> None:
                return

        self._server = http_server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> AppiumAuditProxy:
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)

    def _observe(self, method: str, path: str, status: int, body: bytes) -> None:
        if status >= 400:
            return
        normalized_path = path.rstrip("/")
        if method == "POST" and normalized_path.endswith("/session"):
            try:
                payload = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                with self._lock:
                    self._errors.append("InvalidSessionResponse")
                return
            value = payload.get("value") if isinstance(payload, dict) else None
            session_id = None
            if isinstance(value, dict):
                session_id = value.get("sessionId")
            if session_id is None and isinstance(payload, dict):
                session_id = payload.get("sessionId")
            with self._lock:
                if isinstance(session_id, str):
                    self._created.append(session_id)
                else:
                    self._errors.append("MissingCreatedSessionId")
        elif method == "DELETE" and "/session/" in normalized_path:
            session_id = normalized_path.rsplit("/session/", 1)[-1].split("/", 1)[0]
            if session_id:
                with self._lock:
                    self._deleted.append(session_id)

    def audit(self) -> dict[str, Any]:
        with self._lock:
            created = list(self._created)
            deleted = list(self._deleted)
            errors = list(self._errors)

        def digest(value: str) -> str:
            return hashlib.sha256(value.encode()).hexdigest()

        return {
            "createdSessionCount": len(created),
            "createdSessionHashes": [digest(value) for value in created],
            "deletedSessionCount": len(deleted),
            "deletedSessionHashes": [digest(value) for value in deleted],
            "errors": errors,
        }
