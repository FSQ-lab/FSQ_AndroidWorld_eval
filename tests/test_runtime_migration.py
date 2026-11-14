"""Offline migration boundaries; synthetic release fixtures never control a device."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv
from zipfile import ZipFile

import pytest

from fsq_androidworld_eval import campaign
from fsq_androidworld_eval.continuation import validate_inherited_runtime
from fsq_androidworld_eval.runtime_migration import (
    _PACKAGE_PROBE,
    load_migration, validate_migration, verify_release,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).with_name("fixtures") / "inherited_campaign.json"
VERSION = "0.0.0+test"


def _save(path, value):
    path.write_text(json.dumps(value))
    return load_migration(path)


@pytest.fixture
def release_fixture(tmp_path, monkeypatch, inherited_campaign):
    monkeypatch.setattr(sys.modules[__name__], "SOURCE", inherited_campaign)
    project = tmp_path / "project"
    project.mkdir()
    shutil.copytree(ROOT / ".agents", project / ".agents")
    for relative in (".agents/skills/amkernel/.amkernel-metadata.json", ".agents/amkernel-official.json"):
        path = project / relative
        value = json.loads(path.read_text())
        value["runtimeVersion"] = VERSION
        path.write_text(json.dumps(value))
    runtime = tmp_path / "runtime"
    venv.EnvBuilder(with_pip=False).create(runtime)
    python = runtime / "bin/python"
    site = Path(subprocess.check_output([str(python), "-I", "-c",
                                       "import sysconfig; print(sysconfig.get_path('purelib'))"], text=True).strip())
    artifact = tmp_path / "amkernel-test.whl"
    skill_root = project / ".agents/skills/amkernel"
    package_files = {
        "amkernel/__init__.py": f"__version__ = {VERSION!r}\n".encode(),
        "amkernel/runtime.py": b'"""Synthetic package bytes for provenance checks."""\n',
        **{"amkernel/skill/" + p.relative_to(skill_root).as_posix(): p.read_bytes()
           for p in skill_root.rglob("*") if p.is_file() and p.name != ".amkernel-metadata.json"},
    }
    with ZipFile(artifact, "w") as wheel:
        for name, payload in package_files.items():
            wheel.writestr(name, payload)
            target = site / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        metadata = f"Name: amkernel\nVersion: {VERSION}\n".encode()
        name = f"amkernel-{VERSION}.dist-info/METADATA"
        wheel.writestr(name, metadata)
        (site / name).parent.mkdir(parents=True)
        (site / name).write_bytes(metadata)
    launcher = runtime / "bin/amkernel"
    launcher.write_text(f"#!{python}\nimport sys\nprint('amkernel {VERSION}')\n")
    launcher.chmod(0o755)
    monkeypatch.setenv("PATH", str(launcher.parent) + os.pathsep + os.environ["PATH"])
    (project / ".omp").mkdir()
    (project / ".omp/mcp.json").write_text(json.dumps({"mcpServers": {"amkernel": {
        "command": str(launcher), "cwd": str(project), "type": "stdio",
    }}}))
    frozen = json.loads(SOURCE.read_text())["protocol"]["runtimeIdentity"]
    target = json.loads(json.dumps(frozen))
    target.update(amkernelVersion=VERSION, skillRuntimeVersion=VERSION,
                  amkernelExecutableSha256=hashlib.sha256(launcher.read_bytes()).hexdigest(),
                  ompVersion="omp/18.18.3", ompExecutableSha256="e" * 64,
                  harnessSourceSha256="f" * 64)
    probe = json.loads(subprocess.check_output([str(python), "-I", "-B", "-c", _PACKAGE_PROBE], text=True))
    approval = {"schemaVersion": 1, "comparison": "current_stack", "harnessRevision": 15,
                "sourceManifestSha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "runtimeIdentity": target,
                "release": {"version": VERSION, "artifactUrl": "https://example.invalid/amkernel-test.whl",
                            "artifactPath": str(artifact), "artifactSha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                            "sourceCommit": "a" * 40, "runtime": probe["runtime"]}}
    approval_path = tmp_path / "approval.json"
    return project, frozen, target, approval_path, approval, site


def test_approved_omp_version_still_rejects_post_pin_binary_drift(release_fixture):
    _, frozen, target, path, approval, _ = release_fixture
    migration = _save(path, approval)
    changed = {**target, "ompExecutableSha256": "0" * 64}
    with pytest.raises(ValueError, match="target identity mismatch"):
        validate_migration(frozen, changed, migration)


def test_approval_cannot_authorize_unrelated_evaluator_dependency_drift(release_fixture):
    _, frozen, target, path, approval, _ = release_fixture
    target["harnessDependencies"] = [{"name": "unapproved", "version": "1"}]
    with pytest.raises(ValueError, match="forbids unrelated drift"):
        validate_migration(frozen, target, _save(path, approval))


def test_legacy_inheritance_does_not_silently_opt_in(release_fixture):
    _, frozen, target, path, approval, _ = release_fixture
    with pytest.raises(ValueError, match="frozen runtime mismatch"):
        validate_inherited_runtime({"protocol": {"runtimeIdentity": frozen}}, target)
    validate_migration(frozen, target, _save(path, approval))


@pytest.mark.parametrize("mutation", ["approval_bytes", "wheel_bytes", "old_version", "wrong_omp", "extra_field"])
def test_release_approval_and_artifact_are_immutable(release_fixture, mutation):
    _, frozen, target, path, approval, _ = release_fixture
    if mutation == "old_version":
        approval["release"]["version"] = frozen["amkernelVersion"]
    elif mutation == "wrong_omp":
        target["ompVersion"] = "omp/18.19.0"
    elif mutation == "extra_field":
        approval["allowAnyRuntime"] = True
    migration = _save(path, approval)
    if mutation == "approval_bytes":
        path.write_bytes(path.read_bytes() + b"\n")
    elif mutation == "wheel_bytes":
        Path(approval["release"]["artifactPath"]).write_bytes(b"replaced")
    with pytest.raises(ValueError):
        validate_migration(frozen, target, migration)


@pytest.mark.parametrize("mutation", ["package", "skill", "official_copy", "mcp", "dependency"])
def test_release_verification_rejects_mixed_or_modified_installations(release_fixture, mutation):
    project, _, _, path, approval, site = release_fixture
    migration = _save(path, approval)
    if mutation == "package":
        (site / "amkernel/runtime.py").write_text("changed package")
    elif mutation == "skill":
        (project / ".agents/skills/amkernel/SKILL.md").write_text("changed Skill")
    elif mutation == "official_copy":
        (project / ".agents/skills/setup-uiautomator2/SKILL.md").write_text("changed official copy")
    elif mutation == "mcp":
        (project / ".omp/mcp.json").write_text(json.dumps({"mcpServers": {"amkernel": {"command": sys.executable}}}))
    else:
        extra = site / "unapproved-1.dist-info"
        extra.mkdir()
        (extra / "METADATA").write_text("Name: unapproved\nVersion: 1\n")
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        verify_release(project, migration)


@pytest.mark.parametrize("kind", ["rehearsal", "calibration", "full"])
def test_current_stack_inherits_exact_specs_and_revalidates_release(release_fixture, monkeypatch, kind):
    project, frozen, target, path, approval, _ = release_fixture
    _save(path, approval)
    monkeypatch.setattr(campaign, "_runtime_identity", lambda _: json.loads(json.dumps(target)))
    assets = json.loads((SOURCE).read_text())["protocol"]["environmentArtifacts"]
    # This fixture retains the frozen asset set; unrelated artifact migrations
    # remain covered by the existing named-forwarder contract tests.
    from fsq_androidworld_eval.appium_proxy import SESSION_ACCESSIBILITY_CONFIG
    helper = next(a for a in assets["artifacts"] if a["name"] == SESSION_ACCESSIBILITY_CONFIG["inheritedForwarderArtifactName"])
    helper.update(name=SESSION_ACCESSIBILITY_CONFIG["forwarderArtifactName"], sha256="d" * 64,
                  sizeBytes=1234, url="repo:assets/fsq-accessibility-forwarder-lifecycle-v1.apk")
    monkeypatch.setattr(campaign, "artifact_identity", lambda _: assets)
    monkeypatch.setattr(campaign, "_calibration_gate", lambda *_: {
        "campaignId": "fixture-calibration", "manifestSha256": "1" * 64,
        "summaryIdentitySha256": "2" * 64, "evidenceSha256": "3" * 64,
    })
    output = project / "manifest.json"
    campaign.write_manifest(output, "fixture-current-stack", kind, project,
                            project / "calibration" if kind == "full" else None,
                            SOURCE, runtime_migration=path)
    manifest = campaign._load_manifest(output, project)
    source = json.loads(SOURCE.read_text())
    expected = source["tasks"]
    if kind == "calibration":
        by_name = {t["name"]: t for t in expected}
        expected = [{**by_name[name], "index": i} for i, name in enumerate(campaign.CALIBRATION_TASKS)]
    assert manifest["tasks"] == expected
    for key in ("model", "taskRandomSeed", "nTaskCombinations", "useIdenticalParams", "stepBudget", "timeBudget"):
        assert manifest["protocol"][key] == source["protocol"][key]
    (project / ".agents/skills/amkernel/SKILL.md").write_text("changed after prepare")
    with pytest.raises(ValueError, match="Skill differs"):
        campaign._load_manifest(output, project)


def test_migration_cannot_regenerate_task_parameters(release_fixture):
    project, _, _, path, approval, _ = release_fixture
    _save(path, approval)
    output = project / "uncreated/manifest.json"
    with pytest.raises(ValueError, match="requires the exact inherited"):
        campaign.write_manifest(output, "no-inheritance", project=project, runtime_migration=path)
    assert not output.parent.exists()
