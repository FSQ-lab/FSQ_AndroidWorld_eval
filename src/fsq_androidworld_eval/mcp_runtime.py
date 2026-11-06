"""Bounded stdio MCP access for episode-owned recovery, never a task agent.

A fresh connection owns a fresh Runtime. It cannot recover old Python objects;
callers may attach only to session identities already confirmed by the proxy.
"""

from __future__ import annotations

import json
from pathlib import Path
from queue import Empty, Queue
import subprocess
from threading import Thread
from time import monotonic
from typing import Any


class RecoveryRuntime:
    def __init__(self, project: Path, timeout_seconds: float = 120) -> None:
        entry = json.loads((project / ".omp/mcp.json").read_text())["mcpServers"]["amkernel"]
        if entry.get("type", "stdio") != "stdio":
            raise ValueError("Recovery requires the frozen stdio AMKernel transport")
        self._command = [entry["command"], *entry.get("args", [])]
        self._cwd = entry.get("cwd", str(project))
        self._deadline = monotonic() + timeout_seconds
        self._messages: Queue[dict[str, Any] | None] = Queue()
        self._sequence = 0
        self._process: subprocess.Popen | None = None

    def _read_messages(self) -> None:
        assert self._process is not None and self._process.stdout is not None
        try:
            for line in self._process.stdout:
                try:
                    value = json.loads(line)
                except ValueError:
                    continue
                if isinstance(value, dict):
                    self._messages.put(value)
        finally:
            self._messages.put(None)

    def _send(self, value: dict[str, Any]) -> None:
        assert self._process is not None and self._process.stdin is not None
        self._process.stdin.write(json.dumps({"jsonrpc": "2.0", **value}) + "\n")
        self._process.stdin.flush()

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._sequence += 1
        identifier = self._sequence
        self._send({"id": identifier, "method": method, "params": params})
        while True:
            try:
                message = self._messages.get(timeout=max(0, self._deadline - monotonic()))
            except Empty:
                raise TimeoutError("AMKernel recovery transport deadline exhausted") from None
            if message is None:
                raise RuntimeError("AMKernel recovery transport exited before replying")
            if message.get("id") != identifier:
                continue
            if "error" in message:
                raise RuntimeError("AMKernel recovery JSON-RPC request failed")
            return message["result"]

    def __enter__(self) -> RecoveryRuntime:
        self._process = subprocess.Popen(
            self._command, cwd=self._cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1,
        )
        self._reader = Thread(target=self._read_messages, daemon=True)
        self._reader.start()
        try:
            self._request("initialize", {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "fsq-episode-recovery", "version": "8"},
            })
            self._send({"method": "notifications/initialized", "params": {}})
            tools = self._request("tools/list", {})["tools"]
            self._tool_name = next(tool["name"] for tool in tools if tool["name"] == "python_exec")
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def execute(self, code: str, timeout_seconds: float) -> dict[str, Any]:
        remaining = min(timeout_seconds, self._deadline - monotonic())
        if remaining <= 1:
            raise TimeoutError("No recovery execution window remains")
        result = self._request("tools/call", {
            "name": self._tool_name,
            "arguments": {"code": code, "timeout": max(1, int(remaining - 1))},
        })
        for item in result.get("content", []):
            if item.get("type") != "text":
                continue
            payload = json.loads(item["text"])
            if payload.get("status") != "completed" or payload.get("kernelState") != "alive":
                raise RuntimeError("AMKernel recovery execution did not complete in a live Kernel")
            value = payload.get("result")
            if isinstance(value, dict):
                return value
        raise RuntimeError("AMKernel recovery returned no structured evidence")

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._process is None:
            return
        if self._process.stdin is not None:
            self._process.stdin.close()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2)
        self._reader.join(timeout=1)
