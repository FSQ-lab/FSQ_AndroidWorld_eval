"""Provision pinned host assets explicitly; create official environments offline.

Only ``prepare_artifacts`` may access the network. The helper APK adapter remains
active until controller cleanup, including official controller refreshes. APK
preparation checks every ZIP member's CRC; runtime checks stream pinned SHA256.
No AndroidWorld or AndroidEnv source files are changed.
Database writes replace only the requested file and its WAL/SHM sidecars; the
upstream directory-wide deletion would destroy other databases in the same app.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
import hashlib
from http.client import HTTPException
import os
from pathlib import Path
import shutil
import shlex
import tempfile
import threading
import time
from typing import Any, Callable, Iterator
from urllib import request as url_request
import zipfile

from android_env.wrappers import a11y_grpc_wrapper
from android_world.env import adb_utils, android_world_controller, env_launcher, interface
from android_world.env.setup_device import apps
from android_world.utils import app_snapshot, file_utils

from fsq_androidworld_eval.host_prerequisites import configure_media_encoder


@dataclass(frozen=True)
class _ArtifactSpec:
    name: str
    url: str
    sha256: str
    size_bytes: int


# Full official response acquired; all 17 APK members passed ZIP CRC validation.
_HELPER_APK = _ArtifactSpec(
    name="2024.05.13-accessibility_forwarder.apk",
    url="https://storage.googleapis.com/android_env-tasks/2024.05.13-accessibility_forwarder.apk",
    sha256="97a56a544e44d79f9b3181fc7dbdd72cffa908efd3d53c82afad1773061a350a",
    size_bytes=4_490_495,
)
# Existing cache bytes were matched against official HTTPS Content-Length and
# x-goog-hash MD5 metadata before pinning SHA256. Every APK passed ZIP CRC checks.
_APP_DATA = tuple(
    _ArtifactSpec(name, f"https://storage.googleapis.com/gresearch/android_world/{name}", digest, size)
    for name, digest, size in (
        ("com.dimowner.audiorecorder_926.apk", "ee0bd709021e4069bb1f6fee99e3398f70ba4531dea918840ad4f5156f97b953", 778419),
        ("com.flauschcode.broccoli_1020600.apk", "da99d9465c79398c6c25459daa82017c5faf505589ea6e62b9e85ca0dc70e8da", 7503922),
        ("clipper.apk", "c5f7a1e4fd78d1141164759a099cdcfb0a7b84aaf4c06a63f52e1aa4f1278539", 10143),
        ("net.cozic.joplin_2097740.apk", "6f70a460f6bacd777d08b13a06c5ef5d545491f940de0a40ecf44fd2d9eea385", 43472265),
        ("net.gsantner.markor_146.apk", "1a328c5324b3b33d6cb4d55085637707252569d98c0ffe1cb7089aebbd903256", 11067299),
        ("de.dennisguse.opentracks_5705.apk", "3cd907e57c747b49fac9120defee4c2395c67acc87271c7c591058cb37e7802c", 24268012),
        ("net.osmand-4.6.13.apk", "0ac411942965a431a0a91b19ce990e6948e780a13a1c98bc7e5a9a057af6463c", 351679694),
        ("Liechtenstein_europe.obf", "57a1955c6f517a114999fa50480ecc1402ed9b524db602540ac1c08f57ff140e", 7241271),
        ("com.arduia.expense_11.apk", "e54dcc8250566ab6421119b48d6c4544066c6697c53d27ab06ee5bdf9bf1ee50", 3020823),
        ("code.name.monkey.retromusic_10603.apk", "13212d049cb02b861c0358bde5fe5b9cdf99a16a490685f60c28636278e2ed60", 9041986),
        ("com.simplemobiletools.calendar.pro_238.apk", "fb4d30ce060433fc9283e591eddc58be0ee1d75b079a13939ca7e6cce8a1f4b8", 9870704),
        ("com.simplemobiletools.draw.pro_79.apk", "3c3210590846a30468ab5acb9ef0aaa5d85b49d5930eda86eef0bd991a9f80a1", 8320484),
        ("com.simplemobiletools.gallery.pro_396.apk", "175f10c9ce4c6d5294ed20d61216d850df2c2b1928a846489a4cb372153d1607", 32203025),
        ("com.simplemobiletools.smsmessenger_85.apk", "e134a0e330514de3716dbacfa08d39707ebbb2c9ebde8d08854e159b2cd7c2f4", 9938539),
        ("org.tasks_130605.apk", "3e93405882016be0e8f6c45207bdfb9d4b958bf34430256e77b043d68b8ceb00", 29656271),
        ("org.videolan.vlc_13050408.apk", "3fe17cbd8b7f507436eccc217f9168846a65cadff2f7d87490f5740b243170dc", 38387336),
        ("org.videolan.vlc_13050407.apk", "2cde3fbd8bf240ff66de236a352c68efa40bb267acf3a5cb8d34a5b2850a2666", 36167316),
    )
)
_CACHE_DIRECTORY = Path(".cache/androidworld-assets")
_DOWNLOAD_ATTEMPTS = 3
_NETWORK_TIMEOUT_SECONDS = 20
_DOWNLOAD_DEADLINE_SECONDS = 300
_CHUNK_SIZE = 64 * 1024
_ENVIRONMENT_LOCK = threading.RLock()
_APP_DATA_LOCK = threading.RLock()
_SNAPSHOT_LOCK = threading.RLock()


class ArtifactError(RuntimeError):
    """A required pinned host artifact is unavailable or invalid."""


class StrictSnapshotRestoreError(Exception):
    """An official snapshot restore failed and must not be silently skipped."""


def _specs() -> tuple[_ArtifactSpec, ...]:
    return (_HELPER_APK, *_APP_DATA)


def _identity() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "cacheDirectory": _CACHE_DIRECTORY.as_posix(),
        "artifacts": [
            {"name": spec.name, "url": spec.url, "sha256": spec.sha256, "sizeBytes": spec.size_bytes}
            for spec in _specs()
        ],
    }


def _verify_file(path: Path, spec: _ArtifactSpec, *, apk_integrity: bool = False) -> None:
    try:
        with path.open("rb") as source:
            if os.fstat(source.fileno()).st_size != spec.size_bytes:
                raise ArtifactError(f"Invalid cached size for {spec.name}")
            digest = hashlib.sha256()
            received = 0
            while chunk := source.read(_CHUNK_SIZE):
                received += len(chunk)
                if received > spec.size_bytes:
                    raise ArtifactError(f"Cached artifact exceeds pinned size: {spec.name}")
                digest.update(chunk)
            if received != spec.size_bytes or digest.hexdigest() != spec.sha256:
                raise ArtifactError(f"SHA256 or size mismatch for {spec.name}")
            if apk_integrity and spec.name.endswith(".apk"):
                source.seek(0)
                with zipfile.ZipFile(source) as archive:
                    if not {"AndroidManifest.xml", "classes.dex"} <= set(archive.namelist()):
                        raise ArtifactError(f"Missing required APK members in {spec.name}")
                    bad_member = archive.testzip()
                    if bad_member is not None:
                        raise ArtifactError(f"APK CRC mismatch: {spec.name}: {bad_member}")
    except (OSError, zipfile.BadZipFile, EOFError) as error:
        raise ArtifactError(
            f"Required artifact unavailable or invalid: {spec.name}; run prepare-assets explicitly"
        ) from error


def artifact_identity(project: Path) -> dict[str, Any]:
    """Verify every cache file read-only; never download, create or repair files."""
    for spec in _specs():
        _verify_file(project / _CACHE_DIRECTORY / spec.name, spec)
    return _identity()


def _download(destination: Any, spec: _ArtifactSpec, deadline: float) -> None:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Artifact acquisition deadline exceeded")
    with url_request.urlopen(
        spec.url, timeout=min(_NETWORK_TIMEOUT_SECONDS, remaining)
    ) as response:
        length = response.headers.get("Content-Length")
        if length is not None and int(length) != spec.size_bytes:
            raise ArtifactError(f"Unexpected Content-Length for {spec.name}: {length}")
        received = 0
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("Artifact acquisition deadline exceeded")
            chunk = response.read1(min(_CHUNK_SIZE, spec.size_bytes + 1 - received))
            if not chunk:
                break
            received += len(chunk)
            if received > spec.size_bytes:
                raise ArtifactError(f"Download exceeds pinned size: {spec.name}")
            destination.write(chunk)


def _prepare_one(project: Path, spec: _ArtifactSpec) -> None:
    directory = project / _CACHE_DIRECTORY
    target = directory / spec.name
    try:
        _verify_file(target, spec, apk_integrity=True)
        return
    except ArtifactError:
        pass

    directory.mkdir(parents=True, exist_ok=True)
    # Explicit preparation may reuse upstream's old cache, but never trust its
    # mere presence. Verify a copied snapshot against the baked-in official pin.
    legacy = Path(tempfile.gettempdir()) / "android_world/app_data" / spec.name
    deadline = time.monotonic() + _DOWNLOAD_DEADLINE_SECONDS
    last_error: Exception | None = None
    for attempt in range(_DOWNLOAD_ATTEMPTS):
        temporary: Path | None = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{spec.name}.", suffix=".part", dir=directory
            )
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, "wb") as destination:
                use_legacy = False
                if attempt == 0:
                    try:
                        use_legacy = legacy.stat().st_size == spec.size_bytes
                    except OSError:
                        pass
                if use_legacy:
                    with legacy.open("rb") as source:
                        shutil.copyfileobj(source, destination, length=_CHUNK_SIZE)
                else:
                    _download(destination, spec, deadline)
                destination.flush()
                os.fsync(destination.fileno())
            _verify_file(temporary, spec, apk_integrity=True)
            os.replace(temporary, target)
            return
        except (OSError, ValueError, HTTPException, ArtifactError) as error:
            last_error = error
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    raise ArtifactError(
        f"Failed to provision {spec.name} after bounded acquisition: {last_error}"
    ) from last_error


def prepare_artifacts(project: Path) -> dict[str, Any]:
    """Explicitly provision all pins, publishing each verified file atomically.

    Each artifact has three acquisition attempts, a socket timeout, an overall
    deadline checked between reads, and an exact pinned size cap. Failed attempts
    remove their temporary files and never replace an existing cache entry.
    """
    for spec in _specs():
        _prepare_one(project, spec)
    return _identity()


@contextmanager
def local_app_data(project: Path) -> Iterator[None]:
    """Make official qualification consume pinned local APK/map files only."""
    artifact_identity(project)
    with _APP_DATA_LOCK:
        original_download = apps.download_app_data
        specs = {spec.name: spec for spec in _APP_DATA}

        def local(file_name: str) -> str:
            if file_name not in specs:
                raise ArtifactError(f"Unprovisioned official app asset requested: {file_name}")
            path = project / _CACHE_DIRECTORY / file_name
            _verify_file(path, specs[file_name])
            return str(path)

        apps.download_app_data = local
        try:
            yield
        finally:
            apps.download_app_data = original_download


def restore_shared_assets(env: interface.AsyncEnv, project: Path, app_names: tuple[str, ...] | list[str]) -> list[dict[str, Any]]:
    """Restore only official fixed shared data, never task answers or app state.

    File/media tasks delete regular shared-storage files; private app snapshots do
    not restore the OsmAnd map. Reapply the same pinned map as official app setup
    before each dependent task and verify actual device bytes. This is outside the
    Agent budget and cannot generate requested markers/tracks/favorites.
    """
    if apps.OsmAndApp.app_name not in app_names:
        return []
    maps = apps.OsmAndApp
    file_utils.mkdir(maps.DEVICE_MAPS_PATH, env.controller)
    with local_app_data(project):
        maps._copy_data_to_device(maps.MAP_NAMES, maps.DEVICE_MAPS_PATH, env)
    result = []
    for name in maps.MAP_NAMES:
        spec = next(spec for spec in _APP_DATA if spec.name == name)
        destination = maps.DEVICE_MAPS_PATH.rstrip("/") + "/" + name
        adb_utils.check_ok(
            adb_utils.issue_generic_request(
                ["shell", "chcon", "u:object_r:media_rw_data_file:s0", destination], env.controller,
            ),
            f"Failed to restore shared asset context: {name}",
        )
        response = adb_utils.issue_generic_request(["shell", "sha256sum", destination], env.controller)
        adb_utils.check_ok(response, f"Failed to verify shared asset: {name}")
        if response.generic.output.decode("utf-8").split()[:1] != [spec.sha256]:
            raise ArtifactError(f"Device shared asset checksum mismatch: {name}")
        result.append({"name": name, "sha256": spec.sha256, "status": "restored_and_verified"})
    return result


@dataclass
class _GetterLease:
    payload: bytes
    original: Callable[[], bytes]
    users: int = 0


_getter_lease: _GetterLease | None = None


def _acquire_getter(payload: bytes) -> Callable[[], None]:
    """Called under the environment lock; release is safe on every failure path."""
    global _getter_lease
    if _getter_lease is None:
        _getter_lease = _GetterLease(
            payload=payload,
            original=a11y_grpc_wrapper._get_accessibility_forwarder_apk,
        )
        a11y_grpc_wrapper._get_accessibility_forwarder_apk = lambda: payload
    elif _getter_lease.payload != payload:
        raise ArtifactError("Cannot mix different helper APKs in live environments")
    lease = _getter_lease
    lease.users += 1
    released = False

    def release() -> None:
        nonlocal released
        global _getter_lease
        with _ENVIRONMENT_LOCK:
            if released:
                return
            released = True
            lease.users -= 1
            if lease.users == 0:
                a11y_grpc_wrapper._get_accessibility_forwarder_apk = lease.original
                _getter_lease = None

    return release


@contextmanager
def _capture_construction(owners: list[Any]) -> Iterator[None]:
    """Retain completed owners even if a later official constructor raises.

    Failures inside loader.load or the a11y wrapper's own constructor can precede
    their return; upstream does not expose those private partial objects.
    """
    loader = android_world_controller.loader
    original_load = loader.load
    original_wrap = android_world_controller.apply_a11y_forwarder_app_wrapper

    def load(*args: Any, **kwargs: Any) -> Any:
        owner = original_load(*args, **kwargs)
        owners.append(owner)
        return owner

    def wrap(*args: Any, **kwargs: Any) -> Any:
        owner = original_wrap(*args, **kwargs)
        owners.append(owner)
        return owner

    loader.load = load
    android_world_controller.apply_a11y_forwarder_app_wrapper = wrap
    try:
        yield
    finally:
        android_world_controller.apply_a11y_forwarder_app_wrapper = original_wrap
        loader.load = original_load


def close_environment(env: interface.AsyncEnv) -> None:
    """Run official controller cleanup without AsyncAndroidEnv's suppression.

    Environments returned by load_environment release their APK adapter even if
    controller cleanup raises. Callers must treat such an exception as failure.
    """
    env.controller.close()


def _push_database_file(controller: Any, local_path: str, remote_path: str, timeout_sec: float | None = None) -> None:
    """Replace one database, never sibling databases or their journals."""
    if not Path(local_path).is_file():
        raise FileNotFoundError(local_path)
    targets = [remote_path, remote_path + "-wal", remote_path + "-shm"]
    adb_utils.check_ok(
        adb_utils.issue_generic_request(
            ["shell", "rm", "-f", "--", *(shlex.quote(path) for path in targets)],
            controller.env, timeout_sec,
        ),
        f"Failed to remove target database sidecars: {remote_path}",
    )
    adb_utils.check_ok(
        file_utils.copy_data_to_device(local_path, remote_path, controller.env, timeout_sec),
        f"Failed to replace target database: {remote_path}",
    )


def _own_controller_lifetime(env: interface.AsyncEnv, owners: list[Any], release: Callable[[], None]) -> None:
    """Close retired refresh owners and never mistake a failed refresh for cleanup."""
    controller = env.controller
    original_close = controller.close
    original_refresh = getattr(controller, "refresh_env", None)
    closed: set[int] = set()
    refresh_errors: list[BaseException] = []

    def mark_closed(owner: Any) -> None:
        while owner is not None and id(owner) not in closed:
            closed.add(id(owner))
            owner = getattr(owner, "_env", None)

    def refresh() -> None:
        with _ENVIRONMENT_LOCK:
            previous = getattr(controller, "_env", None)
            try:
                with _capture_construction(owners):
                    original_refresh()
                if previous is not None and previous is not getattr(controller, "_env", None):
                    previous.close()
                    mark_closed(previous)
            except BaseException as error:
                refresh_errors.append(error)
                raise

    def close() -> None:
        errors = list(refresh_errors)
        try:
            current = getattr(controller, "_env", None)
            try:
                original_close()
                mark_closed(current)
            except BaseException as error:
                errors.append(error)
            # A wrapper failure must not prevent independent raw-owner cleanup.
            for owner in reversed(owners):
                if id(owner) in closed:
                    continue
                try:
                    owner.close()
                    mark_closed(owner)
                except BaseException as error:
                    errors.append(error)
        finally:
            release()
        if len(errors) == 1:
            raise errors[0]
        if errors:
            raise BaseExceptionGroup("Environment owner cleanup failed", errors)

    controller.close = close
    controller.push_file = lambda local_db_file_path, remote_db_file_path, timeout_sec=None: _push_database_file(
        controller, local_db_file_path, remote_db_file_path, timeout_sec,
    )
    if original_refresh is not None:
        controller.refresh_env = refresh


def load_environment(
    *,
    artifact_root: Path,
    console_port: int,
    adb_path: str,
    grpc_port: int,
    freeze_datetime: bool,
) -> interface.AsyncEnv:
    """Create and set up an official AsyncEnv using only verified local APK bytes."""
    artifact_identity(artifact_root)
    helper_path = artifact_root / _CACHE_DIRECTORY / _HELPER_APK.name
    with helper_path.open("rb") as source:
        payload = source.read(_HELPER_APK.size_bytes + 1)
    if len(payload) != _HELPER_APK.size_bytes or hashlib.sha256(payload).hexdigest() != _HELPER_APK.sha256:
        raise ArtifactError("Helper APK changed after artifact verification")
    configure_media_encoder()
    with _ENVIRONMENT_LOCK:
        release = _acquire_getter(payload)
        owners: list[Any] = []
        env: interface.AsyncEnv | None = None
        try:
            with _capture_construction(owners):
                env = env_launcher._get_env(console_port, adb_path, grpc_port)
            _own_controller_lifetime(env, owners, release)
            env_launcher.setup_env(
                env, emulator_setup=False, freeze_datetime=freeze_datetime
            )
            return env
        except BaseException as error:
            cleanup_errors: list[BaseException] = []
            if env is not None:
                try:
                    close_environment(env)
                except BaseException as cleanup_error:
                    cleanup_errors.append(cleanup_error)
            else:
                # Raw AndroidEnv.close is idempotent. Explicitly try it as well
                # if outer wrapper cleanup raises before reaching its raw owner.
                for owner in reversed(owners):
                    try:
                        owner.close()
                    except BaseException as cleanup_error:
                        cleanup_errors.append(cleanup_error)
            release()
            if cleanup_errors:
                raise BaseExceptionGroup(
                    "Environment initialization and cleanup failed",
                    [error, *cleanup_errors],
                ) from None
            raise


@contextmanager
def strict_snapshot_restores() -> Iterator[None]:
    """Keep official restore failures from being downgraded to warning-only.

    TaskEval catches RuntimeError from restore_snapshot, and restore_snapshot
    itself catches RuntimeError from clear_directory. Convert at both boundaries
    without changing the successful official restore implementation.
    """
    with _SNAPSHOT_LOCK:
        original_restore = app_snapshot.restore_snapshot

        @wraps(original_restore)
        def restore(app_name: str, *args: Any, **kwargs: Any) -> Any:
            with _SNAPSHOT_LOCK:
                original_clear = app_snapshot.file_utils.clear_directory

                @wraps(original_clear)
                def clear(*clear_args: Any, **clear_kwargs: Any) -> Any:
                    try:
                        return original_clear(*clear_args, **clear_kwargs)
                    except RuntimeError as error:
                        raise StrictSnapshotRestoreError(
                            f"Strict snapshot restore failed for {app_name}: {error}"
                        ) from error

                app_snapshot.file_utils.clear_directory = clear
                try:
                    return original_restore(app_name, *args, **kwargs)
                except RuntimeError as error:
                    raise StrictSnapshotRestoreError(
                        f"Strict snapshot restore failed for {app_name}: {error}"
                    ) from error
                finally:
                    app_snapshot.file_utils.clear_directory = original_clear

        app_snapshot.restore_snapshot = restore
        try:
            yield
        finally:
            app_snapshot.restore_snapshot = original_restore
