"""Text-to-Speech engine using Edge TTS."""

import asyncio
import edge_tts
import numpy as np
import wave
import struct
from pathlib import Path
from typing import Union

import config


async def generate_speech(
    text: str,
    output_path: Union[str, Path],
    voice: str = None,
) -> Path:
    """
    Generate Tamil speech audio from text using Edge TTS.

    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        voice: Specific voice to use (defaults to Tamil voice from config)

    Returns:
        Path to the generated audio file
    """
    output_path = Path(output_path)

    if voice is None:
        voice = config.VOICES["tamil"]

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

    return output_path


def generate_speech_sync(
    text: str,
    output_path: Union[str, Path],
    voice: str = None,
) -> Path:
    """Synchronous wrapper for generate_speech."""
    return asyncio.run(generate_speech(text, output_path, voice))


async def generate_question_audio(
    question: str,
    options: list[str],
    output_path: Union[str, Path],
    language: str = "tamil",
) -> Path:
    """
    Generate Tamil audio for a complete question with options.

    Args:
        question: The question text
        options: List of option texts
        output_path: Path to save the audio file
        language: Unused, kept for API compatibility (always Tamil)

    Returns:
        Path to the generated audio file
    """
    option_labels = ["A", "B", "C", "D"]

    full_text = question + ". "
    for label, option in zip(option_labels, options):
        full_text += f"{label}: {option}. "
    full_text += "சரியான பதில் எது? யோசித்து சொல்லுங்கள்."

    return await generate_speech(full_text, output_path)


async def generate_answer_audio(
    correct_index: int,
    correct_answer: str,
    output_path: Union[str, Path],
    language: str = "tamil",
) -> Path:
    """
    Generate Tamil audio announcing the correct answer.

    Args:
        correct_index: Index of correct answer (0-3)
        correct_answer: The correct answer text
        output_path: Path to save the audio file
        language: Unused, kept for API compatibility (always Tamil)

    Returns:
        Path to the generated audio file
    """
    option_label = ["A", "B", "C", "D"][correct_index]
    text = config.ANSWER_TEXT_TAMIL.format(option=option_label, answer=correct_answer)
    return await generate_speech(text, output_path)


async def generate_engagement_audio(
    output_path: Union[str, Path],
    language: str = "tamil",
    format_type: str = "full",
) -> Path:
    """
    Generate Tamil engagement audio (like, share, subscribe).

    Args:
        output_path: Path to save the audio file
        language: Unused, kept for API compatibility (always Tamil)
        format_type: "shorts" or "full" — determines engagement text

    Returns:
        Path to the generated audio file
    """
    text = (
        config.ENGAGEMENT_TEXT_SHORTS_TAMIL
        if format_type == "shorts"
        else config.ENGAGEMENT_TEXT_FULL_TAMIL
    )
    return await generate_speech(text, output_path)


def generate_tick_sound(
    output_path: Union[str, Path],
    frequency: int = 880,
    duration: float = 0.5,
    sample_rate: int = 44100,
) -> Path:
    """
    Generate a tick/beep sound for the countdown timer.

    Args:
        output_path: Path to save the audio file
        frequency: Frequency of the beep in Hz (default 880 = A5, crisp and clear)
        duration: Duration of the beep in seconds (default 0.5)
        sample_rate: Audio sample rate (default 44100)

    Returns:
        Path to the generated audio file
    """
    output_path = Path(output_path)

    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, False)

    # Main tone + subtle harmonic for a richer beep
    tone = np.sin(2 * np.pi * frequency * t) * 0.7
    tone += np.sin(2 * np.pi * frequency * 2 * t) * 0.15   # one octave up

    # Fade in (5ms) and fade out (80ms) to avoid clicks and give natural decay
    fade_in_samples  = int(sample_rate * 0.005)
    fade_out_samples = int(sample_rate * 0.08)
    tone[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)
    tone[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

    # Convert to 16-bit integers at 80% of max
    tone = (tone * 32767 * 0.8).astype(np.int16)

    with wave.open(str(output_path), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(tone.tobytes())

    return output_path
