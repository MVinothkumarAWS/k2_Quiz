"""Text and frame rendering using Pillow + Windows GDI for complex scripts."""

import sys
from pathlib import Path
from typing import Optional, Tuple
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config
from src.branding import (
    apply_watermark,
    draw_correct_badge,
    draw_question_badge,
    draw_engagement_icons,
    draw_emoji,
)

# Load Windows GDI renderer for proper Tamil script shaping (Uniscribe)
_GDI_AVAILABLE = False
_GDI_FONT_REGULAR = "Noto Sans Tamil"
_GDI_FONT_BOLD = "Noto Sans Tamil"

if sys.platform == "win32":
    try:
        from src import gdi_text as _gdi
        # Pre-load fonts into Windows
        _gdi.load_font("fonts/NotoSansTamil/NotoSansTamil-Regular.ttf")
        _gdi.load_font("fonts/NotoSansTamil/NotoSansTamil-Bold.ttf")
        _GDI_AVAILABLE = True
    except Exception:
        _GDI_AVAILABLE = False


def _draw_text(
    frame: Image.Image,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    font_size: int,
    color: Tuple[int, int, int],
    max_width: int = 2000,
    bold: bool = False,
) -> Tuple[int, int]:
    """Draw text using GDI (Windows) or Pillow fallback. Returns (w, h)."""
    if _GDI_AVAILABLE:
        font_name = _GDI_FONT_BOLD if bold else _GDI_FONT_REGULAR
        return _gdi.draw_text(frame, x, y, text, font_name, font_size, color, max_width, bold)
    else:
        draw = ImageDraw.Draw(frame)
        draw.text((x, y), text, font=font, fill=color)
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _measure_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    font_size: int,
    max_width: int = 2000,
    bold: bool = False,
) -> Tuple[int, int]:
    """Measure text dimensions using GDI (Windows) or Pillow fallback. Returns (w, h)."""
    if _GDI_AVAILABLE:
        font_name = _GDI_FONT_BOLD if bold else _GDI_FONT_REGULAR
        return _gdi.measure_text(text, font_name, font_size, max_width, bold)
    else:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


