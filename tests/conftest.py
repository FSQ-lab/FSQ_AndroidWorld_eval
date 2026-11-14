"""Offline campaign inputs; never depend on private campaign directories."""

import hashlib
import json
from pathlib import Path

import pytest


@pytest.fixture
def inherited_campaign(tmp_path, monkeypatch):
    from fsq_androidworld_eval import campaign, continuation, runtime_migration, scorer

    source = json.loads((Path(__file__).with_name("fixtures") / "inherited_campaign.json").read_text())
    # Freeze this test's installed metadata, not a historical machine's SDK.
    metadata = Path(campaign.registry.__file__).with_name("task_metadata.json")
    source["protocol"]["taskMetadataSha256"] = hashlib.sha256(metadata.read_bytes()).hexdigest()
    payload = json.dumps(source, sort_keys=True).encode()
    path = tmp_path / "inherited-source.json"
    path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    monkeypatch.setattr(continuation, "INHERITED_MANIFEST_SHA256", digest)
    monkeypatch.setattr(scorer, "INHERITED_MANIFEST_SHA256", digest)
    monkeypatch.setattr(runtime_migration, "SOURCE_MANIFEST_SHA256", digest)
    return path
