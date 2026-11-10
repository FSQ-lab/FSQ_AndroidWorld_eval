"""Private, bounded observations of the existing scalar evaluator call.

Logger filters observe records without changing handlers, levels, propagation or
formatting. Only the evaluator thread is captured. No task/DB introspection and no
extra stringification of evaluator-owned objects: templates and bounded literal
arguments are evidence, not reconstructed messages or inferred component scores.
"""

import hashlib
from itertools import islice
import json
import logging
import math
import os
from pathlib import Path
import threading
import time
from typing import Any

from absl import logging as absl_logging


MAX_RECEIPT_BYTES = 64 * 1024
MAX_LOG_BYTES = 48 * 1024
MAX_LOG_RECORDS = 256
MAX_VALUE_CHARS = 2048
MAX_ITEMS = 8
MAX_DEPTH = 3
MAX_VALUE_NODES = 64
MAX_EXCEPTION_FRAMES = 16
MAX_TYPE_NAME_CHARS = 128
RECEIPT_PATH = "raw-private/evaluator-diagnostics.json"

# stdlib dispatch iterates its current list without taking an update lock.
# Never mutate that list: in-flight dispatch must retain its original snapshot.
_FILTER_UPDATE_LOCK = threading.Lock()
_TYPE_NAME = type.__dict__["__name__"]


def bounded_type_name(value: Any, *, budget: list[int] | None = None) -> tuple[str, int]:
    """Return builtin type metadata without metaclass attribute/equality hooks.

    Read the name by reference, then slice before copying or JSON encoding. Even
    str subclasses cannot override these builtin length/slicing operations.
    """
    name = _TYPE_NAME.__get__(type(value))
    length = str.__len__(name)
    count = min(length, MAX_TYPE_NAME_CHARS, budget[1] if budget is not None else MAX_TYPE_NAME_CHARS)
    if budget is not None:
        budget[1] -= count
    return str.__getitem__(name, slice(0, count)), length - count


