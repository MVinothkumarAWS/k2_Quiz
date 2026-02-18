"""Video generation — fast path via direct ffmpeg, MoviePy kept as fallback."""

import asyncio
import tempfile
import wave as _wave
from pathlib import Path
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import mutagen.mp3
import mutagen.wave
import numpy as np
from PIL import Image

import config
from src.tts_engine import generate_speech_sync, generate_question_audio, generate_answer_audio, generate_engagement_audio, generate_tick_sound
from src.text_renderer import render_question_frame, render_engagement_frame, hex_to_rgb, get_font
from src.image_fetcher import fetch_image_for_answer
from src.ffmpeg_writer import assemble_video
from src.branding import apply_watermark


# ─── Parallel TTS pre-generation ─────────────────────────────────────────────

async def _gen_all_audio_async(questions_data: list[dict], language: str, format_type: str) -> dict:
    """
    Generate ALL TTS audio for a batch of questions in parallel.
    Returns a dict keyed by question index with paths for q_audio, a_audio, engage_audio.
    Engagement audio and tick sound are shared (same content every question).
    """
    import tempfile

    tmp_dir = Path(tempfile.mkdtemp(prefix="k2_tts_"))

    # Shared audio (same for every question)
    engage_path = tmp_dir / "engage.mp3"
    tick_path   = tmp_dir / "tick.wav"

    # Per-question paths
    q_paths = {i: tmp_dir / f"q_{i}.mp3" for i in range(len(questions_data))}
    a_paths = {i: tmp_dir / f"a_{i}.mp3" for i in range(len(questions_data))}

    # Build all async tasks
    tasks = []

    # Engagement audio (once)
    tasks.append(generate_engagement_audio(engage_path, language, format_type))

    # Per-question audio
    for i, q in enumerate(questions_data):
        tasks.append(generate_question_audio(q["question"], q["options"], q_paths[i], language))
        tasks.append(generate_answer_audio(q["correct"], q["options"][q["correct"]], a_paths[i], language))

    # Run all TTS calls concurrently
    await asyncio.gather(*tasks)

    # Generate tick sound locally (no network)
    generate_tick_sound(tick_path)

    return {
        "engage": engage_path,
        "tick":   tick_path,
        "q":      q_paths,
        "a":      a_paths,
    }


def prefetch_all_audio(questions_data: list[dict], language: str, format_type: str) -> dict:
    """Synchronous wrapper: generate all TTS audio in parallel before video assembly."""
    print(f"  Generating TTS audio for {len(questions_data)} questions in parallel...")
    audio_map = asyncio.run(_gen_all_audio_async(questions_data, language, format_type))
    print(f"  TTS complete.")
    return audio_map


def prefetch_reveal_images(questions_data: list[dict]) -> dict[int, Image.Image]:
    """Fetch reveal images in parallel and keep decoded copies in memory."""
    workers = min(8, max(1, len(questions_data)))
    image_map: dict[int, Image.Image] = {}

    def _load_one(item: tuple[int, dict]) -> tuple[int, Optional[Image.Image]]:
        idx, q = item
        image_setting = q.get("image", "auto")
        if not image_setting:
            return idx, None

        correct_index = q["correct"]
        correct_answer = q["options"][correct_index]
        img_path = fetch_image_for_answer(correct_answer, image_setting)
        if not img_path:
            return idx, None

        try:
            with Image.open(img_path) as img:
                return idx, img.convert("RGB").copy()
        except Exception:
            return idx, None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for idx, img in ex.map(_load_one, enumerate(questions_data)):
            if img is not None:
                image_map[idx] = img

    return image_map


