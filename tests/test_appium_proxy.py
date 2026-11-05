from http import server as http_server
import json
import socket
import struct
from threading import Thread
import time
from urllib.parse import urlsplit


from fsq_androidworld_eval.appium_proxy import AppiumAuditProxy


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
    assert len(set(audit["createdSessionHashes"])) == 2
    assert audit["deletedSessionHashes"] == [audit["createdSessionHashes"][0]]


def test_audit_records_malformed_session_creation_response() -> None:
    with AppiumAuditProxy("http://127.0.0.1:4723") as proxy:
        proxy._observe("POST", "/wd/hub/session", 200, b"not-json")
        audit = proxy.audit()

    assert audit["createdSessionCount"] == 0
    assert audit["errors"] == ["InvalidSessionResponse"]


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
