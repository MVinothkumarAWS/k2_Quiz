"""Multi-source image fetcher with fallback support."""

import re
import os
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)


def sanitize_filename(query: str) -> str:
    """Convert query to safe filename."""
    sanitized = re.sub(r"[^\w\s-]", "", query.lower())
    sanitized = re.sub(r"[\s-]+", "_", sanitized)
    return sanitized.strip("_")


def get_cached_image_path(query: str) -> Path:
    """Get the cache path for a query."""
    filename = sanitize_filename(query) + ".jpg"
    return IMAGES_DIR / filename


def fetch_from_pexels(query: str) -> Optional[str]:
    """Fetch image from Pexels API (requires free API key)."""
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return None

    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": api_key}
        params = {"query": query, "per_page": 1, "orientation": "landscape"}

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["large"]
    except Exception as e:
        print(f"Pexels error: {e}")

    return None


def fetch_from_unsplash(query: str) -> Optional[str]:
    """Fetch image from Unsplash API (requires free API key)."""
    api_key = os.getenv("UNSPLASH_API_KEY")
    if not api_key:
        return None

    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": 1,
            "client_id": api_key,
            "orientation": "landscape"
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"Unsplash error: {e}")

    return None


def fetch_from_pixabay(query: str) -> Optional[str]:
    """Fetch image from Pixabay API (requires free API key)."""
    api_key = os.getenv("PIXABAY_API_KEY")
    if not api_key:
        return None

    try:
        url = "https://pixabay.com/api/"
        params = {
            "key": api_key,
            "q": query,
            "image_type": "photo",
            "per_page": 1,
            "orientation": "horizontal"
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("hits"):
                return data["hits"][0]["webformatURL"]
    except Exception as e:
        print(f"Pixabay error: {e}")

    return None


def fetch_from_wikimedia(query: str) -> Optional[str]:
    """Fetch image from Wikimedia Commons (free, no API key)."""
    try:
        # Search for images
        search_url = "https://commons.wikimedia.org/w/api.php"
        headers = {"User-Agent": "GK-Video-Generator/1.0 (Educational)"}

        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": f"File:{query}",
            "srnamespace": 6,  # File namespace
            "srlimit": 3
        }

        response = requests.get(search_url, params=search_params, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        results = data.get("query", {}).get("search", [])

        if not results:
            return None

        # Get the first image file info
        filename = results[0]["title"]

        # Get image URL
        image_params = {
            "action": "query",
            "format": "json",
            "titles": filename,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 1200
        }

        img_response = requests.get(search_url, params=image_params, headers=headers, timeout=10)

        if img_response.status_code == 200:
            img_data = img_response.json()
            pages = img_data.get("query", {}).get("pages", {})

            if pages:
                page = list(pages.values())[0]
                imageinfo = page.get("imageinfo", [])

                if imageinfo:
                    # Try thumb URL first, fallback to original
                    return imageinfo[0].get("thumburl") or imageinfo[0].get("url")

    except Exception as e:
        print(f"Wikimedia error: {e}")

    return None


def fetch_placeholder_image(query: str) -> Optional[str]:
    """Get placeholder image (fallback option)."""
    # Use Lorem Picsum for placeholder
    return f"https://picsum.photos/800/600?random={abs(hash(query)) % 1000}"


def fetch_image(query: str, force_download: bool = False) -> Optional[Path]:
    """
    Fetch an image from multiple sources with automatic fallback.

    Priority order:
    1. Pexels (if API key available)
    2. Unsplash (if API key available)
    3. Pixabay (if API key available)
    4. Wikimedia Commons (free, no key)
    5. Placeholder image (Lorem Picsum)

    Args:
        query: Search term for the image
        force_download: If True, download even if cached

    Returns:
        Path to the downloaded image, or None if all sources fail
    """
    cache_path = get_cached_image_path(query)

    # Return cached image if exists
    if cache_path.exists() and not force_download:
        return cache_path

    try:
        print(f"[*] Searching for image: '{query}'")
    except UnicodeEncodeError:
        print("[*] Searching for image...")

    # Try each source in order
    sources = [
        ("Pexels", fetch_from_pexels),
        ("Unsplash", fetch_from_unsplash),
        ("Pixabay", fetch_from_pixabay),
        ("Wikimedia", fetch_from_wikimedia),
        ("Placeholder", fetch_placeholder_image),
    ]

    image_url = None
    source_used = None

    for source_name, fetch_func in sources:
        try:
            image_url = fetch_func(query)
            if image_url:
                source_used = source_name
                print(f"[OK] Found on {source_name}")
                break
        except Exception as e:
            print(f"[WARN] {source_name} failed: {e}")
            continue

    if not image_url:
        try:
            print(f"[X] Could not fetch image for '{query}'")
        except UnicodeEncodeError:
            print("[X] Could not fetch image")
        return None

    # Download image
    try:
        headers = {"User-Agent": "GK-Video-Generator/1.0 (Educational)"}
        img_response = requests.get(image_url, headers=headers, timeout=15)
        img_response.raise_for_status()

        # Save to cache
        cache_path.write_bytes(img_response.content)
        print(f"[SAVED] {cache_path.name}")

        return cache_path

    except Exception as e:
        print(f"[X] Download error: {e}")
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
        fetched = fetch_image(correct_answer)
        if fetched:
            return fetched
        # Retry with India context for GK topics
        return fetch_image(f"India {correct_answer}")

    # Assume it's a local path
    local_path = Path(image_setting)
    if local_path.exists():
        return local_path

    # Try in images directory
    images_path = IMAGES_DIR / image_setting
    if images_path.exists():
        return images_path

    return None
