"""
YouTube search: find relevant videos for investment research.
API key in config (YOUTUBE_API_KEY). Optional feature.
"""
import logging
from typing import List, Optional

from config.config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)


def search_youtube(query: str, max_results: int = 5) -> str:
    """
    Search YouTube and return a formatted string of video titles, channels, and links
    for the LLM to use.
    """
    if not YOUTUBE_API_KEY:
        logger.debug("YOUTUBE_API_KEY not set; skipping YouTube search.")
        return ""
    try:
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        req = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results,
            relevanceLanguage="en",
        )
        res = req.execute()
        parts = []
        for item in res.get("items", []):
            sid = item.get("id", {}).get("videoId", "")
            snip = item.get("snippet", {})
            title = snip.get("title", "")
            channel = snip.get("channelTitle", "")
            url = f"https://www.youtube.com/watch?v={sid}" if sid else ""
            parts.append(f"- {title} (Channel: {channel})\n  {url}")
        return "\n".join(parts) if parts else ""
    except Exception as e:
        logger.exception("YouTube search failed: %s", e)
        return f"[YouTube search error: {e}]"
