"""Tests for text renderer."""

import pytest
from PIL import Image

from src.text_renderer import (
    create_background,
    render_question_frame,
    render_options,
    hex_to_rgb,
)
import config


def test_hex_to_rgb():
    """Test hex color conversion."""
    assert hex_to_rgb("#ffffff") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("#00ff88") == (0, 255, 136)


def test_create_background_shorts():
    """Test background creation for shorts."""
    bg = create_background("shorts")
    assert bg.size == (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)
    assert bg.mode == "RGB"


def test_create_background_full():
    """Test background creation for full video."""
    bg = create_background("full")
    assert bg.size == (config.FULL_WIDTH, config.FULL_HEIGHT)


def test_render_question_frame_shorts():
    """Test rendering a complete question frame for shorts."""
    frame = render_question_frame(
        question="What is the capital of India?",
        options=["Mumbai", "Delhi", "Chennai", "Kolkata"],
        format_type="shorts",
        highlight_correct=None,
        timer_value=5,
    )

    assert frame.size == (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)


def test_render_question_frame_with_highlight():
    """Test rendering with correct answer highlighted."""
    frame = render_question_frame(
        question="What is 2+2?",
        options=["3", "4", "5", "6"],
        format_type="shorts",
        highlight_correct=1,  # Option B (index 1)
        timer_value=0,
    )

    assert frame.size == (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)
