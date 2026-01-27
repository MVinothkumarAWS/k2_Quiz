"""Text and frame rendering using Pillow."""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get font with fallback to default."""
    font_paths = [
        Path("fonts/Poppins/Poppins-Bold.ttf") if bold else Path("fonts/Poppins/Poppins-Medium.ttf"),
        Path("fonts/Poppins-Bold.ttf") if bold else Path("fonts/Poppins-Medium.ttf"),
    ]

    for font_path in font_paths:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)

    # Fallback to default
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def create_background(format_type: str) -> Image.Image:
    """Create background image for the given format."""
    if format_type == "shorts":
        size = (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)
    else:
        size = (config.FULL_WIDTH, config.FULL_HEIGHT)

    bg_color = hex_to_rgb(config.COLORS["background"])
    return Image.new("RGB", size, bg_color)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def render_question_frame(
    question: str,
    options: list[str],
    format_type: str,
    highlight_correct: Optional[int] = None,
    timer_value: Optional[int] = None,
    show_image: Optional[Image.Image] = None,
    question_num: Optional[int] = None,
    total_questions: Optional[int] = None,
    score: Optional[int] = None,
) -> Image.Image:
    """
    Render a complete question frame.

    Args:
        question: Question text
        options: List of 4 options
        format_type: "shorts" or "full"
        highlight_correct: Index of correct answer to highlight (0-3)
        timer_value: Timer value to display (None to hide)
        show_image: Image to display (full format only)
        question_num: Current question number (full format only)
        total_questions: Total questions (full format only)
        score: Current score (full format only)

    Returns:
        Rendered PIL Image
    """
    frame = create_background(format_type)
    draw = ImageDraw.Draw(frame)

    if format_type == "shorts":
        frame = _render_shorts_frame(
            frame, draw, question, options, highlight_correct, timer_value
        )
    else:
        frame = _render_full_frame(
            frame, draw, question, options, highlight_correct, timer_value,
            show_image, question_num, total_questions, score
        )

    return frame


def _render_shorts_frame(
    frame: Image.Image,
    draw: ImageDraw.Draw,
    question: str,
    options: list[str],
    highlight_correct: Optional[int],
    timer_value: Optional[int],
) -> Image.Image:
    """Render shorts format frame."""
    width, height = frame.size
    padding = 60

    # Colors
    text_color = hex_to_rgb(config.COLORS["text"])
    option_bg = hex_to_rgb(config.COLORS["option_box"])
    timer_color = hex_to_rgb(config.COLORS["timer"])
    correct_color = hex_to_rgb(config.COLORS["correct"])

    # Fonts
    question_font = get_font(config.FONT_QUESTION_SIZE, bold=True)
    option_font = get_font(config.FONT_OPTION_SIZE)
    timer_font = get_font(config.FONT_TIMER_SIZE, bold=True)

    # Question area
    max_text_width = width - (padding * 2)
    question_lines = wrap_text(question, question_font, max_text_width)

    y = 200
    for line in question_lines:
        bbox = question_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, font=question_font, fill=text_color)
        y += bbox[3] - bbox[1] + 20

    # Options
    option_labels = ["A", "B", "C", "D"]
    option_height = 90
    option_spacing = 20
    options_start_y = y + 80

    for i, (label, option_text) in enumerate(zip(option_labels, options)):
        opt_y = options_start_y + (i * (option_height + option_spacing))

        # Determine colors
        if highlight_correct is not None and i == highlight_correct:
            # Highlighted correct answer
            box_color = correct_color
            # Add glow effect
            glow_frame = _add_glow(frame, padding, opt_y, width - padding, opt_y + option_height, correct_color)
            frame = glow_frame
            draw = ImageDraw.Draw(frame)
        else:
            box_color = option_bg

        # Draw option box
        draw.rounded_rectangle(
            [padding, opt_y, width - padding, opt_y + option_height],
            radius=15,
            fill=box_color
        )

        # Draw option text
        option_display = f"{label}) {option_text}"
        bbox = option_font.getbbox(option_display)
        text_x = padding + 30
        text_y = opt_y + (option_height - (bbox[3] - bbox[1])) // 2
        draw.text((text_x, text_y), option_display, font=option_font, fill=text_color)

    # Timer
    if timer_value is not None:
        timer_y = options_start_y + (4 * (option_height + option_spacing)) + 60
        timer_text = f"⏱ {timer_value}"
        bbox = timer_font.getbbox(timer_text)
        timer_x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((timer_x, timer_y), timer_text, font=timer_font, fill=timer_color)

    return frame


def _render_full_frame(
    frame: Image.Image,
    draw: ImageDraw.Draw,
    question: str,
    options: list[str],
    highlight_correct: Optional[int],
    timer_value: Optional[int],
    show_image: Optional[Image.Image],
    question_num: Optional[int],
    total_questions: Optional[int],
    score: Optional[int],
) -> Image.Image:
    """Render full video format frame."""
    width, height = frame.size
    padding = 80

    # Colors
    text_color = hex_to_rgb(config.COLORS["text"])
    option_bg = hex_to_rgb(config.COLORS["option_box"])
    timer_color = hex_to_rgb(config.COLORS["timer"])
    correct_color = hex_to_rgb(config.COLORS["correct"])

    # Fonts
    question_font = get_font(config.FONT_QUESTION_SIZE, bold=True)
    option_font = get_font(config.FONT_OPTION_SIZE)
    timer_font = get_font(config.FONT_TIMER_SIZE, bold=True)
    info_font = get_font(36)

    # Layout: Left side for question/options, right side for image
    left_width = int(width * 0.55)
    right_start = left_width + 40

    # Question at top
    max_text_width = left_width - padding
    question_lines = wrap_text(question, question_font, max_text_width)

    y = 100
    for line in question_lines:
        draw.text((padding, y), line, font=question_font, fill=text_color)
        bbox = question_font.getbbox(line)
        y += bbox[3] - bbox[1] + 15

    # Options on left
    option_labels = ["A", "B", "C", "D"]
    option_height = 80
    option_spacing = 15
    options_start_y = y + 50

    for i, (label, option_text) in enumerate(zip(option_labels, options)):
        opt_y = options_start_y + (i * (option_height + option_spacing))

        if highlight_correct is not None and i == highlight_correct:
            box_color = correct_color
            frame = _add_glow(frame, padding, opt_y, left_width, opt_y + option_height, correct_color)
            draw = ImageDraw.Draw(frame)
        else:
            box_color = option_bg

        draw.rounded_rectangle(
            [padding, opt_y, left_width, opt_y + option_height],
            radius=12,
            fill=box_color
        )

        option_display = f"{label}) {option_text}"
        bbox = option_font.getbbox(option_display)
        text_x = padding + 25
        text_y = opt_y + (option_height - (bbox[3] - bbox[1])) // 2
        draw.text((text_x, text_y), option_display, font=option_font, fill=text_color)

    # Image area on right (if provided)
    if show_image is not None:
        img_area_width = width - right_start - padding
        img_area_height = 450
        img_y = 150

        # Resize image to fit
        show_image.thumbnail((img_area_width, img_area_height), Image.Resampling.LANCZOS)
        img_x = right_start + (img_area_width - show_image.width) // 2
        img_y = img_y + (img_area_height - show_image.height) // 2

        frame.paste(show_image, (img_x, img_y))
        draw = ImageDraw.Draw(frame)

    # Bottom bar: question counter, timer, score
    bottom_y = height - 100

    # Question counter
    if question_num is not None and total_questions is not None:
        counter_text = f"Q: {question_num}/{total_questions}"
        draw.text((padding, bottom_y), counter_text, font=info_font, fill=text_color)

    # Timer (center)
    if timer_value is not None:
        timer_text = f"⏱ {timer_value}"
        bbox = timer_font.getbbox(timer_text)
        timer_x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((timer_x, bottom_y - 20), timer_text, font=timer_font, fill=timer_color)

    # Score (right)
    if score is not None:
        score_text = f"Score: {score} ✓"
        bbox = info_font.getbbox(score_text)
        score_x = width - padding - (bbox[2] - bbox[0])
        draw.text((score_x, bottom_y), score_text, font=info_font, fill=correct_color)

    return frame


def _add_glow(
    frame: Image.Image,
    x1: int, y1: int, x2: int, y2: int,
    color: Tuple[int, int, int],
) -> Image.Image:
    """Add glow effect around a rectangle."""
    # Create glow layer
    glow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Draw multiple expanding rectangles with decreasing opacity
    for i in range(3, 0, -1):
        expand = i * 8
        opacity = int(100 / i)
        glow_color = (*color, opacity)
        glow_draw.rounded_rectangle(
            [x1 - expand, y1 - expand, x2 + expand, y2 + expand],
            radius=15 + expand,
            fill=glow_color
        )

    # Apply blur
    glow = glow.filter(ImageFilter.GaussianBlur(radius=10))

    # Composite
    frame = frame.convert("RGBA")
    frame = Image.alpha_composite(frame, glow)

    return frame.convert("RGB")


def render_options(
    options: list[str],
    width: int,
    highlight_index: Optional[int] = None
) -> Image.Image:
    """Render options as a standalone image strip."""
    option_height = 80
    spacing = 15
    total_height = (option_height * 4) + (spacing * 3)

    img = Image.new("RGBA", (width, total_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    option_font = get_font(config.FONT_OPTION_SIZE)
    option_bg = hex_to_rgb(config.COLORS["option_box"])
    text_color = hex_to_rgb(config.COLORS["text"])
    correct_color = hex_to_rgb(config.COLORS["correct"])

    labels = ["A", "B", "C", "D"]

    for i, (label, text) in enumerate(zip(labels, options)):
        y = i * (option_height + spacing)

        color = correct_color if highlight_index == i else option_bg

        draw.rounded_rectangle(
            [0, y, width, y + option_height],
            radius=12,
            fill=color
        )

        display = f"{label}) {text}"
        draw.text((25, y + 20), display, font=option_font, fill=text_color)

    return img
