from dataclasses import replace
import hashlib
from http.client import IncompleteRead
import io
from pathlib import Path
import shutil
from types import SimpleNamespace
import shlex
import sqlite3
import zipfile

import pytest
from android_env.proto import adb_pb2
from android_world.env import interface
from android_world.task_evals import task_eval

from fsq_androidworld_eval import environment


def _apk_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("AndroidManifest.xml", b"fixture-manifest")
        archive.writestr("classes.dex", b"dex\n035\0fixture-bytecode")
    return buffer.getvalue()


class _Response(io.BytesIO):
    def __init__(self, payload: bytes, content_length: int | None = None):
        super().__init__(payload)
        self.headers = {} if content_length is None else {"Content-Length": str(content_length)}


@pytest.fixture
def artifacts(tmp_path: Path, monkeypatch):
    payload = _apk_bytes()
    helper = environment._ArtifactSpec(
        "helper.apk", "https://official.invalid/helper.apk",
        hashlib.sha256(payload).hexdigest(), len(payload),
    )
    app = replace(helper, name="application.apk", url="https://official.invalid/application.apk")
    map_bytes = b"real-local-map-fixture"
    map_spec = environment._ArtifactSpec(
        "map.obf", "https://official.invalid/map.obf",
        hashlib.sha256(map_bytes).hexdigest(), len(map_bytes),
    )
    monkeypatch.setattr(environment, "_HELPER_APK", helper)
    monkeypatch.setattr(environment, "_APP_DATA", (app, map_spec))
    monkeypatch.setattr(environment, "_DOWNLOAD_ATTEMPTS", 2)
    monkeypatch.setattr(environment.tempfile, "gettempdir", lambda: str(tmp_path / "legacy"))
    values = {helper.name: payload, app.name: payload, map_spec.name: map_bytes}
    directory = tmp_path / environment._CACHE_DIRECTORY
    directory.mkdir(parents=True)
    for name, value in values.items():
        (directory / name).write_bytes(value)
    return SimpleNamespace(
        project=tmp_path, directory=directory, helper=helper, app=app,
        map=map_spec, payload=payload, values=values,
    )


def _load(project: Path, *, freeze_datetime: bool = False):
    return environment.load_environment(
        artifact_root=project, console_port=5554, adb_path="fixture-adb",
        grpc_port=8554, freeze_datetime=freeze_datetime,
    )


def _forbid_network(*args, **kwargs):
    raise AssertionError("Unexpected remote acquisition")


def test_verified_cache_reused_without_network_and_identity_is_relocatable(artifacts, monkeypatch):
    monkeypatch.setattr(environment.url_request, "urlopen", _forbid_network)
    original_mtimes = {path.name: path.stat().st_mtime_ns for path in artifacts.directory.iterdir()}

    identity = environment.prepare_artifacts(artifacts.project)
    relocated = artifacts.project / "relocated"
    shutil.copytree(artifacts.directory, relocated / environment._CACHE_DIRECTORY)

    assert environment.artifact_identity(relocated) == identity
    assert identity["cacheDirectory"] == ".cache/androidworld-assets"
    assert len(identity["artifacts"]) == 3
    assert str(artifacts.project) not in str(identity)
    assert original_mtimes == {path.name: path.stat().st_mtime_ns for path in artifacts.directory.iterdir()}