def pil_to_numpy(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to numpy array (kept for compatibility)."""
    return np.array(img)


def create_question_scenes(
    question_data: dict,
    format_type: str,
    language: str,
    question_num: Optional[int] = None,
    total_questions: Optional[int] = None,
    current_score: int = 0,
    audio_map: Optional[dict] = None,
    question_idx: int = 0,
    prefetched_image: Optional[Image.Image] = None,
) -> List[Tuple]:
    """
    Build scene list for one question: [(frame, audio_path, duration), ...]
    Fast path — no MoviePy; uses direct ffmpeg via assemble_video().

    Returns list of (PIL Image, audio Path or None, duration float) tuples.
    """
    def _audio_duration(path: Path) -> float:
        """Get duration of an mp3/wav file without loading it fully."""
        try:
            if str(path).endswith(".mp3"):
                return mutagen.mp3.MP3(str(path)).info.length
            else:
                with _wave.open(str(path)) as wf:
                    return wf.getnframes() / wf.getframerate()
        except Exception:
            return 5.0  # fallback

    question = question_data["question"]
    options  = question_data["options"]
    correct_index = question_data["correct"]
    image_setting = question_data.get("image", "auto")

    scenes: List[Tuple] = []

    # ── Resolve audio paths ───────────────────────────────────────────────────
    if audio_map:
        q_audio   = audio_map["q"][question_idx]
        a_audio   = audio_map["a"][question_idx]
        tick_path = audio_map["tick"]
    else:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            q_audio = Path(f.name)
        asyncio.run(generate_question_audio(question, options, q_audio, language))

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            a_audio = Path(f.name)
        asyncio.run(generate_answer_audio(correct_index, options[correct_index], a_audio, language))

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tick_path = Path(f.name)
        generate_tick_sound(tick_path)

    # ── Scene 1: Question + options (audio duration) ──────────────────────────
    q_dur = _audio_duration(q_audio)
    frame_q = render_question_frame(
        question=question, options=options, format_type=format_type,
        highlight_correct=None, timer_value=None,
        question_num=question_num, total_questions=total_questions, score=current_score,
    )
    scenes.append((frame_q, q_audio, q_dur))

    # ── Silent pause between question audio and countdown ─────────────────────
    # Prevents the tick from clashing immediately after the TTS voice ends
    frame_pause = render_question_frame(
        question=question, options=options, format_type=format_type,
        highlight_correct=None, timer_value=None,
        question_num=question_num, total_questions=total_questions, score=current_score,
    )
    scenes.append((frame_pause, None, config.TIMER_PAUSE_BEFORE))

    # ── Scene 2: Timer countdown ──────────────────────────────────────────────
    for t in range(config.TIMER_DURATION, 0, -1):
        frame_t = render_question_frame(
            question=question, options=options, format_type=format_type,
            highlight_correct=None, timer_value=t,
            question_num=question_num, total_questions=total_questions, score=current_score,
        )
        scenes.append((frame_t, tick_path, config.TIMER_TICK_DURATION))

    # ── Scene 3: Reveal correct answer ───────────────────────────────────────
    reveal_image = prefetched_image
    correct_answer = options[correct_index]
    if reveal_image is None and image_setting:
        img_path = fetch_image_for_answer(correct_answer, image_setting)
        if img_path:
            with Image.open(img_path) as img:
                reveal_image = img.convert("RGB").copy()

    a_dur = _audio_duration(a_audio)
    frame_r = render_question_frame(
        question=question, options=options, format_type=format_type,
        highlight_correct=correct_index, timer_value=None, show_image=reveal_image,
        question_num=question_num, total_questions=total_questions, score=current_score + 1,
    )
    # Hold reveal frame for full answer audio + extra display time
    scenes.append((frame_r, a_audio, a_dur + config.REVEAL_DURATION))

    return scenes


def _make_engagement_scene(
    language: str,
    format_type: str,
    engage_audio_path: Path,
) -> Tuple:
    """Build the engagement screen scene (once per video). Returns (frame, audio, duration)."""
    from src.text_renderer import render_engagement_frame
    try:
        dur = mutagen.mp3.MP3(str(engage_audio_path)).info.length
    except Exception:
        dur = 5.0
    frame = render_engagement_frame(format_type=format_type, language=language)
    return (frame, engage_audio_path, dur + 1.0)


def generate_shorts_video(
    questions_data: list[dict],
    output_dir: Path,
    language: str,
    output_name: Optional[str] = None,
    questions_per_short: int = 2,
) -> list[Path]:
    """
    Generate Shorts videos (questions_per_short questions per video).

    Args:
        questions_data: List of question dicts
        output_dir: Directory to save videos
        language: TTS language
        output_name: Base name for output files
        questions_per_short: Questions per Short video (default: 2)

    Returns:
        List of paths to generated videos
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = []
    base_name = output_name or "quiz_shorts"

    # Batch questions into groups of questions_per_short
    batches = [
        questions_data[i:i + questions_per_short]
        for i in range(0, len(questions_data), questions_per_short)
    ]

    # Pre-fetch ALL TTS audio in parallel
    audio_map = prefetch_all_audio(questions_data, language, "shorts")
    image_map = prefetch_reveal_images(questions_data)

    for batch_idx, batch in enumerate(batches):
        print(f"Generating Shorts video {batch_idx+1}/{len(batches)} ({len(batch)} questions)...")

        all_scenes = []
        for local_idx, q_data in enumerate(batch):
            global_idx = batch_idx * questions_per_short + local_idx
            scenes = create_question_scenes(
                question_data=q_data,
                format_type="shorts",
                language=language,
                question_num=local_idx + 1,
                total_questions=len(batch),
                audio_map=audio_map,
                question_idx=global_idx,
                prefetched_image=image_map.get(global_idx),
            )
            all_scenes.extend(scenes)

        # One engagement screen per Short video
        all_scenes.append(_make_engagement_scene(language, "shorts", audio_map["engage"]))

        output_path = output_dir / f"{base_name}_{batch_idx+1:03d}.mp4"
        assemble_video(all_scenes, output_path)
        output_paths.append(output_path)
        print(f"Saved: {output_path}")

    return output_paths


def generate_full_video(
    questions_data: list[dict],
    output_dir: Path,
    language: str,
    output_name: Optional[str] = None,
    questions_per_video: int = 10,
) -> list[Path]:
    """
    Generate full-length videos with multiple questions.

    Args:
        questions_data: List of question dicts
        output_dir: Directory to save videos
        language: TTS language
        output_name: Base name for output files
        questions_per_video: Number of questions per video

    Returns:
        List of paths to generated videos
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = []
    base_name = output_name or "quiz_full"

    # Batch questions
    batches = [
        questions_data[i:i + questions_per_video]
        for i in range(0, len(questions_data), questions_per_video)
    ]

    # Pre-fetch ALL TTS audio in parallel
    audio_map = prefetch_all_audio(questions_data, language, "full")
    image_map = prefetch_reveal_images(questions_data)

    for batch_idx, batch in enumerate(batches):
        print(f"Generating Full video {batch_idx+1}/{len(batches)}...")

        total_questions = len(batch)
        all_scenes = []

        # Intro scene (3s silent)
        intro_frame = _create_intro_frame(
            title=f"GK Quiz - Part {batch_idx + 1}",
            question_count=total_questions,
        )
        all_scenes.append((intro_frame, None, 3.0))

        # Question scenes
        score = 0
        for q_idx, q_data in enumerate(batch):
            print(f"  Processing question {q_idx+1}/{total_questions}...")
            global_idx = batch_idx * questions_per_video + q_idx
            scenes = create_question_scenes(
                question_data=q_data,
                format_type="full",
                language=language,
                question_num=q_idx + 1,
                total_questions=total_questions,
                current_score=score,
                audio_map=audio_map,
                question_idx=global_idx,
                prefetched_image=image_map.get(global_idx),
            )
            all_scenes.extend(scenes)
            score += 1

        # Engagement + outro
        all_scenes.append(_make_engagement_scene(language, "full", audio_map["engage"]))
        outro_frame = _create_outro_frame(final_score=score, total=total_questions)
        all_scenes.append((outro_frame, None, 4.0))

        output_path = output_dir / f"{base_name}_{batch_idx+1:03d}.mp4"
        assemble_video(all_scenes, output_path)
        output_paths.append(output_path)
        print(f"Saved: {output_path}")

    return output_paths


def _create_intro_frame(title: str, question_count: int) -> Image.Image:
    """Render an intro title frame."""
    from PIL import ImageDraw
    width, height = config.FULL_WIDTH, config.FULL_HEIGHT
    bg_color = hex_to_rgb(config.COLORS["background"])
    text_color = hex_to_rgb(config.COLORS["text"])
    accent_color = hex_to_rgb(config.COLORS["correct"])

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    title_font = get_font(56, bold=True)
    sub_font   = get_font(30)

    bbox = title_font.getbbox(title)
    draw.text(((width - (bbox[2]-bbox[0])) // 2, height // 2 - 60), title, font=title_font, fill=accent_color)

    subtitle = f"{question_count} Questions"
    bbox = sub_font.getbbox(subtitle)
    draw.text(((width - (bbox[2]-bbox[0])) // 2, height // 2 + 30), subtitle, font=sub_font, fill=text_color)

    return apply_watermark(img)


def _create_outro_frame(final_score: int, total: int) -> Image.Image:
    """Render an outro frame with final score."""
    from PIL import ImageDraw
    width, height = config.FULL_WIDTH, config.FULL_HEIGHT
    bg_color = hex_to_rgb(config.COLORS["background"])
    text_color = hex_to_rgb(config.COLORS["text"])
    accent_color = hex_to_rgb(config.COLORS["correct"])

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    title_font = get_font(50, bold=True)
    score_font = get_font(70, bold=True)
    sub_font   = get_font(28)

    title = "வினாடி வினா முடிந்தது!"
    bbox = title_font.getbbox(title)
    draw.text(((width - (bbox[2]-bbox[0])) // 2, height // 2 - 90), title, font=title_font, fill=text_color)

    score_text = f"{final_score}/{total}"
    bbox = score_font.getbbox(score_text)
    draw.text(((width - (bbox[2]-bbox[0])) // 2, height // 2), score_text, font=score_font, fill=accent_color)

    sub_text = f"{config.CHANNEL_NAME} சேனலை லைக் செய்து சப்ஸ்கிரைப் செய்யுங்கள்!"
    bbox = sub_font.getbbox(sub_text)
    draw.text(((width - (bbox[2]-bbox[0])) // 2, height // 2 + 100), sub_text, font=sub_font, fill=text_color)

    return apply_watermark(img)
