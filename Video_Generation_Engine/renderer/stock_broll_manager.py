import os
import requests
from pathlib import Path

# Read Pexels API key if present, but do not raise at import time. That made
# importing this module fatal when the environment variable was missing.
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Make the stock b-roll directory module-relative so it works regardless of CWD
BASE_DIR = Path(__file__).resolve().parents[1] / "data" / "stock_broll"
BASE_DIR.mkdir(parents=True, exist_ok=True)

PEXELS_URL = "https://api.pexels.com/videos/search"
BROLL_DIR = BASE_DIR


def get_stock_broll(keyword: str):
    videos = list(BROLL_DIR.glob("*.mp4"))
    if not videos:
        return None
    return str(videos[hash(keyword) % len(videos)])


def get_broll_clip(keyword: str) -> Path:
    """
    Fetches and caches a short vertical-friendly stock video for the keyword.
    Requires `PEXELS_API_KEY` to be set in the environment.
    """
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY not set")

    keyword_dir = BASE_DIR / keyword
    keyword_dir.mkdir(parents=True, exist_ok=True)

    cached = list(keyword_dir.glob("*.mp4"))
    if cached:
        return cached[0]

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keyword.replace("_", " "),
        "per_page": 5,
        "orientation": "portrait"
    }

    r = requests.get(PEXELS_URL, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    for video in data.get("videos", []):
        duration = video.get("duration", 0)
        if duration > 10:
            continue

        for file in video.get("video_files", []):
            if file.get("quality") == "sd":
                url = file["link"]
                out = keyword_dir / f"{video['id']}.mp4"
                with requests.get(url, stream=True) as v:
                    v.raise_for_status()
                    with open(out, "wb") as f:
                        for chunk in v.iter_content(chunk_size=8192):
                            f.write(chunk)
                return out

    raise RuntimeError(f"No suitable B-roll found for keyword: {keyword}")