def test_missing_identity_is_read_only_and_does_not_create_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(environment.url_request, "urlopen", _forbid_network)
    with pytest.raises(environment.ArtifactError):
        environment.artifact_identity(tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("source_state", ["missing", "tampered"])
def test_local_release_integrity_failure_never_falls_back_to_download_or_legacy(
    artifacts, monkeypatch, source_state,
):
    release = replace(artifacts.helper, url="repo:assets/release.apk")
    monkeypatch.setattr(environment, "_HELPER_APK", release)
    monkeypatch.setattr(environment.url_request, "urlopen", _forbid_network)
    target = artifacts.directory / release.name
    target.write_bytes(b"preserve-existing-cache")
    legacy = Path(environment.tempfile.gettempdir()) / "android_world/app_data" / release.name
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(artifacts.payload)
    if source_state == "tampered":
        source = artifacts.project / "assets/release.apk"
        source.parent.mkdir()
        source.write_bytes(b"untrusted-release")

    with pytest.raises(environment.ArtifactError):
        environment.prepare_artifacts(artifacts.project)

    assert target.read_bytes() == b"preserve-existing-cache"
    assert not list(artifacts.directory.glob("*.part"))


def test_complete_download_is_checked_before_atomic_replacement(artifacts, monkeypatch):
    target = artifacts.directory / artifacts.helper.name
    target.write_bytes(b"old-damaged-cache")
    publications = []
    original_replace = environment.os.replace

    def publish(source, destination):
        assert Path(source).read_bytes() == artifacts.payload
        assert target.read_bytes() == b"old-damaged-cache"
        publications.append(Path(destination).name)
        original_replace(source, destination)

    monkeypatch.setattr(environment.os, "replace", publish)
    monkeypatch.setattr(
        environment.url_request, "urlopen",
        lambda *args, **kwargs: _Response(artifacts.payload, len(artifacts.payload)),
    )

    identity = environment.prepare_artifacts(artifacts.project)

    assert target.read_bytes() == artifacts.payload
    assert publications == [artifacts.helper.name]
    assert environment.artifact_identity(artifacts.project) == identity
    assert sorted(path.name for path in artifacts.directory.iterdir()) == sorted(artifacts.values)


@pytest.mark.parametrize("mode", ["truncated", "incomplete_read", "oversized", "wrong_length", "wrong_digest"])
def test_failed_download_never_publishes_partial_bytes(artifacts, monkeypatch, mode):
    target = artifacts.directory / artifacts.helper.name
    target.write_bytes(b"keep-existing-damaged-cache")
    payload = artifacts.payload
    count = 0

    class IncompleteResponse(_Response):
        def read1(self, size):
            raise IncompleteRead(b"partial", len(payload))

    def acquire(*args, **kwargs):
        nonlocal count
        count += 1
        assert 0 < kwargs["timeout"] <= environment._NETWORK_TIMEOUT_SECONDS
        if mode == "truncated":
            return _Response(payload[:-7], len(payload))
        if mode == "incomplete_read":
            return IncompleteResponse(payload, len(payload))
        if mode == "oversized":
            return _Response(payload + b"extra")
        if mode == "wrong_length":
            return _Response(payload, len(payload) + 1)
        return _Response(b"x" * len(payload), len(payload))

    monkeypatch.setattr(environment.url_request, "urlopen", acquire)
    with pytest.raises(environment.ArtifactError, match="bounded acquisition"):
        environment.prepare_artifacts(artifacts.project)

    assert count == 2
    assert target.read_bytes() == b"keep-existing-damaged-cache"
    assert sorted(path.name for path in artifacts.directory.iterdir()) == sorted(artifacts.values)


def test_prepare_checks_zip_crc_even_when_digest_matches(artifacts, monkeypatch):
    damaged = bytearray(artifacts.payload)
    damaged[damaged.index(b"fixture-manifest")] ^= 1
    damaged = bytes(damaged)
    monkeypatch.setattr(
        environment, "_HELPER_APK",
        replace(artifacts.helper, sha256=hashlib.sha256(damaged).hexdigest()),
    )
    target = artifacts.directory / artifacts.helper.name
    target.unlink()
    monkeypatch.setattr(environment.url_request, "urlopen", lambda *a, **k: _Response(damaged))

    with pytest.raises(environment.ArtifactError, match="bounded acquisition"):
        environment.prepare_artifacts(artifacts.project)

    assert not target.exists()
    assert not list(artifacts.directory.glob("*.part"))


def test_deadline_prevents_network_acquisition_and_removes_temps(artifacts, monkeypatch):
    (artifacts.directory / artifacts.helper.name).unlink()
    monkeypatch.setattr(environment, "_DOWNLOAD_DEADLINE_SECONDS", 0)
    monkeypatch.setattr(environment.url_request, "urlopen", _forbid_network)
    with pytest.raises(environment.ArtifactError, match="deadline exceeded"):
        environment.prepare_artifacts(artifacts.project)
    assert not list(artifacts.directory.glob("*.part"))


def test_explicit_provisioning_reuses_only_pinned_legacy_bytes(artifacts, monkeypatch):
    target = artifacts.directory / artifacts.app.name
    target.unlink()
    legacy = Path(environment.tempfile.gettempdir()) / "android_world/app_data"
    legacy.mkdir(parents=True)
    (legacy / artifacts.app.name).write_bytes(artifacts.payload)
    monkeypatch.setattr(environment.url_request, "urlopen", _forbid_network)

    environment.prepare_artifacts(artifacts.project)

    assert target.read_bytes() == artifacts.payload
    assert not list(artifacts.directory.glob("*.part"))


@pytest.mark.parametrize("which", ["helper", "app", "map"])
@pytest.mark.parametrize("damage", ["missing", "same_size_corruption"])
def test_damaged_artifacts_fail_before_loader_or_device_mutation(artifacts, monkeypatch, which, damage):
    spec = getattr(artifacts, which)
    path = artifacts.directory / spec.name
    if damage == "missing":
        path.unlink()
    else:
        content = bytearray(path.read_bytes())
        content[0] ^= 1
        path.write_bytes(content)
    monkeypatch.setattr(environment.url_request, "urlopen", _forbid_network)
    monkeypatch.setattr(environment, "create_environment", _forbid_network)

    with pytest.raises(environment.ArtifactError):
        environment.artifact_identity(artifacts.project)
    with pytest.raises(environment.ArtifactError):
        _load(artifacts.project)

    assert (not path.exists()) if damage == "missing" else path.read_bytes() != artifacts.values[spec.name]


@pytest.fixture
def offline_controllers(monkeypatch):
    controllers = []

    class Controller:
        def __init__(self):
            self.closed = False
            self.close_error = None

        def close(self):
            self.closed = True
            if self.close_error is not None:
                raise self.close_error

    def create(*args, **kwargs):
        controller = Controller()
        controllers.append(controller)
        return interface.AsyncAndroidEnv(controller)

    monkeypatch.setattr(environment, "create_environment", create)
    monkeypatch.setattr(environment.env_launcher, "_increase_file_descriptor_limit", lambda: None)
    monkeypatch.setattr(environment.env_launcher.datetime_utils, "setup_datetime", lambda value: None)
    monkeypatch.setattr(environment.env_launcher.setup, "setup_apps", _forbid_network)
    monkeypatch.setattr(environment.url_request, "urlopen", _forbid_network)
    return SimpleNamespace(controllers=controllers)




def test_setup_failure_closes_official_environment(artifacts, offline_controllers, monkeypatch):

    def fail(controller):
        raise ValueError("datetime setup failed")

    monkeypatch.setattr(environment.env_launcher.datetime_utils, "setup_datetime", fail)
    with pytest.raises(ValueError, match="datetime setup failed"):
        _load(artifacts.project, freeze_datetime=True)
    assert offline_controllers.controllers[0].closed


def test_close_failure_propagates(artifacts, offline_controllers):
    env = _load(artifacts.project)
    env.controller.close_error = RuntimeError("controller cleanup failed")
    with pytest.raises(RuntimeError, match="controller cleanup failed"):
        environment.close_environment(env)


def test_setup_and_cleanup_failures_are_both_preserved(artifacts, offline_controllers, monkeypatch):

    def fail(controller):
        controller.close_error = RuntimeError("cleanup evidence")
        raise ValueError("setup evidence")

    monkeypatch.setattr(environment.env_launcher.datetime_utils, "setup_datetime", fail)
    with pytest.raises(ExceptionGroup) as failure:
        _load(artifacts.project, freeze_datetime=True)
    assert [str(error) for error in failure.value.exceptions] == ["setup evidence", "cleanup evidence"]


def test_local_app_data_uses_verified_project_files_and_rejects_new_corruption(artifacts, monkeypatch):
    monkeypatch.setattr(environment.apps, "download_app_data", _forbid_network)
    with environment.local_app_data(artifacts.project):
        assert Path(environment.apps.download_app_data(artifacts.app.name)).read_bytes() == artifacts.payload
        assert Path(environment.apps.download_app_data(artifacts.map.name)).read_bytes() == artifacts.values[artifacts.map.name]
        with pytest.raises(environment.ArtifactError, match="Unprovisioned"):
            environment.apps.download_app_data("unexpected.apk")
        (artifacts.directory / artifacts.map.name).write_bytes(b"corrupt")
        with pytest.raises(environment.ArtifactError):
            environment.apps.download_app_data(artifacts.map.name)
    assert environment.apps.download_app_data is _forbid_network


def test_missing_app_data_fails_before_context_body_and_restores_no_hook(artifacts, monkeypatch):
    monkeypatch.setattr(environment.apps, "download_app_data", _forbid_network)
    (artifacts.directory / artifacts.map.name).unlink()
    entered = False
    with pytest.raises(environment.ArtifactError):
        with environment.local_app_data(artifacts.project):
            entered = True
    assert not entered
    assert environment.apps.download_app_data is _forbid_network


def test_strict_snapshot_restore_escapes_official_runtimeerror_suppression(monkeypatch):
    error = RuntimeError("snapshot missing")

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(environment.app_snapshot, "restore_snapshot", fail)
    task = SimpleNamespace(app_names=["fixture app"])
    env = SimpleNamespace(controller=object())
    with pytest.raises(environment.StrictSnapshotRestoreError, match="Strict snapshot restore failed") as failure:
        with environment.strict_snapshot_restores():
            task_eval.TaskEval._initialize_apps(task, env)
    assert failure.value.__cause__ is error
    assert not isinstance(failure.value, RuntimeError)
    assert environment.app_snapshot.restore_snapshot is fail


def test_strict_snapshot_restore_rejects_internally_swallowed_clear_failure(monkeypatch):
    snapshot = environment.app_snapshot
    monkeypatch.setattr(snapshot.adb_utils, "close_app", lambda *args: None)
    monkeypatch.setattr(snapshot, "_snapshot_path", lambda name: "/snapshot")
    monkeypatch.setattr(snapshot, "_app_data_path", lambda name: "/app")
    monkeypatch.setattr(snapshot.file_utils, "check_directory_exists", lambda *args: True)
    copied = []
    monkeypatch.setattr(snapshot.file_utils, "copy_dir", lambda *args: copied.append(args))
    original_error = RuntimeError("old state could not be removed")

    def fail(*args, **kwargs):
        raise original_error

    monkeypatch.setattr(snapshot.file_utils, "clear_directory", fail)
    with pytest.raises(environment.StrictSnapshotRestoreError) as failure:
        with environment.strict_snapshot_restores():
            snapshot.restore_snapshot("fixture app", object())
    assert failure.value.__cause__ is original_error
    assert copied == []
    assert snapshot.file_utils.clear_directory is fail


def test_strict_snapshot_success_keeps_official_result_and_restores_nested_hooks(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(environment.app_snapshot, "restore_snapshot", lambda *args: sentinel)
    original_restore = environment.app_snapshot.restore_snapshot
    original_clear = environment.app_snapshot.file_utils.clear_directory
    with environment.strict_snapshot_restores():
        outer = environment.app_snapshot.restore_snapshot
        with environment.strict_snapshot_restores():
            assert environment.app_snapshot.restore_snapshot("fixture app", object()) is sentinel
        assert environment.app_snapshot.restore_snapshot is outer
    assert environment.app_snapshot.restore_snapshot is original_restore
    assert environment.app_snapshot.file_utils.clear_directory is original_clear




@pytest.mark.parametrize("corrupt_copy", [False, True])
def test_shared_map_restored_after_storage_wipe_and_device_digest_checked(artifacts, monkeypatch, corrupt_copy):
    device = artifacts.project / "device-maps"
    device.mkdir()
    monkeypatch.setattr(environment.apps.OsmAndApp, "MAP_NAMES", (artifacts.map.name,))
    monkeypatch.setattr(environment.apps.OsmAndApp, "DEVICE_MAPS_PATH", str(device))
    monkeypatch.setattr(environment.file_utils, "mkdir", lambda *args: None)
    untouched = device / "unrelated-marker.gpx"
    untouched.write_bytes(b"not task-owned")

    def push(source, destination, controller):
        target = Path(destination) / Path(source).name
        target.write_bytes(b"damaged" if corrupt_copy else Path(source).read_bytes())
        return adb_pb2.AdbResponse(status=adb_pb2.AdbResponse.Status.OK)

    def issue(args, controller):
        response = adb_pb2.AdbResponse(status=adb_pb2.AdbResponse.Status.OK)
        if args[:2] == ["shell", "sha256sum"]:
            path = Path(args[2])
            response.generic.output = (hashlib.sha256(path.read_bytes()).hexdigest() + "  " + str(path)).encode()
        return response

    monkeypatch.setattr(environment.file_utils, "copy_data_to_device", push)
    monkeypatch.setattr(environment.adb_utils, "issue_generic_request", issue)
    env = SimpleNamespace(controller=object())
    if corrupt_copy:
        with pytest.raises(environment.ArtifactError, match="Device shared asset checksum mismatch"):
            environment.restore_shared_assets(env, artifacts.project, ("osmand",))
    else:
        environment.restore_shared_assets(env, artifacts.project, ("osmand",))
        (device / artifacts.map.name).unlink()
        restored = environment.restore_shared_assets(env, artifacts.project, ("osmand",))
        assert (device / artifacts.map.name).read_bytes() == artifacts.values[artifacts.map.name]
        assert restored == [{"name": artifacts.map.name, "sha256": artifacts.map.sha256, "status": "restored_and_verified"}]
    assert untouched.read_bytes() == b"not task-owned"


@pytest.mark.parametrize("failure", [None, "missing_source", "copy_failure"])
def test_database_replacement_preserves_sibling_database_and_journals(tmp_path, monkeypatch, failure):
    directory = tmp_path / "app databases"
    directory.mkdir()
    target = directory / "playlist's.db"
    sibling = directory / "music_playback_state.db"
    replacement = tmp_path / "replacement.db"

    def database(path, value):
        with sqlite3.connect(path) as connection:
            connection.execute("CREATE TABLE values_table (value TEXT)")
            connection.execute("INSERT INTO values_table VALUES (?)", (value,))

    database(target, "old playlist")
    database(sibling, "preserved queue")
    database(replacement, "new playlist")
    for suffix in ("-wal", "-shm"):
        Path(str(target) + suffix).write_bytes(b"obsolete target journal")
        Path(str(sibling) + suffix).write_bytes(b"unrelated journal bytes")
    original_sibling = {path: path.read_bytes() for path in [sibling, Path(str(sibling) + "-wal"), Path(str(sibling) + "-shm")]}
    original_target = target.read_bytes()

    def issue(command, env, timeout):
        for path in shlex.split(" ".join(command[4:])):
            Path(path).unlink(missing_ok=True)
        return adb_pb2.AdbResponse(status=adb_pb2.AdbResponse.Status.OK)

    def copy(source, destination, env, timeout):
        if failure == "copy_failure":
            return adb_pb2.AdbResponse(status=adb_pb2.AdbResponse.Status.ADB_ERROR)
        Path(destination).write_bytes(Path(source).read_bytes())
        return adb_pb2.AdbResponse(status=adb_pb2.AdbResponse.Status.OK)

    monkeypatch.setattr(environment.adb_utils, "issue_generic_request", issue)
    monkeypatch.setattr(environment.file_utils, "copy_data_to_device", copy)
    controller = SimpleNamespace(env=object())
    if failure == "missing_source":
        replacement.unlink()
        with pytest.raises(FileNotFoundError):
            environment._push_database_file(controller, str(replacement), str(target))
        assert target.read_bytes() == original_target
        assert Path(str(target) + "-wal").exists()
    elif failure == "copy_failure":
        with pytest.raises(Exception, match="Failed to replace target database"):
            environment._push_database_file(controller, str(replacement), str(target))
    else:
        environment._push_database_file(controller, str(replacement), str(target))
        with sqlite3.connect(target) as connection:
            assert connection.execute("SELECT value FROM values_table").fetchall() == [("new playlist",)]
        assert not Path(str(target) + "-wal").exists()
        assert not Path(str(target) + "-shm").exists()
    assert {path: path.read_bytes() for path in original_sibling} == original_sibling
    with sqlite3.connect("file:" + str(sibling) + "?immutable=1", uri=True) as connection:
        assert connection.execute("SELECT value FROM values_table").fetchall() == [("preserved queue",)]