class EvaluatorDiagnostics(logging.Filter):
    """Best-effort sidecar; failures must never replace evaluator outcomes."""

    def __init__(self, output_dir: Path, *, task_name: str, params_sha256: str):
        super().__init__()
        self.output_dir = output_dir
        self.task_name = task_name[:256]
        self.params_sha256 = params_sha256
        self.reward: Any = None
        self.reference: dict[str, Any] = {"status": "not_written"}
        self._logs: list[dict[str, Any]] = []
        self._log_bytes = 0
        self._dropped = 0
        self._omitted = 0
        self._capture_errors = 0
        self._attached: list[logging.Logger] = []
        self._active = False

    def _name(self, value: Any, budget: list[int] | None = None) -> str:
        name, omitted = bounded_type_name(value, budget=budget)
        self._omitted += bool(omitted)
        return name

    def _value(self, value: Any, depth: int = 0, budget: list[int] | None = None) -> Any:
        if budget is None:
            budget = [MAX_VALUE_NODES, MAX_VALUE_CHARS]
        kind = type(value)
        if budget[0] <= 0:
            self._omitted += 1
            return {"omittedType": self._name(value, budget), "reason": "node_limit"}
        budget[0] -= 1
        if value is None or kind is bool:
            return value
        if kind is str:
            count = min(len(value), budget[1])
            budget[1] -= count
            if count == len(value):
                return value
            self._omitted += 1
            return {"prefix": value[:count], "omittedCharacters": len(value) - count}
        if kind is int and value.bit_length() <= 256:
            return value
        if kind is float and math.isfinite(value):
            return value
        if (kind is tuple or kind is list or kind is dict) and depth < MAX_DEPTH:
            name = self._name(value, budget)
            if kind is dict:
                items = [[self._value(k, depth + 1, budget), self._value(v, depth + 1, budget)]
                         for k, v in islice(value.items(), MAX_ITEMS)]
            else:
                items = [self._value(v, depth + 1, budget) for v in value[:MAX_ITEMS]]
            omitted = max(0, len(value) - MAX_ITEMS)
            self._omitted += bool(omitted)
            return {"type": name, "items": items, "omittedItems": omitted}
        self._omitted += 1
        return {"omittedType": self._name(value, budget), "reason": "unsupported_type_or_size_or_depth"}

    def _exception(self, exc: BaseException) -> dict[str, Any]:
        # Bypass custom exception formatting and never retain frame locals.
        args = BaseException.args.__get__(exc, type(exc))
        tb = BaseException.__traceback__.__get__(exc, type(exc))
        frames = []
        while tb is not None and len(frames) < MAX_EXCEPTION_FRAMES:
            code = tb.tb_frame.f_code
            frames.append({"file": code.co_filename[-256:], "function": code.co_name[:256], "line": tb.tb_lineno})
            tb = tb.tb_next
        self._omitted += tb is not None
        budget = [MAX_VALUE_NODES, MAX_VALUE_CHARS]
        name = self._name(exc, budget)
        return {"type": name, "arguments": self._value(args, budget=budget),
                "frames": frames, "framesTruncated": tb is not None}

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._active or record.thread != self._thread_id:
            return True
        if len(self._logs) >= MAX_LOG_RECORDS or self._log_bytes >= MAX_LOG_BYTES:
            self._dropped += 1
            return True
        try:
            entry = {
                "createdAtUnix": record.created, "logger": record.name[:256],
                "level": record.levelno, "file": record.pathname[-256:],
                "function": record.funcName[:256], "line": record.lineno,
                "messageTemplate": self._value(record.msg), "arguments": self._value(record.args),
            }
            if record.exc_info and record.exc_info[1] is not None:
                entry["exception"] = self._exception(record.exc_info[1])
            size = len(json.dumps(entry, ensure_ascii=True).encode("utf-8"))
            if self._log_bytes + size > MAX_LOG_BYTES:
                self._dropped += 1
                # Stop projecting arguments once the byte budget has filled.
                self._log_bytes = MAX_LOG_BYTES
            else:
                self._logs.append(entry)
                self._log_bytes += size
        except Exception:
            self._capture_errors += 1
        return True

    def __enter__(self) -> "EvaluatorDiagnostics":
        self._thread_id = threading.get_ident()
        self._started = time.time()
        self._sources = []
        self._active = True
        for logger in (logging.getLogger(), absl_logging.get_absl_logger()):
            try:
                self._sources.append({"logger": logger.name, "effectiveLevel": logger.getEffectiveLevel()})
                with _FILTER_UPDATE_LOCK:
                    logger.filters = [*logger.filters, self]
                    self._attached.append(logger)
            except Exception:
                self._capture_errors += 1
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        ended = time.time()
        self._active = False
        for logger in self._attached:
            try:
                with _FILTER_UPDATE_LOCK:
                    logger.filters = [item for item in logger.filters if item is not self]
            except Exception:
                self._capture_errors += 1
        try:
            receipt = {
                "schemaVersion": 1, "phase": "evaluator",
                "source": "android_world.task_eval.is_successful",
                "boundary": "after_agent_exit_and_submission_before_task_teardown",
                "task": {"name": self.task_name, "paramsSha256": self.params_sha256},
                "startedAtUnix": self._started, "completedAtUnix": ended,
                "outcome": "raised" if exc is not None else "returned",
                "officialReward": self._value(self.reward),
                "exception": self._exception(exc) if exc is not None else None,
                "componentResults": {"status": "not_provided", "source": "scalar_return_interface"},
                "logCapture": {
                    "format": "python_logging_template_and_bounded_arguments",
                    "sources": self._sources, "scope": "current_thread_only",
                    "records": self._logs, "droppedRecords": self._dropped,
                    "omittedValues": self._omitted, "captureErrors": self._capture_errors,
                    "limits": {"receiptBytes": MAX_RECEIPT_BYTES, "logBytes": MAX_LOG_BYTES,
                               "logRecords": MAX_LOG_RECORDS, "valueCharacters": MAX_VALUE_CHARS,
                               "itemsPerContainer": MAX_ITEMS, "valueDepth": MAX_DEPTH,
                               "valueNodes": MAX_VALUE_NODES, "exceptionFrames": MAX_EXCEPTION_FRAMES,
                               "typeNameCharacters": MAX_TYPE_NAME_CHARS},
                },
            }
            while True:
                status = "capture_error" if self._capture_errors else "truncated" if self._dropped or self._omitted else "written"
                receipt["captureStatus"] = status
                receipt["logCapture"].update(droppedRecords=self._dropped, omittedValues=self._omitted)
                payload = (json.dumps(receipt, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")
                if len(payload) <= MAX_RECEIPT_BYTES:
                    break
                if self._logs:
                    self._logs.pop()
                    self._dropped += 1
                elif receipt["exception"] and receipt["exception"]["frames"]:
                    receipt["exception"]["frames"].pop()
                    receipt["exception"]["framesTruncated"] = True
                    self._omitted += 1
                else:
                    raise ValueError("evaluator diagnostic envelope exceeds byte bound")
            path = self.output_dir / RECEIPT_PATH
            path.parent.mkdir(mode=0o700, exist_ok=True)
            temporary = path.with_suffix(".json.tmp")
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(payload)
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
            self.reference = {"path": RECEIPT_PATH, "sha256": hashlib.sha256(payload).hexdigest(),
                              "status": status, "bytes": len(payload)}
        except Exception as error:
            # Do not expose private exception arguments, or disrupt cleanup.
            self.reference = {"status": "write_failed", "errorType": bounded_type_name(error)[0]}
        finally:
            self._logs.clear()
        return False
