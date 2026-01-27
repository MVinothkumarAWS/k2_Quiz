"""Tests for TTS engine."""

import os
import pytest
from pathlib import Path

from src.tts_engine import generate_speech


@pytest.mark.asyncio
async def test_generate_speech_creates_audio_file(tmp_path):
    """Test that generate_speech creates an audio file."""
    output_path = tmp_path / "test_speech.mp3"

    await generate_speech(
        text="Hello, this is a test.",
        output_path=output_path,
        voice="en-US-GuyNeural"
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


@pytest.mark.asyncio
async def test_generate_speech_tamil(tmp_path):
    """Test Tamil voice generation."""
    output_path = tmp_path / "tamil_speech.mp3"

    await generate_speech(
        text="வணக்கம்",
        output_path=output_path,
        voice="ta-IN-ValluvarNeural"
    )

    assert output_path.exists()
