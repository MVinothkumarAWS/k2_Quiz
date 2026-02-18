"""
Windows GDI text renderer for complex scripts (Tamil, etc.)
Uses Uniscribe for correct virama/pulli marks and vowel sign rendering.
"""

import ctypes
import os
import sys
from typing import Tuple
from PIL import Image

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    gdi32 = ctypes.windll.gdi32
    user32 = ctypes.windll.user32
else:
    gdi32 = None
    user32 = None

_loaded_fonts: dict = {}
FR_PRIVATE = 0x10


class _LOGFONTW(ctypes.Structure):
    _fields_ = [
        ("lfHeight", ctypes.c_long), ("lfWidth", ctypes.c_long),
        ("lfEscapement", ctypes.c_long), ("lfOrientation", ctypes.c_long),
        ("lfWeight", ctypes.c_long), ("lfItalic", ctypes.c_byte),
        ("lfUnderline", ctypes.c_byte), ("lfStrikeOut", ctypes.c_byte),
        ("lfCharSet", ctypes.c_byte), ("lfOutPrecision", ctypes.c_byte),
        ("lfClipPrecision", ctypes.c_byte), ("lfQuality", ctypes.c_byte),
        ("lfPitchAndFamily", ctypes.c_byte), ("lfFaceName", ctypes.c_wchar * 32),
    ]


class _RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long), ("top", ctypes.c_long),
        ("right", ctypes.c_long), ("bottom", ctypes.c_long),
    ]


class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32), ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32), ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]


class _BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", _BITMAPINFOHEADER), ("bmiColors", ctypes.c_uint32 * 3)]


DT_WORDBREAK = 0x10
DT_CALCRECT = 0x400
DT_NOPREFIX = 0x800
DT_CENTER = 0x01
DT_SINGLELINE = 0x20
TRANSPARENT = 1
CLEARTYPE_QUALITY = 5
FW_NORMAL = 400
FW_BOLD = 700


def load_font(font_path: str) -> bool:
    """Temporarily load a TTF font file into Windows GDI."""
    if not IS_WINDOWS:
        return False
    abs_path = os.path.abspath(font_path)
    if abs_path not in _loaded_fonts:
        result = gdi32.AddFontResourceExW(abs_path, FR_PRIVATE, 0)
        _loaded_fonts[abs_path] = result > 0
    return _loaded_fonts.get(abs_path, False)


def _render_to_pil(
    text: str,
    font_name: str,
    font_size: int,
    max_width: int,
    bold: bool = False,
) -> Tuple[Image.Image, int, int]:
    """Render text as white-on-black using GDI. Returns (image, width, height)."""
    max_height = font_size * 15

    hdc_screen = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_screen, max_width, max_height)
    gdi32.SelectObject(hdc_mem, hbmp)

    # Black background
    hbrush = gdi32.CreateSolidBrush(0x000000)
    rc_fill = _RECT(0, 0, max_width, max_height)
    user32.FillRect(hdc_mem, ctypes.byref(rc_fill), hbrush)
    gdi32.DeleteObject(hbrush)

    # Create font
    lf = _LOGFONTW()
    lf.lfHeight = -font_size
    lf.lfWeight = FW_BOLD if bold else FW_NORMAL
    lf.lfQuality = CLEARTYPE_QUALITY
    lf.lfCharSet = 0  # DEFAULT_CHARSET
    lf.lfFaceName = font_name
    hfont = gdi32.CreateFontIndirectW(ctypes.byref(lf))
    old_font = gdi32.SelectObject(hdc_mem, hfont)

    gdi32.SetTextColor(hdc_mem, 0xFFFFFF)  # white text
    gdi32.SetBkMode(hdc_mem, TRANSPARENT)

    # Measure text
    rc_measure = _RECT(0, 0, max_width, max_height)
    user32.DrawTextW(
        hdc_mem, text, len(text), ctypes.byref(rc_measure),
        DT_WORDBREAK | DT_CALCRECT | DT_NOPREFIX,
    )
    actual_w = rc_measure.right
    actual_h = rc_measure.bottom

    # Draw text
    rc_draw = _RECT(0, 0, max_width, max_height)
    user32.DrawTextW(
        hdc_mem, text, len(text), ctypes.byref(rc_draw),
        DT_WORDBREAK | DT_NOPREFIX,
    )

    # Read bitmap
    bmi = _BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(_BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = max_width
    bmi.bmiHeader.biHeight = -max_height  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0

    buf = (ctypes.c_byte * (max_width * max_height * 4))()
    gdi32.GetDIBits(hdc_mem, hbmp, 0, max_height, buf, ctypes.byref(bmi), 0)

    img = Image.frombuffer(
        "RGBA", (max_width, max_height), bytes(buf), "raw", "BGRA", 0, 1
    ).convert("RGB")

    # Cleanup
    gdi32.SelectObject(hdc_mem, old_font)
    gdi32.DeleteObject(hfont)
    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc_screen)

    # Crop to actual text size
    img = img.crop((0, 0, max(actual_w, 1), max(actual_h, 1)))
    return img, actual_w, actual_h


