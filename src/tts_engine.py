"""Text-to-Speech engine using Edge TTS."""

import asyncio
import edge_tts
from pathlib import Path
from typing import Union

import config


async def generate_speech(
    text: str,
    output_path: Union[str, Path],
    voice: str = None,
    language: str = "english"
) -> Path:
    """
    Generate speech audio from text using Edge TTS.

    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        voice: Specific voice to use (overrides language)
        language: Language key from config.VOICES

    Returns:
        Path to the generated audio file
    """
    output_path = Path(output_path)

    if voice is None:
        voice = config.VOICES.get(language, config.VOICES["english"])

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

    return output_path


def generate_speech_sync(
    text: str,
    output_path: Union[str, Path],
    voice: str = None,
    language: str = "english"
) -> Path:
    """Synchronous wrapper for generate_speech."""
    return asyncio.run(generate_speech(text, output_path, voice, language))


async def generate_question_audio(
    question: str,
    options: list[str],
    output_path: Union[str, Path],
    language: str = "english"
) -> Path:
    """
    Generate audio for a complete question with options.

    Args:
        question: The question text
        options: List of option texts
        output_path: Path to save the audio file
        language: Language for TTS

    Returns:
        Path to the generated audio file
    """
    option_labels = ["A", "B", "C", "D"]

    full_text = question + ". "
    for label, option in zip(option_labels, options):
        full_text += f"Option {label}: {option}. "

    return await generate_speech(full_text, output_path, language=language)
