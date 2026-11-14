"""Explicit current-stack release pins; no device access or dependency repair."""

from __future__ import annotations

from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any
from urllib.parse import urlparse
from zipfile import BadZipFile, ZipFile

SOURCE_MANIFEST_SHA256 = "2345c5af27c75f7c1a7c6e263b77963f426864a6486a51e845468430a50ea856"
CURRENT_STACK_FIELDS = frozenset({
    "amkernelVersion", "amkernelExecutableSha256", "ompVersion", "ompExecutableSha256",
    "installedAgentAssetsSha256", "skillMetadataSha256", "skillRuntimeVersion",
    "officialSkillManifestSha256", "officialSkillArchiveSha256", "officialSkillSourceCommit",
})


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(c in "0123456789abcdef" for c in value)


def load_migration(path: Path) -> dict[str, Any]:
    path = path.resolve(strict=True)
    payload = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(payload).hexdigest(),
            "approval": json.loads(payload)}


def _wheel_metadata(wheel: ZipFile, version: str) -> None:
    names = wheel.namelist()
    metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
    if len(set(names)) != len(names) or len(metadata_names) != 1:
        raise ValueError("release wheel has duplicate members or ambiguous metadata")
    metadata = BytesParser().parsebytes(wheel.read(metadata_names[0]))
    if metadata["Name"] != "amkernel" or metadata["Version"] != version:
        raise ValueError("release wheel metadata does not match the approved version")


def validate_migration(
    frozen: dict[str, Any], observed: dict[str, Any], migration: dict[str, Any],
) -> None:
    """Check exact approved pins and deny all non-allowlisted identity changes."""
    if not isinstance(migration, dict) or set(migration) != {"path", "sha256", "approval"}:
        raise ValueError("runtime migration reference is malformed")
    path = migration["path"]
    if not isinstance(path, str) or not Path(path).is_absolute() or load_migration(Path(path)) != migration:
        raise ValueError("runtime migration approval identity mismatch")
    approval = migration["approval"]
    if not isinstance(approval, dict) or set(approval) != {
        "schemaVersion", "comparison", "harnessRevision", "sourceManifestSha256", "runtimeIdentity", "release",
    }:
        raise ValueError("runtime migration approval schema mismatch")
    if (type(approval["schemaVersion"]) is not int or approval["schemaVersion"] != 1
            or approval["comparison"] != "current_stack"
            or type(approval["harnessRevision"]) is not int or approval["harnessRevision"] != 15
            or approval["sourceManifestSha256"] != SOURCE_MANIFEST_SHA256):
        raise ValueError("runtime migration is not the approved current_stack r15 comparison")
    target = approval["runtimeIdentity"]
    if not isinstance(target, dict) or set(target) != set(frozen) or target != observed:
        raise ValueError("runtime migration target identity mismatch")
    changes = {key for key in frozen if frozen[key] != target[key]} - {"harnessSourceSha256"}
    if changes - CURRENT_STACK_FIELDS:
        raise ValueError(f"runtime migration forbids unrelated drift: {sorted(changes - CURRENT_STACK_FIELDS)}")
    if target.get("ompVersion") != "omp/18.18.3":
        raise ValueError("current_stack requires OMP 18.18.3")
    release = approval["release"]
    if not isinstance(release, dict) or set(release) != {
        "version", "artifactUrl", "artifactPath", "artifactSha256", "sourceCommit", "runtime",
    }:
        raise ValueError("runtime migration release schema mismatch")
    version = release["version"]
    if (not isinstance(version, str) or not version.strip() or version == frozen.get("amkernelVersion")
            or target.get("amkernelVersion") != version or target.get("skillRuntimeVersion") != version):
        raise ValueError("runtime migration requires the new published version and matching Skills")
    runtime = release["runtime"]
    if (not isinstance(runtime, dict) or set(runtime) != {"pythonVersion", "dependencies"}
            or not isinstance(runtime["pythonVersion"], str) or not runtime["pythonVersion"]
            or not isinstance(runtime["dependencies"], list) or not runtime["dependencies"]):
        raise ValueError("release Runtime Python and dependency pins are required")
    url = urlparse(release["artifactUrl"]) if isinstance(release["artifactUrl"], str) else None
    if url is None or url.scheme != "https" or not url.netloc or url.username or url.password or url.fragment:
        raise ValueError("release artifact must have a public HTTPS source URL")
    if not _hex(release["artifactSha256"], 64) or not _hex(release["sourceCommit"], 40):
        raise ValueError("release artifact digest or source commit is invalid")
    artifact = release["artifactPath"]
    if (not isinstance(artifact, str) or not Path(artifact).is_absolute()
            or Path(artifact).suffix != ".whl" or _digest(Path(artifact)) != release["artifactSha256"]):
        raise ValueError("release wheel identity mismatch")
    try:
        with ZipFile(artifact) as wheel:
            _wheel_metadata(wheel, version)
    except BadZipFile as exc:
        raise ValueError("release artifact is not a valid wheel") from exc


