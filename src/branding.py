"""
Channel branding: logo generation, watermark overlay, emoji indicators.
All rendering uses Pillow and is independent of GDI / Tamil rendering.
"""

import math
import os
from pathlib import Path
from typing import Tuple
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config


# ─── Emoji font ──────────────────────────────────────────────────────────────

@lru_cache(maxsize=16)
def _get_emoji_font(size: int) -> ImageFont.FreeTypeFont:
    """Return an emoji-capable font. Falls back to default."""
    candidates = [
        "seguiemj.ttf",                                        # Windows Segoe UI Emoji
        "NotoColorEmoji.ttf",                                  # Linux / Android
        "/System/Library/Fonts/Apple Color Emoji.ttc",        # macOS
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


@lru_cache(maxsize=64)
def _get_plain_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Return a plain (non-emoji) font for labels."""
    candidates = [
        Path("fonts/Poppins/Poppins-Bold.ttf") if bold else Path("fonts/Poppins/Poppins-Medium.ttf"),
        Path("fonts/Poppins-Bold.ttf") if bold else Path("fonts/Poppins-Medium.ttf"),
        Path("fonts/NotoSansTamil/NotoSansTamil-Bold.ttf"),
    ]
    for p in candidates:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return ImageFont.load_default()


def _logo_text_parts() -> tuple[str, str]:
    """Derive two logo text lines from configured channel name."""
    raw = config.CHANNEL_NAME.replace("-", " ").replace("_", " ").strip()
    parts = [p for p in raw.split() if p]
    if not parts:
        return "K2", "Quiz"
    if len(parts) == 1:
        token = parts[0]
        return (token[:3].upper(), token[3:7] or "Quiz")
    return (parts[0][:3].upper(), parts[1][:7])


# ─── Logo generation ─────────────────────────────────────────────────────────

def generate_logo(size: int = 200) -> Image.Image:
    """
    Generate the K2_Quiz channel logo as a square RGBA image.

    Design: dark gradient background, coloured "K2" large, "Quiz" small below,
    decorative circle border and a quiz-pin emoji.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded-square background with gradient (simulate via two layers)
    bg_color1 = (15, 15, 40, 255)     # deep navy
    bg_color2 = (255, 107, 53, 255)   # K2 orange accent

    # Fill background
    draw.rounded_rectangle([0, 0, size, size], radius=size // 6, fill=bg_color1)

    # Orange accent strip at bottom
    strip_h = size // 5
    draw.rounded_rectangle(
        [0, size - strip_h, size, size],
        radius=size // 6,
        fill=bg_color2,
    )

    top_text, bottom_text = _logo_text_parts()

    # Top text
    k2_size = int(size * 0.42)
    k2_font = _get_plain_font(k2_size, bold=True)
    bbox = k2_font.getbbox(top_text)
    k2_w, k2_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    k2_x = (size - k2_w) // 2
    k2_y = int(size * 0.08)
    draw.text((k2_x, k2_y), top_text, font=k2_font, fill=(255, 255, 255, 255))

    # Bottom text
    quiz_size = int(size * 0.20)
    quiz_font = _get_plain_font(quiz_size, bold=False)
    qbbox = quiz_font.getbbox(bottom_text)
    q_w, q_h = qbbox[2] - qbbox[0], qbbox[3] - qbbox[1]
    q_x = (size - q_w) // 2
    q_y = k2_y + k2_h + int(size * 0.04)
    draw.text((q_x, q_y), bottom_text, font=quiz_font, fill=(255, 255, 255, 230))

    # Orange dot (quiz bullet) in bottom strip
    dot_r = strip_h // 4
    dot_cx = size // 2
    dot_cy = size - strip_h // 2
    draw.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=(255, 255, 255, 255),
    )

    return img


def get_logo(size: int = 140) -> Image.Image:
    """Return logo from in-memory cache, file cache, or generate it."""
    global _logo_cache
    if size in _logo_cache:
        return _logo_cache[size].copy()

    logo_path = Path(config.LOGO_PATH)
    preferred_logo_path = Path(config.CHANNEL_LOGO_PATH)
    logo_path.parent.mkdir(parents=True, exist_ok=True)

    source_path = preferred_logo_path if preferred_logo_path.exists() else logo_path
    if not source_path.exists():
        # If user has custom images in assets/, use them for branding first.
        asset_candidates = []
        for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            asset_candidates.extend(sorted(Path("assets").glob(pattern)))
        if asset_candidates:
            source_path = asset_candidates[0]
        else:
            logo = generate_logo(200)
            logo.save(str(logo_path), "PNG")
            source_path = logo_path

    logo = Image.open(str(source_path)).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
    _logo_cache[size] = logo.copy()
    return logo


# ─── Watermark ───────────────────────────────────────────────────────────────

_watermark_cache: dict = {}   # keyed by (width, height)
_logo_cache: dict = {}        # keyed by size

def _make_diagonal_watermark(width: int, height: int) -> Image.Image:
    """
    Create a transparent RGBA layer with diagonal tiled 'K2_Quiz' text.
    Opacity is set by config.WATERMARK_OPACITY.
    """
    wm = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(wm)

    # Optional channel brand image layer (faint background).
    brand_path = Path(config.CHANNEL_BRAND_IMAGE_PATH)
    if brand_path.exists():
        try:
            brand = Image.open(str(brand_path)).convert("RGBA")
            brand.thumbnail((int(width * 0.8), int(height * 0.8)), Image.Resampling.LANCZOS)
            bx = (width - brand.width) // 2
            by = (height - brand.height) // 2
            alpha = brand.split()[-1].point(lambda p: int(p * 0.12))
            brand.putalpha(alpha)
            wm.alpha_composite(brand, (bx, by))
        except Exception:
            pass

    font_size = config.WATERMARK_FONT_SIZE
    try:
        font = _get_plain_font(font_size, bold=True)
    except Exception:
        font = ImageFont.load_default()

    text = config.WATERMARK_TEXT
    try:
        bbox = font.getbbox(text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = font_size * len(text) // 2, font_size

    # Step size for tiling (with gap)
    step_x = tw + 160
    step_y = th + 100
    angle = -30  # degrees

    opacity = config.WATERMARK_OPACITY  # 0-255

    # We render into a large tile then rotate
    tile_size = max(step_x, step_y) * 3
    tile = Image.new("RGBA", (tile_size, tile_size), (0, 0, 0, 0))
    tile_draw = ImageDraw.Draw(tile)

    # Draw multiple copies in the tile
    for row in range(-1, 4):
        for col in range(-1, 4):
            x = col * step_x
            y = row * step_y
            tile_draw.text(
                (x, y),
                text,
                font=font,
                fill=(255, 255, 255, opacity),
            )

    tile_rot = tile.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)

    # Tile the rotated image across the full frame
    rx, ry = tile_rot.size
    for y in range(-ry, height, ry):
        for x in range(-rx, width, rx):
            wm.alpha_composite(tile_rot, dest=(x, y))

    return wm


def _get_cached_watermark(width: int, height: int) -> Image.Image:
    """Return pre-built watermark layer, cached by frame size."""
    global _watermark_cache
    key = (width, height)
    if key not in _watermark_cache:
        _watermark_cache[key] = _make_diagonal_watermark(width, height)
    return _watermark_cache[key]


def _get_cached_logo_overlay(width: int, height: int) -> tuple:
    """Return (logo_image, lx, ly) for corner placement, cached by frame size."""
    logo_size = max(80, min(width, height) // 10)
    logo = get_logo(logo_size)  # already in-memory cached

    # Pre-apply opacity once
    cache_key = (width, height, "logo_overlay")
    if cache_key not in _watermark_cache:
        corner_opacity = config.WATERMARK_CORNER_OPACITY
        r, g, b, a = logo.split()
        a = a.point(lambda p: int(p * corner_opacity / 255))
        logo_ready = logo.copy()
        logo_ready.putalpha(a)
        margin = 20
        lx = width - logo_size - margin
        ly = height - logo_size - margin
        _watermark_cache[cache_key] = (logo_ready, lx, ly)

    return _watermark_cache[cache_key]


def apply_watermark(frame: Image.Image) -> Image.Image:
    """
    Apply two branding layers to a frame:
      1. Diagonal semi-transparent 'K2_Quiz' text tile (background watermark)
      2. Channel logo in the bottom-right corner

    Both layers are cached — only computed once per unique frame size.
    Works with both Shorts (1080×1920) and Full (1920×1080) frames.
    Returns a new RGB image.
    """
    frame_rgba = frame.convert("RGBA")
    width, height = frame_rgba.size

    # ── Layer 1: diagonal text watermark (cached) ────────────────────────────
    wm_layer = _get_cached_watermark(width, height)
    frame_rgba = Image.alpha_composite(frame_rgba, wm_layer)

    # ── Layer 2: logo corner (cached) ────────────────────────────────────────
    logo_overlay, lx, ly = _get_cached_logo_overlay(width, height)
    frame_rgba.alpha_composite(logo_overlay, dest=(lx, ly))

    return frame_rgba.convert("RGB")


# ─── Emoji indicators ────────────────────────────────────────────────────────

def draw_emoji(
    frame: Image.Image,
    emoji_char: str,
    x: int,
    y: int,
    size: int = 50,
    color: Tuple[int, int, int] = (255, 255, 255),
) -> Tuple[int, int]:
    """
    Draw an emoji character using the system emoji font.
    Falls back to a colored circle if emoji font unavailable.
    Returns (width, height) of rendered glyph.
    """
    try:
        font = _get_emoji_font(size)
        draw = ImageDraw.Draw(frame)
        draw.text((x, y), emoji_char, font=font, embedded_color=True)
        bbox = font.getbbox(emoji_char)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        # Fallback: colored dot
        r = size // 3
        draw = ImageDraw.Draw(frame)
        draw.ellipse([x, y, x + r * 2, y + r * 2], fill=color)
        return r * 2, r * 2


def draw_correct_badge(
    frame: Image.Image,
    cx: int,
    cy: int,
    radius: int = 28,
    color: Tuple[int, int, int] = (0, 255, 136),
) -> None:
    """
    Draw a green circle with a ✓ checkmark — used to mark the correct option.
    This is purely Pillow-drawn (no emoji font needed).
    """
    draw = ImageDraw.Draw(frame)

    # Filled circle
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(*color, 255) if frame.mode == "RGBA" else color,
    )

    # Draw ✓ as two lines
    lw = max(3, radius // 6)
    # first stroke: short descending
    draw.line(
        [cx - radius // 2, cy, cx - radius // 8, cy + radius // 2],
        fill=(0, 0, 0),
        width=lw,
    )
    # second stroke: long ascending
    draw.line(
        [cx - radius // 8, cy + radius // 2, cx + radius // 2, cy - radius // 2],
        fill=(0, 0, 0),
        width=lw,
    )


def draw_question_badge(
    frame: Image.Image,
    cx: int,
    cy: int,
    radius: int = 30,
) -> None:
    """
    Draw an orange circle with a '?' — used as the question indicator.
    """
    draw = ImageDraw.Draw(frame)
    orange = (255, 107, 53)

    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=orange,
    )

    q_font = _get_plain_font(int(radius * 1.2), bold=True)
    bbox = q_font.getbbox("?")
    qw, qh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (cx - qw // 2, cy - qh // 2),
        "?",
        font=q_font,
        fill=(255, 255, 255),
    )


def draw_engagement_icons(
    frame: Image.Image,
    icons: list,        # list of (emoji_str, label_str, color_rgb)
    start_x: int,
    start_y: int,
    spacing: int = 200,
    icon_size: int = 60,
) -> None:
    """
    Draw a row of emoji + label pairs for the engagement screen.
    Labels are rendered via GDI (if available) for Tamil support.
    """
    label_size = max(24, icon_size // 3)

    # Import GDI renderer lazily to avoid circular imports
    _gdi = None
    _gdi_font = "Noto Sans Tamil"
    try:
        import sys
        if sys.platform == "win32":
            from src import gdi_text as _gdi  # noqa: F401
    except Exception:
        _gdi = None

    label_font = _get_plain_font(label_size, bold=True)

    for i, (emoji_char, label, color) in enumerate(icons):
        x = start_x + i * spacing
        # Emoji
        draw_emoji(frame, emoji_char, x, start_y, size=icon_size, color=color)

        # Label text below — prefer GDI for Tamil
        label_y = start_y + icon_size + 8
        if _gdi is not None and _gdi.IS_WINDOWS:
            w, _ = _gdi.measure_text(label, _gdi_font, label_size, spacing)
            lx = x + icon_size // 2 - w // 2
            _gdi.draw_text(frame, lx, label_y, label, _gdi_font, label_size, color, spacing, bold=True)
        else:
            draw = ImageDraw.Draw(frame)
            try:
                bbox = label_font.getbbox(label)
                lw = bbox[2] - bbox[0]
                draw.text(
                    (x + icon_size // 2 - lw // 2, label_y),
                    label,
                    font=label_font,
                    fill=color,
                )
            except Exception:
                pass
