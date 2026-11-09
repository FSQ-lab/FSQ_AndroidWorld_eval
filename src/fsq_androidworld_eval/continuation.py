"""Revision 12 continuation identity and immutable inherited task provenance.

Only verified recovery permits scheduling another task. It never upgrades the
original outcome, Agent cleanup attribution, reward, or scoring qualification.
Unknown cleanup and unavailable services require coordinated external recovery;
this protocol never cold-restarts a target or resumes an interrupted campaign.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fsq_androidworld_eval.runner import _sha256

CAMPAIGN_CONTINUATION = {
    "version": 2,
    "policy": "full_coverage_after_verified_recovery",
}
INHERITED_MANIFEST_SHA256 = "2345c5af27c75f7c1a7c6e263b77963f426864a6486a51e845468430a50ea856"
INHERITED_TASKS_SHA256 = "f41b2dac8a427ddd22bbe4ea04b0104ae9feea8280c9295b2fe1dfbc6671d417"


def inherited_source(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Check original bytes and exact ordered task specs before making any copy."""
    import hashlib

    path = path.resolve()
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != INHERITED_MANIFEST_SHA256:
        raise ValueError("inherited source manifest file digest mismatch")
    source = json.loads(payload)
    tasks = source.get("tasks")
    if (
        source.get("schemaVersion") != 2
        or source.get("kind") != "full"
        or source.get("protocol", {}).get("harnessRevision") != 11
        or not isinstance(tasks, list)
        or len(tasks) != 116
        or _sha256(tasks) != INHERITED_TASKS_SHA256
    ):
        raise ValueError("inherited source task specification digest mismatch")
    return source, {
        "path": str(path),
        "sha256": INHERITED_MANIFEST_SHA256,
        "tasksSha256": INHERITED_TASKS_SHA256,
        "campaignId": source["campaignId"],
        "taskCount": len(tasks),
    }


def validate_inherited_runtime(source: dict[str, Any], observed: dict[str, Any]) -> None:
    """Only this revision's harness source may differ from the frozen Runtime."""
    expected = source["protocol"]["runtimeIdentity"]
    frozen = {key: value for key, value in expected.items() if key != "harnessSourceSha256"}
    current = {key: value for key, value in observed.items() if key != "harnessSourceSha256"}
    if frozen != current:
        changed = sorted(key for key in set(frozen) | set(current) if frozen.get(key) != current.get(key))
        raise ValueError(f"inherited frozen runtime mismatch: {changed}")


def inherited_tasks(source: dict[str, Any], names: list[str] | None = None) -> list[dict[str, Any]]:
    """Copy frozen specs, changing only calibration's contiguous task indexes."""
    tasks = json.loads(json.dumps(source["tasks"]))
    if names is None:
        return tasks
    by_name = {task["name"]: task for task in tasks}
    selected = [by_name[name] for name in names]
    for index, task in enumerate(selected):
        task["index"] = index
    return selected


def cleanup_known(record: dict[str, Any]) -> bool:
    """Prove cleanup safety, not successful Agent cleanup for score purposes."""
    cleanup = record.get("cleanup")
    if not isinstance(cleanup, dict):
        return False
    if cleanup.get("taskTearDown") not in {"completed", "not_applicable"}:
        return False
    if cleanup.get("environment") not in {"closed", "not_created"}:
        return False
    session = cleanup.get("agentSession")
    if not isinstance(session, dict):
        return False
    status = session.get("status")
    if status == "closed":
        if session.get("verificationStatus") == "absent":
            return True
        from fsq_androidworld_eval.scorer import _cleanup_failed

        return isinstance(record.get("timeBudget"), dict) and not _cleanup_failed(record)
    if status == "not_created":
        if record.get("agent") is None:
            return True
        agent = record.get("agent")
        audit = record.get("appiumSessionAudit")
        return (
            isinstance(agent, dict) and agent.get("processExited") is True
            and type(agent.get("exitCode")) is int
            and session.get("attribution") == "none" and session.get("verificationStatus") == "absent"
            and isinstance(audit, dict) and audit.get("errors") == []
            and all(type(audit.get(key)) is int and audit[key] == 0 for key in (
                "createdSessionCount", "deletedSessionCount", "activeSessionCount",
                "pendingRequestCount", "pendingCreateCount", "unknownCreationOutcomeCount",
            ))
            and audit.get("createdSessionHashes") == [] and audit.get("deletedSessionHashes") == []
        )
    if status != "harness_reclaimed":
        return False
    sessions = session.get("sessions")
    return (
        session.get("attribution") == "harness"
        and session.get("verificationStatus") == "absent"
        and all(type(session.get(field)) is int and session[field] == 0 for field in (
            "pendingRequestCount", "unknownCreationOutcomeCount", "activeSessionCount"
        ))
        and isinstance(sessions, list)
        and bool(sessions)
        and all(isinstance(row, dict) and row.get("quitReturned") is True
                and row.get("absentVerified") is True for row in sessions)
    )
