"""Offline FSQ candidate freeze; no Android environment, provider, or oracle is run.

``evaluator_site`` is a NEW isolated --target site directory containing a real
AndroidWorld wheel installation plus a full copy of the corrected source package
(including generated protobuf modules and all task data). Install dependencies in
that directory too, or provide them in the evaluator interpreter. The source
package must equal the installed package byte-for-byte, excluding bytecode only.
Imports occur in a fresh ``-I -B`` evaluator subprocess with this site first; FSQ
metadata is inspected separately with its own interpreter. Neither shared .venv
nor the FSQ checkout is modified. Candidate inspection is not live qualification.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any
from urllib.parse import unquote, urlparse

from fsq_androidworld_eval.lifecycle import episode_time_budget

PROVIDER = "github_copilot"
MODEL = "gpt-6.1-sol"
SUITE_SIZE = 116
GATE_NAMES = (
    "independentReview", "nativeProviderModelAuthentication", "targetResourceOwnership",
    "deviceReadiness", "qualification", "smoke", "campaignAuthorization",
)
PROTOCOL = {
    "version": 2,
    "taskRandomSeed": 30,
    "nTaskCombinations": 1,
    "useIdenticalParams": True,
    "suiteSize": SUITE_SIZE,
    "actionBudget": {
        "formula": "int(10 * complexity)",
        "unit": "admitted_android_harness_write_capability_dispatch",
        "capabilities": ["launch_app", "kill_app", "tap_on", "tap_at", "long_press_on", "input_text", "press_key", "swipe"],
        "reservation": "atomic_before_forward; failed_attempts_not_refunded; includes_setup_and_teardown",
        "inputText": "one_composite_capability: click, optional_clear_text, set_text; not_Appium_primitive_equivalent",
        "exclusions": ["driver_construction_and_u2_connect", "implicit_u2_service_startup", "observation_and_context_backend_side_effects"],
    },
    "timeBudget": {
        "allocator": "fsq_androidworld_eval.lifecycle.episode_time_budget",
        "businessFormula": "max(600, 120 + 60 * maxSteps)",
        "cleanupWindowSeconds": 180,
        "terminationGraceSeconds": 10,
    },
    "answerProfile": {
        "version": 1,
        "name": "fsq_parsed_summary_answer",
        "source": "agent_runtime.runner.tool_output.summary",
        "runnerCount": 1,
        "runnerStatus": "success",
        "schemaVersion": "task_run_v1",
        "summaryType": "string",
        "representation": "parsed_reserialized_redacted_summary_not_original_wire_text",
        "excludedSources": ["pre_plan", "verifier"],
        "goalSuffix": None,
    },
    "lifecycle": {
        "entry": "DynamicExecutionService(FsqAgent.from_settings(...)).execute(DynamicExecutionRequest(record=False))",
        "preserve": ["original_FSQ_Skill", "original_observations", "native_uiautomator2", "original_kill_app"],
        "ordering": "official_evaluation_after_complete_native_FSQ_return_and_returned_internal_verification",
        "killRequiredForScoring": False,
        "killObservation": "real_dispatch_outcomes_and_observed_order_only; unobserved_main_final_order_is_unknown",
        "internalVerification": "private_FSQ_artifact_separate_from_official_reward",
        "officialReward": "official_AndroidWorld_evaluator_only_after_full_FSQ_returns",
    },
    "retryPolicy": "one_attempt_per_task; no_automatic_retries_or_resume",
    "privacy": "goals_params_task_data_and_expected_values_are_evaluator_private; worker_receives_only_initialized_public_goal",
    "filesystemIsolation": "default_deny_host_file_data; explicit_runtime_and_worker_allowlist; canonical_oracle_and_result_roots_denied",
    "workerCleanup": "trusted_process_receipt_before_parse_or_archive; group_settled_required; forced_or_unknown_halts",
}


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _digest(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe(value: Any) -> Any:
    # Same canonical value semantics as runner._json_safe, without importing the
    # legacy AMKernel runner (and its installed AndroidWorld) into this process.
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _safe(dataclasses.asdict(value))
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("task parameter keys must be strings")
        return {key: _safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(child) for child in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("nonfinite task parameter")
        return value
    from PIL import Image
    if isinstance(value, Image.Image):
        return {"$type": "PIL.Image", "mode": value.mode, "size": list(value.size),
                "pixelsSha256": hashlib.sha256(value.tobytes()).hexdigest()}
    raise TypeError(f"unsupported manifest value: {type(value).__name__}")


def params_digest(value: Any) -> str:
    """Canonical task.params digest, identical for JSON and seed transports."""
    return _digest(_safe(value))


def manifest_file_sha256(path: Path) -> str:
    return _file_hash(path)


def task_from_spec(spec: dict[str, Any]) -> Any:
    """Reconstruct without initialization; caller imports ONLY the pinned site.

    Insert manifest.paths.evaluatorSite before any android_world import. Seed
    transport regenerates through the official suite API, never a lossy decoded
    image/dataclass parameter document. The frozen digest is checked either way.
    """
    from android_world import registry, suite_utils
    task_registry = registry.TaskRegistry()
    all_tasks = task_registry.get_registry(task_registry.ANDROID_WORLD_FAMILY)
    name = spec["name"]
    if name not in all_tasks:
        raise ValueError("frozen task is absent from isolated registry")
    if spec["paramsTransport"] == "json":
        task = all_tasks[name](json.loads(_json_bytes(spec["params"])))
    elif spec["paramsTransport"] == "seed":
        suite = suite_utils.create_suite({name: all_tasks[name]}, n_task_combinations=1,
                                         seed=30, tasks=[name], use_identical_params=True, env=None)
        if set(suite) != {name} or len(suite[name]) != 1:
            raise ValueError("seed reconstruction did not yield one frozen task")
        task = suite[name][0]
    else:
        raise ValueError("unsupported frozen parameter transport")
    if params_digest(task.params) != spec["paramsSha256"] or params_digest(spec["params"]) != spec["paramsSha256"]:
        raise ValueError("reconstructed task parameters differ from frozen identity")
    if task.params.get("seed") != spec["instanceSeed"]:
        raise ValueError("reconstructed task seed differs from frozen identity")
    return task


def _json_native(value: Any) -> bool:
    if value is None or isinstance(value, (bool, int, float, str)):
        return not isinstance(value, float) or math.isfinite(value)
    if isinstance(value, list):
        return all(_json_native(child) for child in value)
    return isinstance(value, dict) and all(isinstance(key, str) and _json_native(child) for key, child in value.items())


def _tree_identity(root: Path) -> dict[str, Any]:
    root = root.absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"identity root must be a nonsymlink directory: {root}")
    files = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ValueError(f"symlink in frozen tree: {path}")
        if path.is_file():
            files.append({"path": relative.as_posix(), "sha256": _file_hash(path), "sizeBytes": path.stat().st_size})
    if not files:
        raise ValueError(f"empty identity tree: {root}")
    return {"path": str(root), "sha256": _digest(files), "files": files}


def _same_tree(source: dict[str, Any], installed: dict[str, Any]) -> None:
    if source["files"] != installed["files"]:
        raise ValueError("complete source/installed package mapping mismatch")


def _revision(root: Path) -> str | None:
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def _worktree_state(root: Path) -> dict[str, Any]:
    # --no-optional-locks prevents git status from refreshing/writing an index.
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=normal"],
        capture_output=True, check=False, timeout=20,
    )
    if result.returncode != 0:
        return {"status": "unavailable", "dirty": None, "statusSha256": None}
    return {"status": "observed", "dirty": bool(result.stdout),
            "statusSha256": hashlib.sha256(result.stdout).hexdigest()}


def _distribution(name: str, site: Path | None = None) -> dict[str, Any]:
    if site is None:
        dist = importlib.metadata.distribution(name)
    else:
        normalized = name.replace("_", "-").lower()
        matches = [dist for dist in importlib.metadata.distributions(path=[str(site)])
                   if dist.metadata.get("Name", "").replace("_", "-").lower() == normalized]
        if len(matches) != 1:
            raise ValueError(f"expected exactly one {name} distribution in isolated site")
        dist = matches[0]
    metadata_files = []
    for item in dist.files or []:
        if item.name == "METADATA" and item.parent.name.endswith((".dist-info", ".egg-info")):
            metadata_files.append(Path(dist.locate_file(item)).parent)
    if len(metadata_files) != 1:
        raise ValueError(f"missing real distribution metadata for {name}")
    return {"name": dist.metadata["Name"], "version": dist.version, "metadata": _tree_identity(metadata_files[0])}


def _suite_snapshot(site: Path, frozen_tasks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    # Called ONLY in a new interpreter. No environment creation, initialize_task,
    # evaluator invocation, device discovery, model construction, or auth loader.
    sys.path.insert(0, str(site))
    from android_world import registry, suite_utils
    package = Path(registry.__file__).resolve().parent
    if package != (site / "android_world").resolve():
        raise ValueError("AndroidWorld did not import from isolated evaluator site")
    task_registry = registry.TaskRegistry()
    all_tasks = task_registry.get_registry(task_registry.ANDROID_WORLD_FAMILY)
    names = sorted(all_tasks)
    if len(names) != SUITE_SIZE:
        raise ValueError(f"expected exact {SUITE_SIZE}-task suite, got {len(names)}")
    families = {name: "android" for name in task_registry.get_registry(task_registry.ANDROID_FAMILY)}
    families.update({name: "information_retrieval" for name in task_registry.get_registry(task_registry.INFORMATION_RETRIEVAL_FAMILY)})
    metadata_path = package / "task_metadata.json"
    metadata = {row["task_name"]: row for row in json.loads(metadata_path.read_text())}
    if frozen_tasks is None:
        suite = suite_utils.create_suite(all_tasks, n_task_combinations=1, seed=30,
                                         tasks=names, use_identical_params=True, env=None)
    else:
        if not isinstance(frozen_tasks, list) or [spec["name"] for spec in frozen_tasks] != names:
            raise ValueError("frozen task order differs from complete official registry")
        # Official generators can use wall time. Freeze their first result;
        # never regenerate JSON-transported parameters during admission.
        suite = {spec["name"]: [task_from_spec(spec)] for spec in frozen_tasks}
    if sorted(suite) != names:
        raise ValueError("suite registry mismatch")
    rows = []
    for index, name in enumerate(names):
        if len(suite[name]) != 1:
            raise ValueError("suite must have exactly one instance per task")
        instance = suite[name][0]
        params = instance.params
        safe = _safe(params)
        complexity = instance.complexity
        if isinstance(complexity, bool) or not isinstance(complexity, (int, float)) or not math.isfinite(complexity):
            raise ValueError("invalid task complexity")
        maximum = int(10 * complexity)
        if maximum <= 0 or suite_utils._allocate_step_budget(complexity) != maximum:
            raise ValueError("official task allocator disagrees with int(10 * complexity)")
        seed = int(hashlib.sha256(f"30_{name}_0".encode()).hexdigest(), 16) % (2**32)
        if params.get("seed") != seed:
            raise ValueError("official task instance seed mismatch")
        transport = "seed"
        if _json_native(params):
            try:
                reconstructed = all_tasks[name](json.loads(_json_bytes(safe)))
            except Exception:
                # The authoritative generated instance is still represented by
                # the exact deterministic seed transport, not a fake substitute.
                pass
            else:
                if params_digest(reconstructed.params) == _digest(safe):
                    transport = "json"
        row = metadata.get(name)
        if row is None:
            raise ValueError(f"task metadata missing: {name}")
        rows.append({"index": index, "name": name, "family": families.get(name, "unknown"),
                     "apps": list(instance.app_names), "complexity": complexity,
                     "maxSteps": maximum, "maxActions": maximum, "timeBudget": episode_time_budget(maximum),
                     "difficulty": row.get("difficulty", "unknown"), "tags": row.get("tags", []),
                     "instanceSeed": seed, "params": safe, "paramsSha256": _digest(safe), "paramsTransport": transport})
    return {"package": _tree_identity(package), "distribution": _distribution("android-world", site),
            "taskMetadataSha256": _file_hash(metadata_path), "tasks": rows}


def _fsq_snapshot() -> dict[str, Any]:
    spec = importlib.util.find_spec("fsq_agent")
    if spec is None or spec.origin is None:
        raise ValueError("FSQ is unavailable in the requested interpreter")
    package = Path(spec.origin).resolve().parent
    # Package version and distribution version are intentionally not conflated.
    result = {"package": _tree_identity(package), "distribution": _distribution("fsq-agent"),
              "pythonVersion": sys.version, "executable": sys.executable, "prefix": sys.prefix,
              "dependencies": {name: importlib.metadata.version(name) for name in ("uiautomator2", "openai")}}
    result["basePrefix"] = sys.base_prefix
    venv_config = Path(sys.prefix) / "pyvenv.cfg"
    result["venvConfigSha256"] = _file_hash(venv_config) if venv_config.is_file() else None
    return result


def _probe(python: Path, mode: str, site: Path | None = None, *,
           frozen_tasks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    # -I drops cwd/PYTHONPATH, -B prevents source-tree bytecode writes. Only our
    # explicit evaluator source and (suite mode) isolated package site are added.
    source = str(Path(__file__).resolve().parents[1])
    call = "m._suite_snapshot(Path(sys.argv[1]), json.load(sys.stdin))" if mode == "suite" else "m._fsq_snapshot()"
    script = ("import sys,json,contextlib,io; from pathlib import Path; "
              f"sys.path.insert(0,{source!r}); import fsq_androidworld_eval.fsq_manifest as m; "
              "out=io.StringIO(); "
              f"\nwith contextlib.redirect_stdout(out): result={call}\n"
              "print(json.dumps(result,sort_keys=True,allow_nan=False))")
    result = subprocess.run([str(python), "-I", "-B", "-c", script, *([str(site)] if site else [])],
                            input=_json_bytes(frozen_tasks).decode() if mode == "suite" else None,
                            capture_output=True, text=True, check=False, timeout=300)
    if result.returncode != 0:
        # Do not echo arbitrary subprocess/config text into public output.
        raise ValueError(f"offline {mode} identity probe failed (exit {result.returncode}); check isolated dependencies and package data")
    return json.loads(result.stdout)


def _settings_identity(path: Path) -> dict[str, Any]:
    import yaml
    value = yaml.safe_load(path.read_text())
    if not isinstance(value, dict) or set(value) - {"version", "name", "root_path", "platform", "target", "env"} or type(value.get("version")) is not int or value.get("version") != 2 or value.get("platform") != "android":
        raise ValueError("settingsPath must be native version-2 Android workspace configuration")
    workspace = path.parent.parent.parent
    if path != workspace / ".fsq" / "config" / "config.android.yaml":
        raise ValueError("settingsPath must be canonical workspace/.fsq/config/config.android.yaml")
    if not isinstance(value.get("root_path"), str) or Path(value["root_path"]).expanduser().resolve() != workspace:
        raise ValueError("native workspace root_path mismatch")
    if not isinstance(value.get("name"), str) or not value["name"].strip():
        raise ValueError("native workspace name missing")
    target = value.get("target")
    if not isinstance(target, dict) or set(target) - {"app_id"}:
        raise ValueError("native Android target must contain only app_id")
    app_id = target.get("app_id")
    if app_id is not None and (not isinstance(app_id, str) or not app_id.strip()):
        raise ValueError("invalid native app_id")
    env = value.get("env", {})
    if not isinstance(env, dict) or any(not isinstance(key, str) for key in env):
        raise ValueError("invalid native env mapping")
    public = {key: value[key] for key in ("version", "name", "root_path", "platform", "target")}
    public["envKeys"] = sorted(env)  # No secret values or hashes of credentials.
    return {"path": str(path), "public": public, "publicSha256": _digest(public),
            "serialBinding": "explicit_manifest_serial_injected_into_settings.harness.android.serial_per_episode"}


def _provider_identity() -> dict[str, Any]:
    import yaml
    path = Path.home() / ".fsq" / "config.yaml"
    if not path.exists():
        return {"path": str(path), "status": "unconfigured", "provider": None, "model": None}
    value = yaml.safe_load(path.read_text())
    if not isinstance(value, dict) or value.get("version") not in (2, 3):
        raise ValueError("invalid native user-provider metadata")
    provider = value.get("provider")
    if provider is None:
        return {"path": str(path), "status": "unconfigured", "provider": None, "model": None}
    if not isinstance(provider, dict) or not isinstance(provider.get("type"), str) or not isinstance(provider.get("model"), str):
        raise ValueError("invalid native provider/model metadata")
    return {"path": str(path), "status": "metadata_observed_not_authenticated",
            "provider": provider["type"], "model": provider["model"]}


def _oracle_source_roots(project: Path, distribution: dict[str, Any], extra: list[Path] | None) -> list[str]:
    """Retain local build provenance as an oracle root, not just its installed copy."""
    roots = {(project / "android_world").resolve(strict=True)}
    metadata = distribution["metadata"]
    if any(entry["path"] == "direct_url.json" for entry in metadata["files"]):
        direct = json.loads((Path(metadata["path"]) / "direct_url.json").read_text())
        source_url = urlparse(direct.get("url", ""))
        if source_url.scheme == "file":
            if source_url.netloc not in {"", "localhost"}:
                raise ValueError("nonlocal AndroidWorld source origin")
            roots.add(Path(unquote(source_url.path)).resolve(strict=True))
    for root in extra or []:
        roots.add(root.expanduser().resolve(strict=True))
    return sorted(str(root) for root in roots)


def _identities(project: Path, evaluator_site: Path, fsq_source: Path, fsq_python: Path,
                settings_path: Path, adb_path: Path, *,
                frozen_tasks: list[dict[str, Any]] | None = None,
                oracle_source_roots: list[Path] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if evaluator_site == project / ".venv" or project / ".venv" in evaluator_site.parents:
        raise ValueError("shared project .venv is not an isolated evaluator target")
    if evaluator_site.is_symlink():
        raise ValueError("isolated evaluator site must not be a symlink")
    android_source = _tree_identity(project / "android_world" / "android_world")
    suite = _probe(Path(sys.executable), "suite", evaluator_site, frozen_tasks=frozen_tasks)
    _same_tree(android_source, suite["package"])
    native = _probe(fsq_python, "fsq")
    native_source = _tree_identity(fsq_source / "fsq_agent")
    _same_tree(native_source, native["package"])
    pyproject = fsq_source / "pyproject.toml"
    native["source"] = native_source
    native["sourceRevisionObserved"] = _revision(fsq_source)
    native["sourceWorktree"] = _worktree_state(fsq_source)
    native["sourcePyprojectSha256"] = _file_hash(pyproject)
    native["sourceCodeVersion"] = tomllib.loads(pyproject.read_text())["project"]["version"]
    native["interpreterPath"] = str(fsq_python)
    native["interpreterSha256"] = _file_hash(fsq_python)
    identities = {
        "evaluator": {"project": str(project), "source": _tree_identity(project / "src" / "fsq_androidworld_eval"),
                      "pyprojectSha256": _file_hash(project / "pyproject.toml"),
                      "sourceRevisionObserved": _revision(project), "sourceWorktree": _worktree_state(project),
                      "pythonPath": sys.executable, "pythonVersion": sys.version, "pythonSha256": _file_hash(Path(sys.executable))},
        "configurationParser": {"distribution": _distribution("PyYAML"),
                                "package": _tree_identity(Path(importlib.util.find_spec("yaml").origin).parent)},
        "androidWorld": {"source": android_source, "sourceRevisionObserved": _revision(project / "android_world"),
                         "sourceWorktree": _worktree_state(project / "android_world"),
                         "sourceSetupSha256": _file_hash(project / "android_world" / "setup.py"),
                         "site": str(evaluator_site), "installed": suite["package"], "distribution": suite["distribution"],
                         "taskMetadataSha256": suite["taskMetadataSha256"],
                         "oracleSourceRoots": _oracle_source_roots(project, suite["distribution"], oracle_source_roots),
                         "installationMode": "isolated_wheel_install_plus_complete_corrected_source_and_data_copy"},
        "fsq": native,
        "nativeSettings": _settings_identity(settings_path),
        "nativeProviderMetadata": _provider_identity(),
        "adb": {"path": str(adb_path), "sha256": _file_hash(adb_path), "executed": False},
    }
    return identities, suite["tasks"]


def _validate_target(serial: str, console_port: int, grpc_port: int) -> None:
    if not isinstance(serial, str) or not serial.strip() or serial != serial.strip():
        raise ValueError("exact nonempty serial is required")
    if any(type(port) is not int or not 1 <= port <= 65535 for port in (console_port, grpc_port)) or console_port == grpc_port:
        raise ValueError("distinct valid console and gRPC ports are required")


def create_manifest(project: Path, evaluator_site: Path, fsq_source: Path, fsq_python: Path,
                    settings_path: Path, output_path: Path, *, campaign_id: str, serial: str,
                    console_port: int, grpc_port: int, adb_path: Path,
                    oracle_source_roots: list[Path] | None = None) -> dict[str, Any]:
    """Prepare private seed-30 suite and pending candidate only, never qualify it.

    Both output and adjacent ``<name>.sha256`` must be new. The latter is a local
    byte-integrity anchor, not a signature or authorization to execute a campaign.
    """
    project, evaluator_site, fsq_source, settings_path, output_path, adb_path = (
        path.expanduser().absolute() for path in (project, evaluator_site, fsq_source, settings_path, output_path, adb_path))
    # Resolving a venv's python symlink would silently switch interpreter prefix.
    fsq_python = fsq_python.expanduser().absolute()
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise ValueError("campaign_id is required")
    _validate_target(serial, console_port, grpc_port)
    seal = output_path.with_name(output_path.name + ".sha256")
    if output_path.exists() or seal.exists():
        raise FileExistsError("candidate output already exists; old runs are never overwritten")
    identities, tasks = _identities(project, evaluator_site, fsq_source, fsq_python, settings_path, adb_path,
                                   oracle_source_roots=oracle_source_roots)
    manifest = {"schemaVersion": 1, "campaignId": campaign_id, "kind": "fsq_androidworld",
                "status": "candidate_pending_independent_review", "protocol": json.loads(_json_bytes(PROTOCOL)),
                "identities": identities,
                "paths": {"project": str(project), "evaluatorSite": str(evaluator_site), "fsqSource": str(fsq_source),
                          "fsqPython": str(fsq_python), "settingsPath": str(settings_path)},
                "target": {"serial": serial, "consolePort": console_port, "grpcPort": grpc_port, "adbPath": str(adb_path),
                           "provider": PROVIDER, "model": MODEL, "resourceStatus": "pending",
                           "authenticationStatus": "pending", "readinessStatus": "pending"},
                "tasks": tasks, "gates": {name: "pending" for name in GATE_NAMES}}
    identities["targetConfiguration"] = dict(manifest["target"])
    data = _json_bytes(manifest) + b"\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        with contextlib.ExitStack() as stack:
            output = stack.enter_context(output_path.open("xb"))
            created.append(output_path)
            anchor = stack.enter_context(seal.open("xb"))
            created.append(seal)
            output.write(data)
            anchor.write((hashlib.sha256(data).hexdigest() + "\n").encode())
    except BaseException:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return manifest


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError(f"duplicate manifest key: {key}")
        value[key] = child
    return value


def load_manifest(path: Path, project: Path) -> dict[str, Any]:
    """Fail closed on byte, source, interpreter, native metadata or suite drift.

    This permits *inspection* of a pending candidate, not execution. A runner must
    independently require live gates and the observed native provider/model to
    match the requested target. Credential files are not read and credential
    values from workspace env are excluded from the frozen public identity.
    """
    path, project = path.expanduser().absolute(), project.expanduser().absolute()
    if path.is_symlink():
        raise ValueError("manifest must not be a symlink")
    data = path.read_bytes()
    seal = path.with_name(path.name + ".sha256")
    if seal.is_symlink() or seal.read_text().strip() != hashlib.sha256(data).hexdigest():
        raise ValueError("manifest frozen byte identity mismatch")
    manifest = json.loads(data, object_pairs_hook=_unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite manifest value")))
    if not isinstance(manifest, dict) or set(manifest) != {"schemaVersion", "campaignId", "kind", "status", "protocol", "identities", "paths", "target", "tasks", "gates"}:
        raise ValueError("invalid FSQ manifest shape")
    if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1 or manifest["kind"] != "fsq_androidworld" or manifest["status"] != "candidate_pending_independent_review":
        raise ValueError("not an FSQ pending candidate manifest")
    if _json_bytes(manifest["protocol"]) != _json_bytes(PROTOCOL) or manifest["gates"] != {name: "pending" for name in GATE_NAMES}:
        raise ValueError("FSQ candidate protocol or pending gates changed")
    if not isinstance(manifest["campaignId"], str) or not manifest["campaignId"].strip():
        raise ValueError("invalid campaign identity")
    target = manifest["target"]
    if not isinstance(target, dict) or set(target) != {"serial", "consolePort", "grpcPort", "adbPath", "provider", "model", "resourceStatus", "authenticationStatus", "readinessStatus"}:
        raise ValueError("invalid FSQ target")
    _validate_target(target["serial"], target["consolePort"], target["grpcPort"])
    if target["provider"] != PROVIDER or target["model"] != MODEL or any(target[key] != "pending" for key in ("resourceStatus", "authenticationStatus", "readinessStatus")):
        raise ValueError("FSQ requested target identity or pending state changed")
    identities = manifest["identities"]
    try:
        if identities["evaluator"]["project"] != str(project):
            raise ValueError("manifest belongs to another evaluator project")
        current, tasks = _identities(project, Path(identities["androidWorld"]["site"]),
                                     Path(identities["fsq"]["source"]["path"]).parent,
                                     Path(identities["fsq"]["interpreterPath"]),
                                     Path(identities["nativeSettings"]["path"]), Path(identities["adb"]["path"]),
                                     frozen_tasks=manifest["tasks"],
                                     oracle_source_roots=[Path(root) for root in identities["androidWorld"]["oracleSourceRoots"]])
        expected_paths = {"project": str(project), "evaluatorSite": identities["androidWorld"]["site"],
                          "fsqSource": str(Path(identities["fsq"]["source"]["path"]).parent),
                          "fsqPython": identities["fsq"]["interpreterPath"], "settingsPath": identities["nativeSettings"]["path"]}
        if manifest["paths"] != expected_paths or target["adbPath"] != identities["adb"]["path"]:
            raise ValueError("FSQ manifest path bindings changed")
    except (KeyError, TypeError) as error:
        raise ValueError("invalid FSQ frozen identity shape") from error
    current["targetConfiguration"] = dict(target)
    if _json_bytes(current) != _json_bytes(identities):
        raise ValueError("frozen FSQ source, runtime, native configuration, or package identity drift")
    if _json_bytes(tasks) != _json_bytes(manifest["tasks"]):
        raise ValueError("frozen task parameters or budgets differ from corrected seed-30 suite")
    return manifest


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Offline FSQ candidate prepare/inspect; never runs devices or models")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    for name in ("project", "evaluator-site", "fsq-source", "fsq-python", "settings-path", "output", "adb-path", "campaign-id", "serial"):
        prepare.add_argument(f"--{name}", required=True)
    prepare.add_argument("--console-port", required=True, type=int)
    prepare.add_argument("--grpc-port", required=True, type=int)
    prepare.add_argument("--oracle-source-root", action="append", type=Path, default=[])
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--manifest", required=True)
    inspect.add_argument("--project", required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        manifest = create_manifest(Path(args.project), Path(args.evaluator_site), Path(args.fsq_source), Path(args.fsq_python),
                                   Path(args.settings_path), Path(args.output), campaign_id=args.campaign_id,
                                   serial=args.serial, console_port=args.console_port, grpc_port=args.grpc_port, adb_path=Path(args.adb_path),
                                   oracle_source_roots=args.oracle_source_root)
    else:
        manifest = load_manifest(Path(args.manifest), Path(args.project))
    # No evaluator-private parameters or goals in routine CLI output.
    print(json.dumps({"campaignId": manifest["campaignId"], "kind": manifest["kind"], "status": manifest["status"],
                      "taskCount": len(manifest["tasks"]), "target": manifest["target"],
                      "observedNativeProvider": manifest["identities"]["nativeProviderMetadata"], "gates": manifest["gates"]}, sort_keys=True))


if __name__ == "__main__":
    main()
