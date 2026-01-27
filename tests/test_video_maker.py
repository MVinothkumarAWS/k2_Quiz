"""Tests for video maker."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from src.video_maker import (
    create_question_clip,
    generate_shorts_video,
    generate_full_video,
)


@pytest.fixture
def sample_question():
    return {
        "question": "What is the capital of France?",
        "options": ["London", "Paris", "Berlin", "Madrid"],
        "correct": 1,
    }


def test_create_question_clip_returns_clip(sample_question):
    """Test that create_question_clip returns a MoviePy clip."""
    # Mock generate_question_audio (async function called via asyncio.run)
    with patch("src.video_maker.asyncio.run") as mock_asyncio_run:
        mock_asyncio_run.return_value = Path("/tmp/test_audio.mp3")

        # Mock AudioFileClip
        with patch("src.video_maker.AudioFileClip") as mock_audio_clip:
            mock_audio_instance = MagicMock()
            mock_audio_instance.duration = 5.0
            mock_audio_clip.return_value = mock_audio_instance

            # Mock ImageClip
            with patch("src.video_maker.ImageClip") as mock_image_clip:
                mock_clip_instance = MagicMock()
                mock_clip_instance.set_duration.return_value = mock_clip_instance
                mock_clip_instance.set_audio.return_value = mock_clip_instance
                mock_clip_instance.duration = 1.0
                mock_image_clip.return_value = mock_clip_instance

                # Mock concatenate_videoclips
                with patch("src.video_maker.concatenate_videoclips") as mock_concat:
                    mock_final_clip = MagicMock()
                    mock_concat.return_value = mock_final_clip

                    # Mock Path.unlink to avoid file operations
                    with patch.object(Path, "unlink"):
                        clip = create_question_clip(
                            sample_question,
                            format_type="shorts",
                            language="english",
                        )

                        assert clip is not None
                        assert clip == mock_final_clip
                        mock_concat.assert_called_once()