@lru_cache(maxsize=64)
def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get font with fallback to default."""
    font_paths = [
        # Try bundled Tamil font first (supports Tamil Unicode)
        Path("fonts/NotoSansTamil/NotoSansTamil-Bold.ttf") if bold else Path("fonts/NotoSansTamil/NotoSansTamil-Regular.ttf"),
        # Fallback to Poppins
        Path("fonts/Poppins/Poppins-Bold.ttf") if bold else Path("fonts/Poppins/Poppins-Medium.ttf"),
        Path("fonts/Poppins-Bold.ttf") if bold else Path("fonts/Poppins-Medium.ttf"),
        # Linux system Noto Sans Tamil (installed via apt fonts-noto)
        Path("/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf") if bold else Path("/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansTamil-Bold.ttf") if bold else Path("/usr/share/fonts/opentype/noto/NotoSansTamil-Regular.ttf"),
        # Linux DejaVu fallback
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if bold else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]

    for font_path in font_paths:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size, layout_engine=ImageFont.Layout.RAQM)
            except Exception:
                return ImageFont.truetype(str(font_path), size)

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
            frame, draw, question, options, highlight_correct, timer_value, show_image,
            question_num=question_num,
        )
    else:
        frame = _render_full_frame(
            frame, draw, question, options, highlight_correct, timer_value,
            show_image, question_num, total_questions, score
        )

    # Apply channel watermark + logo on every frame
    frame = apply_watermark(frame)

    return frame


def _render_shorts_frame(
    frame: Image.Image,
    draw: ImageDraw.Draw,
    question: str,
    options: list[str],
    highlight_correct: Optional[int],
    timer_value: Optional[int],
    show_image: Optional[Image.Image] = None,
    question_num: Optional[int] = None,
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

    # Question area — use GDI for correct Tamil rendering
    badge_r = 18       # question badge radius (scaled for 720p)
    badge_margin = badge_r * 2 + 12
    max_text_width = width - (padding * 2) - badge_margin
    q_size = config.FONT_QUESTION_SIZE

    # Measure total question block height to center it
    q_w, q_h = _measure_text(question, question_font, q_size, max_text_width, bold=True)
    option_height = 64
    option_spacing = 14
    options_total_h = 4 * (option_height + option_spacing)
    gap = 60
    content_h = q_h + gap + options_total_h
    y = max(100, (height - content_h) // 3)  # upper-third centering

    # Draw question badge (orange circle with number) at left edge
    draw_question_badge(frame, padding + badge_r, y + badge_r, radius=badge_r,
                        number=question_num)
    draw = ImageDraw.Draw(frame)

    # Draw question text (GDI handles word-wrapping internally)
    _draw_text(frame, padding + badge_margin, y, question, question_font, q_size,
               text_color, max_text_width, bold=True)
    y += q_h + gap

    # Options
    option_labels = ["A", "B", "C", "D"]
    options_start_y = y
    draw = ImageDraw.Draw(frame)  # refresh draw after GDI modifications

    for i, (label, option_text) in enumerate(zip(option_labels, options)):
        opt_y = options_start_y + (i * (option_height + option_spacing))

        # Determine colors
        if highlight_correct is not None and i == highlight_correct:
            box_color = correct_color
            glow_frame = _add_glow(frame, padding, opt_y, width - padding, opt_y + option_height, correct_color)
            frame = glow_frame
            draw = ImageDraw.Draw(frame)
        else:
            box_color = option_bg

        # Draw option box
        draw.rounded_rectangle(
            [padding, opt_y, width - padding, opt_y + option_height],
            radius=15,
            fill=box_color,
        )

        # Draw option text using GDI
        option_display = f"{label}) {option_text}"
        opt_size = config.FONT_OPTION_SIZE
        _, opt_th = _measure_text(option_display, option_font, opt_size, max_text_width - 80)
        text_x = padding + 30
        text_y = opt_y + (option_height - opt_th) // 2
        opt_text_color = (0, 0, 0) if (highlight_correct is not None and i == highlight_correct) else text_color
        _draw_text(frame, text_x, text_y, option_display, option_font, opt_size,
                   opt_text_color, width - padding - text_x - 80)
        draw = ImageDraw.Draw(frame)  # refresh after GDI

        # ✓ badge on correct option (right side of box)
        if highlight_correct is not None and i == highlight_correct:
            badge_cx = width - padding - 24
            badge_cy = opt_y + option_height // 2
            draw_correct_badge(frame, badge_cx, badge_cy, radius=18,
                               color=hex_to_rgb(config.COLORS["background"]))
            draw = ImageDraw.Draw(frame)

    # Timer — clock emoji + number, centered together
    if timer_value is not None:
        from src.branding import draw_emoji as _draw_emoji
        timer_y = height - 160
        timer_text = str(timer_value)
        emoji_char = "⏱"
        emoji_size = config.FONT_TIMER_SIZE

        # Measure number
        num_bbox = timer_font.getbbox(timer_text)
        num_w = num_bbox[2] - num_bbox[0]
        num_h = num_bbox[3] - num_bbox[1]

        # Emoji is roughly square at emoji_size
        gap = 12
        total_w = emoji_size + gap + num_w
        badge_pad = 18

        start_x = (width - total_w) // 2

        # Draw dark background badge behind both
        draw.rounded_rectangle(
            [
                start_x - badge_pad,
                timer_y - badge_pad,
                start_x + total_w + badge_pad,
                timer_y + max(emoji_size, num_h) + badge_pad,
            ],
            radius=20,
            fill=(0, 0, 0),
        )

        # Draw clock emoji
        _draw_emoji(frame, emoji_char, start_x, timer_y, size=emoji_size, color=timer_color)
        draw = ImageDraw.Draw(frame)  # refresh after emoji draw

        # Draw number to the right of emoji
        num_x = start_x + emoji_size + gap
        num_y = timer_y + (emoji_size - num_h) // 2
        draw.text((num_x, num_y), timer_text, font=timer_font, fill=timer_color)

    # Image at bottom (during reveal phase)
    if show_image is not None:
        img_area_height = 350
        img_y = height - img_area_height - padding

        # Resize image to fit
        show_image = show_image.copy()
        show_image.thumbnail((width - (padding * 2), img_area_height), Image.Resampling.LANCZOS)
        img_x = (width - show_image.width) // 2

        frame.paste(show_image, (img_x, img_y))
        draw = ImageDraw.Draw(frame)

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

    # Question at top — use GDI for correct Tamil rendering
    badge_r = 24
    badge_margin = badge_r * 2 + 16
    max_text_width = left_width - padding - badge_margin
    q_size = config.FONT_QUESTION_SIZE

    y = 100
    draw_question_badge(frame, padding + badge_r, y + badge_r, radius=badge_r, number=question_num)
    _draw_text(frame, padding + badge_margin, y, question, question_font, q_size,
               text_color, max_text_width, bold=True)
    _, q_h = _measure_text(question, question_font, q_size, max_text_width, bold=True)
    y += q_h + 15
    draw = ImageDraw.Draw(frame)

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
            fill=box_color,
        )

        option_display = f"{label}) {option_text}"
        opt_size = config.FONT_OPTION_SIZE
        _, opt_th = _measure_text(option_display, option_font, opt_size, left_width - padding - 70)
        text_x = padding + 25
        text_y = opt_y + (option_height - opt_th) // 2
        opt_text_color = (0, 0, 0) if (highlight_correct is not None and i == highlight_correct) else text_color
        _draw_text(frame, text_x, text_y, option_display, option_font, opt_size,
                   opt_text_color, left_width - text_x - 70)
        draw = ImageDraw.Draw(frame)

        # ✓ badge on correct option
        if highlight_correct is not None and i == highlight_correct:
            badge_cx = left_width - 35
            badge_cy = opt_y + option_height // 2
            draw_correct_badge(frame, badge_cx, badge_cy, radius=24,
                               color=hex_to_rgb(config.COLORS["background"]))
            draw = ImageDraw.Draw(frame)

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


def render_engagement_frame(format_type: str, language: str = "tamil") -> Image.Image:
    """
    Render the Tamil engagement screen (Like, Comment, Subscribe).

    Args:
        format_type: "shorts" or "full"
        language: Unused, kept for API compatibility (always Tamil)

    Returns:
        Rendered PIL Image
    """
    frame = create_background(format_type)
    draw = ImageDraw.Draw(frame)
    width, height = frame.size

    # Colors
    text_color = hex_to_rgb(config.COLORS["text"])
    accent_color = hex_to_rgb(config.COLORS["correct"])
    timer_color = hex_to_rgb(config.COLORS["timer"])

    # Fonts
    action_font = get_font(55, bold=True)
    channel_font = get_font(80, bold=True)
    sub_font = get_font(40)

    # Tamil engagement text
    like_text    = "லைக்"
    comment_text = "கமெண்ட்"
    share_text   = "ஷேர்"
    sub_text     = "சப்ஸ்கிரைப்"
    sub_to_text  = "சப்ஸ்கிரைப் செய்யுங்கள்"
    cta_text     = "சரியான பதில் கிடைத்ததா?"
    cta_text2    = "கீழே கமெண்ட் செய்யுங்கள்!"
    score_text   = "உங்கள் ஸ்கோரை கமெண்டில் எழுதுங்கள்!"

    # Center Y calculation
    center_y = height // 2

    if format_type == "shorts":
        # Shorts layout (vertical)
        y_offset = center_y - 300

        # Emoji icon row: 👍 💬 📢 🔔
        icon_size = 70
        icons_data = [
            ("👍", like_text,    accent_color),
            ("💬", comment_text, timer_color),
            ("📢", share_text,   accent_color),
            ("🔔", sub_text,     timer_color),
        ]
        row_w = len(icons_data) * 160
        icons_x = (width - row_w) // 2
        draw_engagement_icons(frame, icons_data, icons_x, y_offset,
                              spacing=160, icon_size=icon_size)
        draw = ImageDraw.Draw(frame)
        y_offset += icon_size + 70

        # Channel name (ASCII — Pillow)
        bbox = channel_font.getbbox(config.CHANNEL_NAME)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_offset), config.CHANNEL_NAME, font=channel_font, fill=text_color)
        y_offset += 140

        # CTA lines using GDI (supports Tamil)
        for eng_text, color in [(cta_text, accent_color), (cta_text2, text_color)]:
            tw, _ = _measure_text(eng_text, sub_font, 40, width)
            x = (width - tw) // 2
            _draw_text(frame, x, y_offset, eng_text, sub_font, 40, color, width)
            draw = ImageDraw.Draw(frame)
            y_offset += 70

    else:
        # Full format layout (horizontal)
        y_offset = center_y - 240

        # Emoji icon row for Full (wider spacing)
        icon_size = 70
        icons_data = [
            ("👍", like_text,    accent_color),
            ("💬", comment_text, timer_color),
            ("📢", share_text,   accent_color),
            ("🔔", sub_text,     timer_color),
        ]
        row_w = len(icons_data) * 220
        icons_x = (width - row_w) // 2
        draw_engagement_icons(frame, icons_data, icons_x, y_offset,
                              spacing=220, icon_size=icon_size)
        draw = ImageDraw.Draw(frame)
        y_offset += icon_size + 80

        # Subscribe CTA
        tw, _ = _measure_text(sub_to_text, action_font, 55, width, bold=True)
        x = (width - tw) // 2
        _draw_text(frame, x, y_offset, sub_to_text, action_font, 55, timer_color, width, bold=True)
        draw = ImageDraw.Draw(frame)
        y_offset += 100

        # Channel name (ASCII — Pillow)
        bbox = channel_font.getbbox(config.CHANNEL_NAME)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_offset), config.CHANNEL_NAME, font=channel_font, fill=text_color)
        y_offset += 140

        # Score prompt (GDI for Tamil) — clamp to keep within frame
        bottom_margin = 60
        y_offset = min(y_offset, height - bottom_margin - 40)
        tw, _ = _measure_text(score_text, sub_font, 40, width)
        x = (width - tw) // 2
        _draw_text(frame, x, y_offset, score_text, sub_font, 40, text_color, width)
        draw = ImageDraw.Draw(frame)

    # Apply watermark + logo on engagement frame
    frame = apply_watermark(frame)

    return frame


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
