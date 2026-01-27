"""Video generation using MoviePy."""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image

from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
    ColorClip,
    TextClip,
)

import config
from src.tts_engine import generate_speech_sync, generate_question_audio
from src.text_renderer import render_question_frame, hex_to_rgb
from src.image_fetcher import fetch_image_for_answer


def pil_to_numpy(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to numpy array for MoviePy."""
    return np.array(img)


def create_question_clip(
    question_data: dict,
    format_type: str,
    language: str,
    question_num: Optional[int] = None,
    total_questions: Optional[int] = None,
    current_score: int = 0,
) -> CompositeVideoClip:
    """
    Create a video clip for a single question.

    Args:
        question_data: Dict with question, options, correct, image
        format_type: "shorts" or "full"
        language: Language for TTS
        question_num: Current question number (for full format)
        total_questions: Total questions (for full format)
        current_score: Current score (for full format)

    Returns:
        MoviePy CompositeVideoClip
    """
    question = question_data["question"]
    options = question_data["options"]
    correct_index = question_data["correct"]
    image_setting = question_data.get("image")

    # Get dimensions
    if format_type == "shorts":
        width, height = config.SHORTS_WIDTH, config.SHORTS_HEIGHT
    else:
        width, height = config.FULL_WIDTH, config.FULL_HEIGHT

    clips = []

    # Generate TTS audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
        audio_path = Path(tmp_audio.name)

    asyncio.run(generate_question_audio(question, options, audio_path, language))
    audio_clip = AudioFileClip(str(audio_path))
    audio_duration = audio_clip.duration

    # Phase 1: Question and options appear (during TTS)
    frame_question = render_question_frame(
        question=question,
        options=options,
        format_type=format_type,
        highlight_correct=None,
        timer_value=None,
        question_num=question_num,
        total_questions=total_questions,
        score=current_score,
    )
    clip_question = ImageClip(pil_to_numpy(frame_question)).with_duration(audio_duration)
    clip_question = clip_question.with_audio(audio_clip)
    clips.append(clip_question)

    # Phase 2: Timer countdown (5 seconds)
    for t in range(config.TIMER_DURATION, 0, -1):
        frame_timer = render_question_frame(
            question=question,
            options=options,
            format_type=format_type,
            highlight_correct=None,
            timer_value=t,
            question_num=question_num,
            total_questions=total_questions,
            score=current_score,
        )
        clip_timer = ImageClip(pil_to_numpy(frame_timer)).with_duration(1)
        clips.append(clip_timer)

    # Phase 3: Reveal correct answer
    # Fetch image if full format
    reveal_image = None
    if format_type == "full" and image_setting:
        correct_answer = options[correct_index]
        image_path = fetch_image_for_answer(correct_answer, image_setting)
        if image_path:
            reveal_image = Image.open(image_path)

    frame_reveal = render_question_frame(
        question=question,
        options=options,
        format_type=format_type,
        highlight_correct=correct_index,
        timer_value=0,
        show_image=reveal_image,
        question_num=question_num,
        total_questions=total_questions,
        score=current_score + 1,  # Show updated score
    )
    clip_reveal = ImageClip(pil_to_numpy(frame_reveal)).with_duration(
        config.PAUSE_AFTER_REVEAL + config.FADE_DURATION
    )
    clips.append(clip_reveal)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Cleanup temp audio file
    audio_path.unlink(missing_ok=True)

    return final_clip


def generate_shorts_video(
    questions_data: list[dict],
    output_dir: Path,
    language: str,
    output_name: Optional[str] = None,
) -> list[Path]:
    """
    Generate Shorts videos (one per question).

    Args:
        questions_data: List of question dicts
        output_dir: Directory to save videos
        language: TTS language
        output_name: Base name for output files

    Returns:
        List of paths to generated videos
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = []
    base_name = output_name or "quiz_shorts"

    for i, q_data in enumerate(questions_data):
        print(f"Generating Shorts video {i+1}/{len(questions_data)}...")

        clip = create_question_clip(
            question_data=q_data,
            format_type="shorts",
            language=language,
        )

        output_path = output_dir / f"{base_name}_{i+1:03d}.mp4"
        clip.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )
        clip.close()

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

    for batch_idx, batch in enumerate(batches):
        print(f"Generating Full video {batch_idx+1}/{len(batches)}...")

        clips = []
        total_questions = len(batch)

        # Intro clip
        intro_clip = _create_intro_clip(
            title=f"GK Quiz - Part {batch_idx + 1}",
            question_count=total_questions,
        )
        clips.append(intro_clip)

        # Question clips
        score = 0
        for q_idx, q_data in enumerate(batch):
            print(f"  Processing question {q_idx+1}/{total_questions}...")

            clip = create_question_clip(
                question_data=q_data,
                format_type="full",
                language=language,
                question_num=q_idx + 1,
                total_questions=total_questions,
                current_score=score,
            )
            clips.append(clip)
            score += 1  # Assume all answers shown as correct

        # Outro clip
        outro_clip = _create_outro_clip(final_score=score, total=total_questions)
        clips.append(outro_clip)

        # Concatenate
        final_clip = concatenate_videoclips(clips, method="compose")

        output_path = output_dir / f"{base_name}_{batch_idx+1:03d}.mp4"
        final_clip.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )
        final_clip.close()

        output_paths.append(output_path)
        print(f"Saved: {output_path}")

    return output_paths


def _create_intro_clip(title: str, question_count: int, duration: float = 3.0) -> ImageClip:
    """Create an intro title clip."""
    width, height = config.FULL_WIDTH, config.FULL_HEIGHT
    bg_color = hex_to_rgb(config.COLORS["background"])
    text_color = hex_to_rgb(config.COLORS["text"])
    accent_color = hex_to_rgb(config.COLORS["correct"])

    img = Image.new("RGB", (width, height), bg_color)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    from src.text_renderer import get_font
    title_font = get_font(80, bold=True)
    sub_font = get_font(40)

    # Title
    bbox = title_font.getbbox(title)
    title_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((title_x, height // 2 - 80), title, font=title_font, fill=accent_color)

    # Subtitle
    subtitle = f"{question_count} Questions"
    bbox = sub_font.getbbox(subtitle)
    sub_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((sub_x, height // 2 + 40), subtitle, font=sub_font, fill=text_color)

    return ImageClip(pil_to_numpy(img)).with_duration(duration)


def _create_outro_clip(final_score: int, total: int, duration: float = 4.0) -> ImageClip:
    """Create an outro clip with final score."""
    width, height = config.FULL_WIDTH, config.FULL_HEIGHT
    bg_color = hex_to_rgb(config.COLORS["background"])
    text_color = hex_to_rgb(config.COLORS["text"])
    accent_color = hex_to_rgb(config.COLORS["correct"])

    img = Image.new("RGB", (width, height), bg_color)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    from src.text_renderer import get_font
    title_font = get_font(70, bold=True)
    score_font = get_font(100, bold=True)
    sub_font = get_font(40)

    # Title
    title = "Quiz Complete!"
    bbox = title_font.getbbox(title)
    title_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((title_x, height // 2 - 120), title, font=title_font, fill=text_color)

    # Score
    score_text = f"{final_score}/{total}"
    bbox = score_font.getbbox(score_text)
    score_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((score_x, height // 2), score_text, font=score_font, fill=accent_color)

    # Subscribe text
    sub_text = "Like & Subscribe for more!"
    bbox = sub_font.getbbox(sub_text)
    sub_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((sub_x, height // 2 + 140), sub_text, font=sub_font, fill=text_color)

    return ImageClip(pil_to_numpy(img)).with_duration(duration)
