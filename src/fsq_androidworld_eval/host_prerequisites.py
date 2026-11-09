"""Project-local encoder identity and actual official media round-trip probes.

The approved imageio-ffmpeg wheel supplies the encoder; neither the system PATH
nor IMAGEIO_FFMPEG_EXE may silently substitute a different executable. Identity
is frozen with the Harness runtime. Probes run before device preparation, not
halfway through a campaign's first music/video task.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
from pathlib import Path
import subprocess
import tempfile
from typing import Any

import imageio_ffmpeg


def _encoder() -> Path:
    if importlib.metadata.version("imageio-ffmpeg") != "0.6.0":
        raise RuntimeError("Harness requires the locked imageio-ffmpeg==0.6.0 dependency; sync the project environment")
    binaries = Path(imageio_ffmpeg.__file__).parent / "binaries"
    candidates = [path for path in binaries.glob("ffmpeg-*") if path.is_file()]
    if len(candidates) != 1:
        raise RuntimeError("exactly one bundled ffmpeg executable is required; system fallback is forbidden")
    return candidates[0].resolve()


def media_encoder_identity() -> dict[str, Any]:
    executable = _encoder()
    digest = hashlib.sha256()
    with executable.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"package": "imageio-ffmpeg", "version": "0.6.0", "executable": executable.name, "sha256": digest.hexdigest()}


def configure_media_encoder() -> None:
    from pydub import AudioSegment

    AudioSegment.converter = str(_encoder())


def probe_host_media() -> dict[str, Any]:
    import cv2
    from android_world.task_evals.utils import user_data_generation

    configure_media_encoder()
    with tempfile.TemporaryDirectory(prefix="fsq-host-media-") as temporary:
        audio = Path(temporary) / "probe.mp3"
        user_data_generation._create_test_mp3(str(audio), "harness-probe", "harness-probe", 100)
        decoded = subprocess.run(
            [str(_encoder()), "-v", "error", "-i", str(audio), "-f", "s16le", "-acodec", "pcm_s16le", "-"],
            capture_output=True, check=True, timeout=20,
        )
        if not decoded.stdout:
            raise RuntimeError("official MP3 generation produced no decodable audio samples")
        video = Path(temporary) / "probe.mp4"
        user_data_generation._create_mpeg_with_messages(
            str(video), ["harness-probe"], width=64, height=48, fps=2, display_time=1,
        )
        capture = cv2.VideoCapture(str(video))
        try:
            frames = []
            while True:
                available, frame = capture.read()
                if not available:
                    break
                frames.append(frame.shape)
            if frames != [(48, 64, 3), (48, 64, 3)]:
                raise RuntimeError(f"official MP4 generation failed frame decode: {frames}")
        finally:
            capture.release()
    return {"encoder": media_encoder_identity(), "mp3": "encoded_and_decoded", "mp4": "encoded_and_decoded"}
