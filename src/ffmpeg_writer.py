"""
Fast video assembly using direct ffmpeg calls.

Instead of MoviePy's slow Python-frame-pipe approach, each scene is:
  1. Rendered as a PNG by PIL/GDI (fast)
  2. Combined with its audio by ffmpeg (fast)
  3. All scenes concatenated with stream-copy (instant)

This is typically 5-8x faster than MoviePy for slide-show style videos.
"""

import subprocess
import tempfile
import shutil
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Tuple
from PIL import Image
import numpy as np


def _find_ffmpeg() -> str:
    """Return path to ffmpeg executable."""
    # 1. Try imageio_ffmpeg (bundled with MoviePy)
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass

    # 2. Try system PATH
    import shutil as _sh
    ffmpeg = _sh.which("ffmpeg") or _sh.which("ffmpeg.exe")
    if ffmpeg:
        return ffmpeg

    raise FileNotFoundError(
        "ffmpeg not found. Run: pip install imageio-ffmpeg"
    )


FFMPEG = _find_ffmpeg()
FFMPEG_PRESET = os.getenv("K2_FFMPEG_PRESET", "veryfast")
FFMPEG_CRF = os.getenv("K2_FFMPEG_CRF", "23")
FFMPEG_DEBUG = os.getenv("K2_FFMPEG_DEBUG", "0") == "1"


# ─── Scene = (PIL Image, audio_path, duration_seconds) ──────────────────────

Scene = Tuple[Image.Image, Path, float]   # (frame_image, audio_path, duration)


def _png_scene(frame: Image.Image, audio_path: Path, duration: float, work_dir: Path, idx: int) -> Path:
    """
    Create one MP4 segment: static PNG + audio, trimmed to `duration` seconds.
    Returns path to the segment MP4.
    """
    png_path = work_dir / f"scene_{idx:04d}.png"
    seg_path = work_dir / f"scene_{idx:04d}.mp4"

    frame.save(str(png_path), "PNG")

    cmd = [
        FFMPEG, "-y",
        "-loop", "1",
        "-i", str(png_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-ar", "44100",        # force consistent sample rate across all segments
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),   # always hold for full duration even after audio ends
        "-preset", FFMPEG_PRESET,
        "-crf", FFMPEG_CRF,
        str(seg_path),
    ]
    subprocess.run(
        cmd,
        check=True,
        stdout=None if FFMPEG_DEBUG else subprocess.DEVNULL,
        stderr=None if FFMPEG_DEBUG else subprocess.DEVNULL,
    )
    return seg_path


def _silent_scene(frame: Image.Image, duration: float, work_dir: Path, idx: int) -> Path:
    """
    Create one silent MP4 segment (no audio): static PNG for `duration` seconds.
    """
    png_path = work_dir / f"scene_{idx:04d}.png"
    seg_path = work_dir / f"scene_{idx:04d}.mp4"

    frame.save(str(png_path), "PNG")

    cmd = [
        FFMPEG, "-y",
        "-loop", "1",
        "-i", str(png_path),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=44100",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-ar", "44100",        # force consistent sample rate across all segments
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
        "-preset", FFMPEG_PRESET,
        "-crf", FFMPEG_CRF,
        "-shortest",
        str(seg_path),
    ]
    subprocess.run(
        cmd,
        check=True,
        stdout=None if FFMPEG_DEBUG else subprocess.DEVNULL,
        stderr=None if FFMPEG_DEBUG else subprocess.DEVNULL,
    )
    return seg_path


def assemble_video(
    scenes: List[Tuple[Image.Image, Path | None, float]],
    output_path: Path,
    fps: int = 30,
) -> Path:
    """
    Assemble a video from a list of (frame_image, audio_path_or_None, duration) scenes.

    - Each scene is a static image held for `duration` seconds with optional audio.
    - All scenes are concatenated via ffmpeg concat demuxer (stream copy = instant).
    - Output is a valid MP4 at the given fps.

    Args:
        scenes: List of (PIL Image, audio Path or None, duration float)
        output_path: Where to save the final MP4
        fps: Video frame rate

    Returns:
        Path to the output MP4
    """
    work_dir = Path(tempfile.mkdtemp(prefix="k2_ffmpeg_"))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        seg_paths = [None] * len(scenes)

        def _build_segment(item: tuple[int, tuple[Image.Image, Path | None, float]]) -> tuple[int, Path]:
            idx, (frame, audio_path, duration) = item
            if audio_path and Path(audio_path).exists() and Path(audio_path).stat().st_size > 100:
                return idx, _png_scene(frame, Path(audio_path), duration, work_dir, idx)
            return idx, _silent_scene(frame, duration, work_dir, idx)

        workers_env = os.getenv("K2_FFMPEG_WORKERS", "").strip()
        if workers_env.isdigit():
            max_workers = max(1, int(workers_env))
        else:
            max_workers = 2 if len(scenes) > 8 else 1

        if max_workers == 1:
            for item in enumerate(scenes):
                idx, seg = _build_segment(item)
                seg_paths[idx] = seg
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                for idx, seg in ex.map(_build_segment, enumerate(scenes)):
                    seg_paths[idx] = seg

        # Write concat list
        concat_list = work_dir / "concat.txt"
        with open(concat_list, "w") as f:
            for seg in seg_paths:
                f.write(f"file '{seg.as_posix()}'\n")

        # Concatenate with stream copy
        cmd = [
            FFMPEG, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output_path),
        ]
        subprocess.run(
            cmd,
            check=True,
            stdout=None if FFMPEG_DEBUG else subprocess.DEVNULL,
            stderr=None if FFMPEG_DEBUG else subprocess.DEVNULL,
        )

        return output_path

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
