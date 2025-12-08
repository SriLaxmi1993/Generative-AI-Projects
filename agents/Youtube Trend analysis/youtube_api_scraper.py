import os
import time
from datetime import datetime
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def _extract_channel_id(channel_url: str) -> str | None:
    """Extract channel ID or handle/custom from URL."""
    if not channel_url:
        return None
    channel_url = channel_url.strip()
    if "/channel/" in channel_url:
        return channel_url.split("/channel/")[1].split("/")[0]
    if "/@" in channel_url:
        return channel_url.split("/@")[1].split("/")[0]
    if "/c/" in channel_url:
        return channel_url.split("/c/")[1].split("/")[0]
    return None


def _resolve_channel_id(channel_url: str) -> str | None:
    """
    Resolve a channel URL/handle/custom name to a channelId via YouTube Data API.
    """
    extracted = _extract_channel_id(channel_url)
    if not extracted:
        return None

    # If it already looks like a channel id (starts with UC and length > 20), return it
    if extracted.startswith("UC") and len(extracted) > 20:
        return extracted

    # Otherwise search for the channel by handle/custom name
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": extracted if extracted.startswith("@") else f"@{extracted}",
        "type": "channel",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY,
    }
    try:
        resp = requests.get(search_url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if items:
            return items[0]["snippet"]["channelId"]
    except Exception as e:
        print(f"Channel resolve failed for {channel_url}: {e}")

    return None


def _iso_date(date_str: str | None, default_time: str) -> str | None:
    if not date_str:
        return None
    try:
        return f"{date_str}T{default_time}Z"
    except Exception:
        return None


def fetch_channel_videos(
    channel_url: str,
    num_videos: int = 3,
    start_date: str | None = None,
    end_date: str | None = None,
    get_transcripts: bool = True,
    transcript_timeout: float = 8.0,
):
    """
    Fetch latest videos from a channel using YouTube Data API v3.
    Returns list of dicts with metadata and optional transcripts.
    """
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY missing. Set it in .env")

    channel_id = _resolve_channel_id(channel_url)
    if not channel_id:
        raise ValueError(f"Could not resolve channel: {channel_url}")

    search_url = "https://www.googleapis.com/youtube/v3/search"
    published_after = _iso_date(start_date, "00:00:00") if start_date else None
    published_before = _iso_date(end_date, "23:59:59") if end_date else None

    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "maxResults": min(num_videos, 5),  # API limit per request
        "key": YOUTUBE_API_KEY,
        "type": "video",
    }
    if published_after:
        params["publishedAfter"] = published_after
    if published_before:
        params["publishedBefore"] = published_before

    try:
        resp = requests.get(search_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
    except Exception as e:
        print(f"Search failed for {channel_url}: {e}")
        items = []

    # Fallback: if no items, try a generic search by handle/name (no channelId filter)
    if not items:
        try:
            fallback_params = {
                "part": "snippet",
                "q": channel_id,
                "order": "date",
                "maxResults": min(num_videos, 5),
                "key": YOUTUBE_API_KEY,
                "type": "video",
            }
            if published_after:
                fallback_params["publishedAfter"] = published_after
            if published_before:
                fallback_params["publishedBefore"] = published_before

            resp = requests.get(search_url, params=fallback_params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            if items:
                print(f"Fallback search returned {len(items)} videos for {channel_url}")
        except Exception as e:
            print(f"Fallback search failed for {channel_url}: {e}")
            items = []

    videos = []
    for item in items:
        vid = item["id"].get("videoId")
        if not vid:
            continue
        snippet = item.get("snippet", {})
        videos.append(
            {
                "title": snippet.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "shortcode": vid,
                "description": snippet.get("description", ""),
                "thumbnail": (snippet.get("thumbnails", {}).get("high") or {}).get(
                    "url", ""
                ),
                "views": "",
                "published_date": snippet.get("publishedAt", ""),
                "channel": snippet.get("channelTitle", ""),
                "transcript": [],
                "formatted_transcript": [],
            }
        )

    # Limit to requested count
    videos = videos[:num_videos]

    if not get_transcripts or not videos:
        return videos

    # Fetch transcripts with fallbacks
    for idx, v in enumerate(videos):
        vid = v["shortcode"]
        print(f"Transcript {idx+1}/{len(videos)} for {vid}...")
        start_t = time.time()
        formatted = []
        raw_text = []
        try:
            # Try listing available transcripts to pick best option
            available = YouTubeTranscriptApi.list_transcripts(vid)
            transcript_obj = None
            try:
                transcript_obj = available.find_transcript(['en'])
            except:
                try:
                    transcript_obj = available.find_manually_created_transcript(['en'])
                except:
                    try:
                        transcript_obj = available.find_generated_transcript(['en'])
                    except:
                        # If no English, grab the first available
                        transcript_obj = next(iter(available))
            transcript_data = transcript_obj.fetch()
        except Exception as e2:
            elapsed = time.time() - start_t
            print(f"Transcript failed for {vid} after {elapsed:.1f}s: {e2}")
            transcript_data = []

        for t in transcript_data:
            text = t.get("text", "")
            if not text:
                continue
            start_time = t.get("start", 0.0)
            end_time = start_time + t.get("duration", 0.0)
            formatted.append(
                {
                    "text": text,
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )
            raw_text.append(text)

        v["formatted_transcript"] = formatted
        v["transcript"] = raw_text

        # If still empty, synthesize a minimal transcript from metadata so analysis can proceed
        if not v["formatted_transcript"]:
            synthesized = f"Title: {v.get('title','')}. Description: {v.get('description','')}. URL: {v.get('url','')}"
            v["formatted_transcript"] = [
                {
                    "text": synthesized,
                    "start_time": 0.0,
                    "end_time": 0.0,
                }
            ]
            v["transcript"] = [synthesized]


    return videos

