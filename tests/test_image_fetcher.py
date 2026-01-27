"""Tests for image fetcher."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.image_fetcher import fetch_image, get_cached_image_path


def test_get_cached_image_path():
    """Test cache path generation."""
    path = get_cached_image_path("Tiger")
    assert "tiger" in str(path).lower()
    assert path.suffix == ".jpg"


def test_get_cached_image_path_sanitizes_query():
    """Test that special characters are removed from cache path."""
    path = get_cached_image_path("What is a Tiger?")
    assert "?" not in str(path)
    assert "what_is_a_tiger" in str(path).lower()


@patch("src.image_fetcher.requests.get")
def test_fetch_image_downloads_and_caches(mock_get, tmp_path):
    """Test image download and caching."""
    # Mock Pixabay API response
    mock_api_response = MagicMock()
    mock_api_response.json.return_value = {
        "hits": [{"webformatURL": "https://example.com/tiger.jpg"}]
    }

    # Mock image download response
    mock_image_response = MagicMock()
    mock_image_response.content = b"fake image data"

    mock_get.side_effect = [mock_api_response, mock_image_response]

    with patch("src.image_fetcher.IMAGES_DIR", tmp_path):
        result = fetch_image("tiger")

    assert result is not None
    assert result.exists()


@patch("src.image_fetcher.requests.get")
def test_fetch_image_returns_none_on_no_results(mock_get):
    """Test handling of no search results."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"hits": []}
    mock_get.return_value = mock_response

    result = fetch_image("xyznonexistent123")
    assert result is None