# Run only metadata/file reads in the launcher's own interpreter, not the evaluator
# venv, and do not import AMKernel or create a Runtime/Appium session.
_PACKAGE_PROBE = """
import hashlib, importlib.metadata as md, json
from pathlib import Path
import sys
package = md.distribution('amkernel')
root = Path(package.locate_file('amkernel'))
files = {}
for path in root.rglob('*'):
    if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
        files['amkernel/' + path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
dependencies = sorted([{'name': d.metadata['Name'], 'version': d.version} for d in md.distributions()], key=lambda d: d['name'].lower())
print(json.dumps({'version': package.version, 'root': str(root.resolve()), 'files': files,
                  'runtime': {'pythonVersion': sys.version, 'dependencies': dependencies}}))
"""


def verify_release(project: Path, migration: dict[str, Any]) -> None:
    """Prove PATH/MCP, installed package and installed Skills match the pinned wheel."""
    release = migration["approval"]["release"]
    command = shutil.which("amkernel")
    if command is None:
        raise ValueError("release launcher is unavailable")
    launcher = Path(command).resolve(strict=True)
    entry = json.loads((project / ".omp/mcp.json").read_text())["mcpServers"]["amkernel"]
    if (entry.get("type", "stdio") != "stdio" or entry.get("args")
            or Path(entry["command"]).resolve() != launcher):
        raise ValueError("project MCP and campaign PATH must bind the same release launcher")
    shebang = launcher.read_text().splitlines()[0]
    interpreter = shebang.removeprefix("#!")
    if not shebang.startswith("#!/") or not Path(interpreter).is_file():
        raise ValueError("release requires an absolute Python launcher shebang")
    completed = subprocess.run(
        [interpreter, "-I", "-B", "-c", _PACKAGE_PROBE], check=True,
        capture_output=True, text=True, timeout=30,
    )
    installed = json.loads(completed.stdout)
    if installed["runtime"] != release["runtime"]:
        raise ValueError("release Runtime Python or dependencies drifted from their exact pins")
    with ZipFile(release["artifactPath"]) as wheel:
        _wheel_metadata(wheel, release["version"])
        names = wheel.namelist()
        if installed["version"] != release["version"]:
            raise ValueError("installed package version differs from release")
        package_files = {name: hashlib.sha256(wheel.read(name)).hexdigest()
                         for name in names if name.startswith("amkernel/") and not name.endswith("/")}
        if not package_files or installed["files"] != package_files:
            raise ValueError("installed AMKernel package differs from the release wheel")
        package_root = Path(installed["root"])
        if "site-packages" not in package_root.parts:
            raise ValueError("release package must be installed, not imported from a development checkout")
        skill_root = project / ".agents/skills/amkernel"
        skill_metadata = json.loads((skill_root / ".amkernel-metadata.json").read_text())
        files = skill_metadata.get("files")
        if (skill_metadata.get("runtimeVersion") != release["version"]
                or not isinstance(files, dict) or "SKILL.md" not in files
                or "scripts/verify_official_skills.py" not in files
                or "references/official-skills.json" not in files):
            raise ValueError("release Skill metadata is incomplete or has a different version")
        actual = {p.relative_to(skill_root).as_posix() for p in skill_root.rglob("*") if p.is_file()}
        if actual != set(files) | {".amkernel-metadata.json"}:
            raise ValueError("installed AMKernel Skill has unexpected or missing files")
        for relative, digest in files.items():
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
                raise ValueError("unsafe release Skill path")
            expected = package_files.get("amkernel/skill/" + relative)
            if expected != digest or _digest(skill_root / path) != expected:
                raise ValueError(f"installed Skill differs from release wheel: {relative}")
    # Reuse the packaged fail-closed verifier for the official archive, vendor tree
    # and generated Skill copies instead of implementing another provenance scheme.
    subprocess.run(
        [interpreter, "-I", "-B", str(skill_root / "scripts/verify_official_skills.py"),
         "--project-root", str(project)], check=True, capture_output=True, text=True, timeout=30,
    )
