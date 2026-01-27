"""Image fetcher using Pixabay API."""

import re
import requests
from pathlib import Path
from typing import Optional

import config

IMAGES_DIR = Path("images")


def sanitize_filename(query: str) -> str:
    """Convert query to safe filename."""
    # Remove special characters, replace spaces with underscores
    sanitized = re.sub(r"[^\w\s-]", "", query.lower())
    sanitized = re.sub(r"[\s-]+", "_", sanitized)
    return sanitized.strip("_")


def get_cached_image_path(query: str) -> Path:
    """Get the cache path for a query."""
    filename = sanitize_filename(query) + ".jpg"
    return IMAGES_DIR / filename


def fetch_image(query: str, force_download: bool = False) -> Optional[Path]:
    """
    Fetch an image from Pixabay based on search query.

    Args:
        query: Search term for the image
        force_download: If True, download even if cached

    Returns:
        Path to the downloaded image, or None if not found
    """
    IMAGES_DIR.mkdir(exist_ok=True)

    cache_path = get_cached_image_path(query)

    # Return cached image if exists
    if cache_path.exists() and not force_download:
        return cache_path

    # Search Pixabay
    params = {
        "key": config.PIXABAY_API_KEY if hasattr(config, "PIXABAY_API_KEY") else "",
        "q": query,
        "image_type": "photo",
        "per_page": 3,
        "safesearch": "true",
    }

    try:
        # Pixabay allows limited requests without API key
        url = config.PIXABAY_API_URL
        if not params["key"]:
            # Use without key (limited but works)
            url = f"{config.PIXABAY_API_URL}?q={query}&image_type=photo&per_page=3"
            response = requests.get(url, timeout=10)
        else:
            response = requests.get(url, params=params, timeout=10)

        data = response.json()

        if not data.get("hits"):
            return None

        # Get first result's image URL
        image_url = data["hits"][0].get("webformatURL")
        if not image_url:
            return None

        # Download image
        img_response = requests.get(image_url, timeout=15)
        img_response.raise_for_status()

        # Save to cache
        cache_path.write_bytes(img_response.content)

        return cache_path

    except (requests.RequestException, KeyError, IndexError) as e:
        print(f"Warning: Could not fetch image for '{query}': {e}")
        return None


def fetch_image_for_answer(correct_answer: str, image_setting: str = "auto") -> Optional[Path]:
    """
    Fetch image based on the correct answer.

    Args:
        correct_answer: The correct answer text
        image_setting: "auto" to fetch, path to use local, or None to skip

    Returns:
        Path to image or None
    """
    if image_setting is None or image_setting == "":
        return None

    if image_setting == "auto":
        return fetch_image(correct_answer)

    # Assume it's a local path
    local_path = Path(image_setting)
    if local_path.exists():
        return local_path

    # Try in images directory
    images_path = IMAGES_DIR / image_setting
    if images_path.exists():
        return images_path

    return None
