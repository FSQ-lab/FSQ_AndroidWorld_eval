"""CPU-only behavioral freezes using real synthetic installed Python packages."""

import dataclasses
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import venv

import pytest

from fsq_androidworld_eval import fsq_manifest as fm
from fsq_androidworld_eval.lifecycle import episode_time_budget


def _put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _dist(site: Path, name: str, version: str) -> None:
    root = site / f"{name}-{version}.dist-info"
    _put(root / "METADATA", f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n")
    _put(root / "WHEEL", "Wheel-Version: 1.0\nGenerator: offline-fixture\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
    _put(root / "RECORD", f"{root.name}/METADATA,,\n{root.name}/WHEEL,,\n{root.name}/RECORD,,\n")


@pytest.fixture
def candidate(tmp_path, monkeypatch):
    project = tmp_path / "project"
    site = tmp_path / "owned-target" / "site"
    source = project / "android_world" / "android_world"
    _put(project / "pyproject.toml", '[project]\nname="evaluator-fixture"\nversion="1"\n')
    _put(project / "src" / "fsq_androidworld_eval" / "owned.py", "VALUE = 1\n")
    _put(project / "android_world" / "setup.py", "# synthetic corrected source build input\n")
    _put(source / "__init__.py", "")
    _put(source / "registry.py", '''
class Task:
    def __init__(self, params):
        self.params = params
        self.complexity = 1 + params["index"] % 3
        self.app_names = ("fixture_app",)
    def initialize_task(self, env):
        raise AssertionError("offline freeze initialized task")
    def is_successful(self, env):
        raise AssertionError("offline freeze invoked evaluator")
class TaskRegistry:
    ANDROID_WORLD_FAMILY = "all"
    ANDROID_FAMILY = "android"
    INFORMATION_RETRIEVAL_FAMILY = "ir"
    def get_registry(self, family):
        names = {f"Task{i:03}": Task for i in range(116)}
        return names if family in ("all", "android") else {}
''')
    _put(source / "suite_utils.py", '''
import hashlib
import random
from .registry import Task
def create_suite(registry, *, n_task_combinations, seed, tasks, use_identical_params, env):
    assert (n_task_combinations, seed, use_identical_params, env) == (1, 30, True, None)
    result = {}
    for name in sorted(tasks):
        i = int(name[4:])
        instance_seed = int(hashlib.sha256(f"{seed}_{name}_0".encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(instance_seed)
        result[name] = [Task({"seed": instance_seed, "index": i, "hour": 15, "value": rng.randint(1, 10**9)})]
    return result
def _allocate_step_budget(complexity):
    return int(10 * complexity)
''')
    _put(source / "task_metadata.json", json.dumps([
        {"task_name": f"Task{i:03}", "difficulty": "easy", "tags": ["offline"]}
        for i in range(116)
    ]))
    # Full task data are part of mapping equality, not just imported .py files.
    _put(source / "task_evals" / "data" / "clock.json", '{"allowedHours":[0,23],"hour":15}\n')
    _put(source / "nonruntime-source.kt", "// complete package supplement\n")
    shutil.copytree(source, site / "android_world")
    _dist(site, "android_world", "0.0.0")
    fsq_source = tmp_path / "native-source"
    _put(fsq_source / "fsq_agent" / "__init__.py", "# metadata lookup never constructs runtime\n")
    _put(fsq_source / "fsq_agent" / "skill.md", "Keep original native kill semantics.\n")
    _put(fsq_source / "pyproject.toml", '[project]\nname="fsq-agent"\nversion="0.1.2"\n')
    native_env = tmp_path / "native-venv"
    venv.EnvBuilder(with_pip=False, symlinks=True).create(native_env)
    native_site = native_env / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    shutil.copytree(fsq_source / "fsq_agent", native_site / "fsq_agent")
    _dist(native_site, "fsq_agent", "0.1.0a1")
    _dist(native_site, "uiautomator2", "3.5.2")
    _dist(native_site, "openai", "2.34.0")
    workspace = tmp_path / "owned-workspace"
    settings = workspace / ".fsq" / "config" / "config.android.yaml"
    _put(settings, f'version: 2\nname: fixture\nroot_path: {workspace}\nplatform: android\ntarget:\n  app_id: fixture.app\nenv:\n  PRIVATE_VALUE: never-serialize-this-secret\n')
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    _put(home / ".fsq" / "config.yaml", 'version: 3\nprovider:\n  type: deepseek\n  model: deepseek-chat\nworkspaces: []\n')
    adb = tmp_path / "adb"
    _put(adb, "a frozen binary identity, never executed\n")
    args = {"project": project, "evaluator_site": site, "fsq_source": fsq_source,
            "fsq_python": native_env / "bin" / "python", "settings_path": settings,
            "output_path": tmp_path / "campaign" / "manifest.json", "campaign_id": "offline-candidate",
            "serial": "emulator-5564", "console_port": 5564, "grpc_port": 8564, "adb_path": adb}
    return args


def _prepare(args):
    return fm.create_manifest(**args)


def _reseal(path, value):
    data = fm._json_bytes(value) + b"\n"
    path.write_bytes(data)
    path.with_name(path.name + ".sha256").write_text(hashlib.sha256(data).hexdigest() + "\n")


def test_prepare_load_real_isolated_suite_and_pending_target(candidate):
    manifest = _prepare(candidate)
    assert fm.load_manifest(candidate["output_path"], candidate["project"]) == manifest
    assert manifest["kind"] == "fsq_androidworld"
    assert manifest["status"] == "candidate_pending_independent_review"
    assert set(manifest["gates"].values()) == {"pending"}
    assert manifest["target"]["provider"] == "github_copilot"
    assert manifest["target"]["model"] == "gpt-6.1-sol"
    assert manifest["identities"]["nativeProviderMetadata"]["provider"] == "deepseek"
    assert manifest["identities"]["fsq"]["sourceCodeVersion"] == "0.1.2"
    assert manifest["identities"]["fsq"]["distribution"]["version"] == "0.1.0a1"
    assert manifest["identities"]["adb"]["executed"] is False
    assert len(manifest["tasks"]) == 116
    assert len({task["name"] for task in manifest["tasks"]}) == 116
    for task in manifest["tasks"]:
        assert task["maxSteps"] == task["maxActions"] == int(10 * task["complexity"])
        assert task["timeBudget"] == episode_time_budget(task["maxActions"])
        assert task["params"]["hour"] == 15
        assert task["paramsSha256"] == fm._digest(task["params"])
        expected = int(hashlib.sha256(f'30_{task["name"]}_0'.encode()).hexdigest(), 16) % (2**32)
        assert task["instanceSeed"] == expected
    assert "never-serialize-this-secret" not in candidate["output_path"].read_text()
    assert not list((candidate["evaluator_site"] / "android_world").rglob("*.pyc"))


def test_two_new_preparations_have_identical_suite_and_pins(candidate):
    first = _prepare(candidate)
    candidate["output_path"] = candidate["output_path"].with_name("another.json")
    second = _prepare(candidate)
    assert first == second


def test_old_manifest_and_seal_are_never_overwritten(candidate):
    _prepare(candidate)
    before = candidate["output_path"].read_bytes()
    with pytest.raises(FileExistsError):
        _prepare(candidate)
    assert candidate["output_path"].read_bytes() == before


@pytest.mark.parametrize("mutation", ["model", "provider", "serial", "params", "budget", "gates", "profile"])
def test_manifest_mutations_fail_closed(candidate, mutation):
    value = _prepare(candidate)
    if mutation == "params":
        value["tasks"][0]["params"]["hour"] = 3
    elif mutation == "budget":
        value["tasks"][0]["maxActions"] = 100000
    elif mutation == "gates":
        value["gates"]["deviceReadiness"] = "completed"
    elif mutation == "profile":
        value["protocol"]["lifecycle"]["oracleBeforeKill"] = True
    else:
        value["target"][mutation] = "tampered"
    _reseal(candidate["output_path"], value)
    with pytest.raises(ValueError):
        fm.load_manifest(candidate["output_path"], candidate["project"])


def test_original_byte_anchor_rejects_reformatted_manifest(candidate):
    value = _prepare(candidate)
    candidate["output_path"].write_text(json.dumps(value, indent=2))
    with pytest.raises(ValueError, match="byte identity"):
        fm.load_manifest(candidate["output_path"], candidate["project"])


@pytest.mark.parametrize("part", ["installed-data", "source-data", "native-source", "evaluator-source", "adb", "settings"])
def test_source_and_runtime_drift_fail_closed(candidate, part):
    _prepare(candidate)
    paths = {
        "installed-data": candidate["evaluator_site"] / "android_world" / "task_evals" / "data" / "clock.json",
        "source-data": candidate["project"] / "android_world" / "android_world" / "task_evals" / "data" / "clock.json",
        "native-source": candidate["fsq_source"] / "fsq_agent" / "skill.md",
        "evaluator-source": candidate["project"] / "src" / "fsq_androidworld_eval" / "owned.py",
        "adb": candidate["adb_path"], "settings": candidate["settings_path"],
    }
    path = paths[part]
    if part == "settings":
        path.write_text(path.read_text().replace("fixture.app", "changed.app"))
    else:
        path.write_text(path.read_text() + "\nchanged\n")
    with pytest.raises(ValueError):
        fm.load_manifest(candidate["output_path"], candidate["project"])


def test_corrected_source_and_installed_change_require_new_candidate(candidate):
    old = _prepare(candidate)
    for root in (candidate["project"] / "android_world" / "android_world", candidate["evaluator_site"] / "android_world"):
        data = root / "task_evals" / "data" / "clock.json"
        data.write_text('{"hour":16}\n')
    with pytest.raises(ValueError, match="identity drift"):
        fm.load_manifest(candidate["output_path"], candidate["project"])
    candidate["output_path"] = candidate["output_path"].with_name("corrected.json")
    new = _prepare(candidate)
    assert new["identities"]["androidWorld"]["source"]["sha256"] != old["identities"]["androidWorld"]["source"]["sha256"]


def test_native_provider_change_requires_fresh_candidate_but_secret_refresh_does_not(candidate):
    _prepare(candidate)
    provider = Path.home() / ".fsq" / "config.yaml"
    _put(Path.home() / ".fsq" / "auth" / "github-copilot-token.json", '{"token":"private-refreshed"}')
    settings = candidate["settings_path"]
    settings.write_text(settings.read_text().replace("never-serialize-this-secret", "refreshed-private-value"))
    fm.load_manifest(candidate["output_path"], candidate["project"])
    provider.write_text(provider.read_text().replace("deepseek", "github_copilot").replace("github_copilot-chat", "gpt-6.1-sol"))
    with pytest.raises(ValueError, match="identity drift"):
        fm.load_manifest(candidate["output_path"], candidate["project"])


def test_missing_native_provider_is_pending_and_not_created(candidate):
    provider = Path.home() / ".fsq" / "config.yaml"
    provider.unlink()
    value = _prepare(candidate)
    assert value["identities"]["nativeProviderMetadata"]["status"] == "unconfigured"
    assert not provider.exists()
    assert value["target"]["authenticationStatus"] == "pending"


def test_complete_mapping_rejects_extra_missing_and_symlink_files(candidate):
    installed = candidate["evaluator_site"] / "android_world"
    (installed / "nonruntime-source.kt").unlink()
    with pytest.raises(ValueError, match="mapping mismatch"):
        _prepare(candidate)
    shutil.copyfile(candidate["project"] / "android_world" / "android_world" / "nonruntime-source.kt", installed / "nonruntime-source.kt")
    _put(installed / "unexpected.json", "{}")
    with pytest.raises(ValueError, match="mapping mismatch"):
        _prepare(candidate)
    (installed / "unexpected.json").unlink()
    (installed / "link.json").symlink_to(installed / "task_metadata.json")
    with pytest.raises(ValueError, match="identity probe failed"):
        _prepare(candidate)


def test_exact_116_required(candidate):
    for root in (candidate["project"] / "android_world" / "android_world", candidate["evaluator_site"] / "android_world"):
        registry = root / "registry.py"
        registry.write_text(registry.read_text().replace("range(116)", "range(115)"))
    with pytest.raises(ValueError, match="suite identity probe failed"):
        _prepare(candidate)


def test_shared_environment_target_is_refused(candidate):
    candidate["evaluator_site"] = candidate["project"] / ".venv" / "lib" / "python3.11" / "site-packages"
    with pytest.raises(ValueError, match="shared project .venv"):
        _prepare(candidate)


def test_serializer_preserves_structured_identity_and_seed_transport_values():
    @dataclasses.dataclass
    class Params:
        names: tuple[str, ...]
        hour: int
    value = Params(("one", "two"), 15)
    assert fm._safe(value) == {"names": ["one", "two"], "hour": 15}
    assert not fm._json_native(value)
    assert not fm._json_native(("one", "two"))
    with pytest.raises(ValueError, match="nonfinite"):
        fm._safe(float("nan"))
    with pytest.raises(TypeError, match="keys"):
        fm._safe({1: "collision"})


def test_inspect_cli_does_not_print_private_params(candidate, capsys):
    _prepare(candidate)
    fm.main(["inspect", "--manifest", str(candidate["output_path"]), "--project", str(candidate["project"])])
    value = json.loads(capsys.readouterr().out)
    assert value["taskCount"] == 116
    assert value["status"] == "candidate_pending_independent_review"
    assert "tasks" not in value
    assert "params" not in value


@pytest.mark.parametrize("transport", ["json", "seed"])
def test_task_reconstruction_uses_exact_frozen_parameters(candidate, transport):
    value = _prepare(candidate)
    spec = dict(value["tasks"][57], paramsTransport=transport)
    source = str(Path(fm.__file__).resolve().parents[1])
    script = '''
import sys, json
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
from fsq_androidworld_eval.fsq_manifest import task_from_spec, params_digest
spec = json.load(sys.stdin)
task = task_from_spec(spec)
print(json.dumps({"params": task.params, "digest": params_digest(task.params)}))
'''
    command = [sys.executable, "-I", "-B", "-c", script, source, str(candidate["evaluator_site"])]
    result = subprocess.run(command, input=json.dumps(spec), capture_output=True, text=True, check=True)
    actual = json.loads(result.stdout)
    assert actual["params"] == spec["params"]
    assert actual["digest"] == spec["paramsSha256"]
    spec["paramsSha256"] = "0" * 64
    result = subprocess.run(command, input=json.dumps(spec), capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "reconstructed task parameters differ" in result.stderr


def test_public_digest_and_manifest_file_identity(candidate):
    value = _prepare(candidate)
    assert fm.params_digest(value["tasks"][0]["params"]) == value["tasks"][0]["paramsSha256"]
    assert fm.manifest_file_sha256(candidate["output_path"]) == hashlib.sha256(candidate["output_path"].read_bytes()).hexdigest()


def test_loading_frozen_json_tasks_never_calls_their_parameter_generator_again(candidate):
    marker = candidate["project"].parent / "generator-consumed"
    source = candidate["project"] / "android_world" / "android_world" / "suite_utils.py"
    installed = candidate["evaluator_site"] / "android_world" / "suite_utils.py"
    guarded = source.read_text() + f'''
from pathlib import Path
_original_create_suite = create_suite
def create_suite(*args, **kwargs):
    marker = Path({str(marker)!r})
    if marker.exists():
        raise RuntimeError("parameter generation is not repeatable")
    marker.write_text("generated once")
    return _original_create_suite(*args, **kwargs)
'''
    _put(source, guarded)
    _put(installed, guarded)
    frozen = _prepare(candidate)
    assert fm.load_manifest(candidate["output_path"], candidate["project"])["tasks"] == frozen["tasks"]


def test_dirty_provenance_observation_does_not_refresh_an_index(tmp_path, monkeypatch):
    import os
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    repo = tmp_path / "independent-repository"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    source = repo / "source.txt"
    source.write_text("source bytes")
    subprocess.run(["git", "-C", str(repo), "add", "source.txt"], check=True)
    index = repo / ".git" / "index"
    before = index.read_bytes()
    os.utime(source, (1_000_000_000, 1_000_000_000))
    observed = fm._worktree_state(repo)
    assert observed["status"] == "observed" and observed["dirty"] is True
    assert index.read_bytes() == before
    assert not (repo / ".git" / "index.lock").exists()
