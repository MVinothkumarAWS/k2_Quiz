"""YouTube Data API v3 uploader with OAuth2 authentication."""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import config

# OAuth2 scopes required for uploading + playlist management
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

# Default paths (relative to project root)
DEFAULT_CLIENT_SECRETS = "client_secret.json"
DEFAULT_TOKEN_FILE = "youtube_token.json"

# YouTube category IDs
CATEGORY_EDUCATION = "27"
CATEGORY_ENTERTAINMENT = "24"
CATEGORY_PEOPLE_BLOGS = "22"

# Resumable upload chunk size (10 MB)
CHUNK_SIZE = 10 * 1024 * 1024

# Max retry attempts on transient errors
MAX_RETRIES = 5
RETRIABLE_STATUS_CODES = {500, 502, 503, 504}


def get_authenticated_service(
    client_secrets_file: str = DEFAULT_CLIENT_SECRETS,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> object:
    """
    Authenticate with YouTube API using OAuth2.

    On first run, opens a browser window for the user to authorize.
    Token is saved to token_file for subsequent runs.

    Args:
        client_secrets_file: Path to client_secrets.json from Google Cloud Console
        token_file: Path to save/load the OAuth token

    Returns:
        Authenticated YouTube API service object
    """
    creds = None

    # Load existing token if available
    if Path(token_file).exists():
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Refresh or re-authorize if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing YouTube access token...")
            creds.refresh(Request())
        else:
            if not Path(client_secrets_file).exists():
                raise FileNotFoundError(
                    f"client_secret.json not found at '{client_secrets_file}'.\n"
                    "Please download it from Google Cloud Console:\n"
                    "  1. Go to https://console.cloud.google.com/\n"
                    "  2. Create a project → Enable YouTube Data API v3\n"
                    "  3. Create OAuth 2.0 credentials (Desktop app)\n"
                    "  4. Download and save as 'client_secret.json' in project root"
                )

            print("Opening browser for YouTube authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(token_file, "w") as f:
            f.write(creds.to_json())
        print(f"Token saved to {token_file}")

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str | Path,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = CATEGORY_EDUCATION,
    privacy: str = "public",
    is_shorts: bool = False,
    publish_at: str | None = None,
    client_secrets_file: str = DEFAULT_CLIENT_SECRETS,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> dict:
    """
    Upload a video to YouTube.

    Args:
        video_path: Path to the .mp4 video file
        title: Video title (max 100 chars)
        description: Video description
        tags: List of tags
        category_id: YouTube category ID (default: 27 = Education)
        privacy: "public", "private", or "unlisted"
        is_shorts: If True, adds #Shorts to title/description for Shorts detection
        publish_at: ISO 8601 datetime string to schedule publish (e.g. "2026-02-18T10:00:00Z")
                    Requires privacy="private" to be set initially then YouTube publishes it
        client_secrets_file: Path to client_secrets.json
        token_file: Path to OAuth token file

    Returns:
        Dict with video_id and video_url on success
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Shorts: append #Shorts hashtag
    if is_shorts:
        if "#Shorts" not in title:
            title = f"{title} #Shorts"
        if "#Shorts" not in description:
            description = f"{description}\n\n#Shorts".strip()

    # Truncate title to 100 chars (YouTube limit)
    title = title[:100]

    # Build tags list
    tags = tags or []
    if is_shorts and "Shorts" not in tags:
        tags.append("Shorts")

    # Build snippet and status
    snippet = {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": category_id,
        "defaultLanguage": "en",
    }

    status = {
        "privacyStatus": "private" if publish_at else privacy,
        "selfDeclaredMadeForKids": False,
    }

    # Schedule publish time
    if publish_at:
        status["publishAt"] = publish_at

    body = {
        "snippet": snippet,
        "status": status,
    }

    print(f"\nUploading: {video_path.name}")
    print(f"Title: {title}")
    print(f"Privacy: {status['privacyStatus']}")
    if publish_at:
        print(f"Scheduled publish: {publish_at}")

    youtube = get_authenticated_service(client_secrets_file, token_file)

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        chunksize=CHUNK_SIZE,
        resumable=True,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    # Execute with retry logic
    video_id = _execute_upload_with_retry(request, video_path.name)

    video_url = f"https://youtu.be/{video_id}"
    print(f"Upload complete! Video URL: {video_url}")

    return {
        "video_id": video_id,
        "video_url": video_url,
        "title": title,
        "privacy": status["privacyStatus"],
    }


def _execute_upload_with_retry(request, filename: str) -> str:
    """Execute resumable upload with exponential backoff retry."""
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print(f"  Uploading {filename}...", end="", flush=True)
            status, response = request.next_chunk()

            if status:
                pct = int(status.progress() * 100)
                print(f"\r  Uploading {filename}... {pct}%", end="", flush=True)

        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"HTTP {e.resp.status}: {e.content}"
            else:
                raise

        except Exception as e:
            error = str(e)

        if error:
            retry += 1
            if retry > MAX_RETRIES:
                raise Exception(f"Upload failed after {MAX_RETRIES} retries: {error}")

            wait = 2 ** retry
            print(f"\n  Retry {retry}/{MAX_RETRIES} in {wait}s... ({error})")
            time.sleep(wait)
            error = None

    print()  # newline after progress
    return response["id"]


def upload_batch(
    video_paths: list[str | Path],
    title_prefix: str,
    description_template: str = "",
    tags: list[str] | None = None,
    category_id: str = CATEGORY_EDUCATION,
    privacy: str = "public",
    is_shorts: bool = False,
    delay_between: int = 5,
    playlist_id: str | None = None,
    client_secrets_file: str = DEFAULT_CLIENT_SECRETS,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> list[dict]:
    """
    Upload multiple videos to YouTube.

    Args:
        video_paths: List of video file paths
        title_prefix: Base title (video number will be appended for multiple videos)
        description_template: Description for all videos
        tags: Tags for all videos
        category_id: YouTube category ID
        privacy: Privacy setting
        is_shorts: Whether these are YouTube Shorts
        delay_between: Seconds to wait between uploads (avoids rate limiting)
        playlist_id: If set, adds each uploaded video to this playlist
        client_secrets_file: Path to client_secrets.json
        token_file: Path to OAuth token file

    Returns:
        List of result dicts with video_id and video_url
    """
    results = []
    total = len(video_paths)

    # Authenticate once before batch
    youtube_service = get_authenticated_service(client_secrets_file, token_file)

    for i, video_path in enumerate(video_paths, 1):
        video_path = Path(video_path)

        # Build title: "Prefix #1" for multiple, just prefix for single
        if total > 1:
            title = f"{title_prefix} #{i}"
        else:
            title = title_prefix

        try:
            result = upload_video(
                video_path=video_path,
                title=title,
                description=description_template,
                tags=tags,
                category_id=category_id,
                privacy=privacy,
                is_shorts=is_shorts,
                client_secrets_file=client_secrets_file,
                token_file=token_file,
            )
            results.append(result)
            print(f"[{i}/{total}] Uploaded: {result['video_url']}")

            # Add to playlist if specified
            if playlist_id and "video_id" in result:
                add_video_to_playlist(
                    result["video_id"], playlist_id,
                    client_secrets_file, token_file,
                )

        except Exception as e:
            print(f"[{i}/{total}] FAILED to upload {video_path.name}: {e}")
            results.append({
                "video_path": str(video_path),
                "error": str(e),
            })

        # Wait between uploads to avoid rate limiting
        if i < total and delay_between > 0:
            print(f"Waiting {delay_between}s before next upload...")
            time.sleep(delay_between)

    return results


def create_playlist(
    title: str,
    description: str = "",
    privacy: str = "public",
    client_secrets_file: str = DEFAULT_CLIENT_SECRETS,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> str:
    """
    Create a YouTube playlist and return its playlist ID.

    Args:
        title: Playlist title
        description: Playlist description
        privacy: "public", "private", or "unlisted"
        client_secrets_file: Path to client_secrets.json
        token_file: Path to OAuth token file

    Returns:
        Playlist ID string (e.g. "PLxxx...")
    """
    youtube = get_authenticated_service(client_secrets_file, token_file)

    body = {
        "snippet": {
            "title": title[:150],         # YouTube limit 150 chars
            "description": description,
        },
        "status": {
            "privacyStatus": privacy,
        },
    }

    response = youtube.playlists().insert(
        part="snippet,status",
        body=body,
    ).execute()

    playlist_id = response["id"]
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"Playlist created: {title}")
    print(f"Playlist URL: {playlist_url}")
    return playlist_id


def get_or_create_playlist(
    title: str,
    description: str = "",
    privacy: str = "public",
    client_secrets_file: str = DEFAULT_CLIENT_SECRETS,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> str:
    """
    Find an existing playlist by title, or create it if it doesn't exist.

    Returns:
        Playlist ID string
    """
    youtube = get_authenticated_service(client_secrets_file, token_file)

    # Search channel's playlists for matching title
    next_page = None
    while True:
        req = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50,
            pageToken=next_page,
        )
        resp = req.execute()

        for item in resp.get("items", []):
            if item["snippet"]["title"].lower() == title.lower():
                playlist_id = item["id"]
                print(f"Using existing playlist: {title} ({playlist_id})")
                return playlist_id

        next_page = resp.get("nextPageToken")
        if not next_page:
            break

    # Not found — create it
    return create_playlist(title, description, privacy, client_secrets_file, token_file)


def add_video_to_playlist(
    video_id: str,
    playlist_id: str,
    client_secrets_file: str = DEFAULT_CLIENT_SECRETS,
    token_file: str = DEFAULT_TOKEN_FILE,
) -> bool:
    """
    Add a video to a playlist.

    Args:
        video_id: YouTube video ID (e.g. "dQw4w9WgXcQ")
        playlist_id: YouTube playlist ID (e.g. "PLxxx...")
        client_secrets_file: Path to client_secrets.json
        token_file: Path to OAuth token file

    Returns:
        True on success, False on failure
    """
    youtube = get_authenticated_service(client_secrets_file, token_file)

    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    },
                }
            },
        ).execute()
        print(f"  Added video {video_id} → playlist {playlist_id}")
        return True
    except HttpError as e:
        print(f"  Failed to add video to playlist: {e}")
        return False


def build_description(
    category: str = "",
    language: str = "english",
    channel_name: str | None = None,
    question_count: int | None = None,
    is_shorts: bool = False,
) -> str:
    """
    Build a standard video description for K2_Quiz channel.

    Args:
        category: Quiz topic/category
        language: Video language
        channel_name: YouTube channel name
        question_count: Number of questions in the video
        is_shorts: Whether this is a Shorts video

    Returns:
        Formatted description string
    """
    if channel_name is None:
        channel_name = config.CHANNEL_NAME

    lines = []

    if category:
        lines.append(f"Test your knowledge of {category}!")
    else:
        lines.append("Test your General Knowledge!")

    if question_count:
        if is_shorts:
            lines.append(f"Can you answer this question? Comment your answer below!")
        else:
            lines.append(f"{question_count} questions to challenge yourself.")

    lines.append("")
    lines.append("🔔 Subscribe to never miss a quiz!")
    lines.append("👍 Like if you enjoyed")
    lines.append("💬 Share your score in the comments")
    lines.append("")
    lines.append(f"Channel: {channel_name}")
    lines.append("")

    # Tags
    base_tags = ["GK Quiz", "Indian GK", "General Knowledge", "Quiz", "K2Quiz"]
    if category:
        base_tags.append(category)
    if language == "tamil":
        base_tags.extend(["Tamil Quiz", "Tamil GK"])
    if is_shorts:
        base_tags.append("#Shorts")

    lines.append(" ".join(f"#{t.replace(' ', '')}" for t in base_tags))

    return "\n".join(lines)


def build_tags(
    category: str = "",
    language: str = "english",
    is_shorts: bool = False,
) -> list[str]:
    """Build a list of relevant tags for the video."""
    tags = [
        "GK Quiz", "Indian GK", "General Knowledge", "Quiz",
        "K2 Quiz", "India Quiz", "Knowledge Test", "MCQ",
    ]

    if category:
        tags.append(category)
        # Add category words as individual tags
        for word in category.split():
            if len(word) > 3:
                tags.append(word)

    if language == "tamil":
        tags.extend(["Tamil Quiz", "Tamil GK", "தமிழ் வினாடி வினா"])

    if is_shorts:
        tags.extend(["Shorts", "YouTube Shorts", "Short Video"])

    return tags[:500]  # YouTube tag limit