def draw_text(
    frame: Image.Image,
    x: int,
    y: int,
    text: str,
    font_name: str,
    font_size: int,
    text_color: Tuple[int, int, int],
    max_width: int,
    bold: bool = False,
) -> Tuple[int, int]:
    """
    Render Tamil/Unicode text using Windows GDI and composite it onto frame.
    Returns (text_width, text_height).
    """
    if not IS_WINDOWS or not text.strip():
        return 0, 0

    text_img, tw, th = _render_to_pil(text, font_name, font_size, max_width, bold)

    if tw == 0 or th == 0:
        return 0, 0

    # Convert white-on-black → text_color with alpha
    r, g, b = text_color
    pixels = list(text_img.getdata())
    colored = [(r, g, b, px[0]) for px in pixels]  # brightness → alpha

    text_rgba = Image.new("RGBA", text_img.size)
    text_rgba.putdata(colored)

    # Paste onto frame using alpha mask
    frame_rgba = frame.convert("RGBA")
    dest_x = max(0, x)
    dest_y = max(0, y)

    # Clip to frame bounds
    fw, fh = frame_rgba.size
    clip_w = min(text_rgba.width, fw - dest_x)
    clip_h = min(text_rgba.height, fh - dest_y)
    if clip_w <= 0 or clip_h <= 0:
        return tw, th

    text_clipped = text_rgba.crop((0, 0, clip_w, clip_h))
    frame_rgba.alpha_composite(text_clipped, dest=(dest_x, dest_y))

    result = frame_rgba.convert("RGB")
    frame.paste(result)
    return tw, th


def measure_text(
    text: str,
    font_name: str,
    font_size: int,
    max_width: int,
    bold: bool = False,
) -> Tuple[int, int]:
    """Measure text width and height using GDI. Returns (width, height)."""
    if not IS_WINDOWS or not text.strip():
        return 0, font_size

    max_height = font_size * 15
    hdc_screen = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)

    lf = _LOGFONTW()
    lf.lfHeight = -font_size
    lf.lfWeight = FW_BOLD if bold else FW_NORMAL
    lf.lfQuality = CLEARTYPE_QUALITY
    lf.lfCharSet = 0
    lf.lfFaceName = font_name
    hfont = gdi32.CreateFontIndirectW(ctypes.byref(lf))
    old_font = gdi32.SelectObject(hdc_mem, hfont)

    rc = _RECT(0, 0, max_width, max_height)
    user32.DrawTextW(
        hdc_mem, text, len(text), ctypes.byref(rc),
        DT_WORDBREAK | DT_CALCRECT | DT_NOPREFIX,
    )

    gdi32.SelectObject(hdc_mem, old_font)
    gdi32.DeleteObject(hfont)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc_screen)

    return rc.right, rc.bottom
