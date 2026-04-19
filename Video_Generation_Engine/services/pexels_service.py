import os
import requests
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
STOCK_VIDEO_PATH = Path("data/stock_broll")
STOCK_VIDEO_PATH.mkdir(parents=True, exist_ok=True)

def fetch_and_save_pexels_video_batch(query: str, count: int = 20):
    headers = {"Authorization": PEXELS_API_KEY}
    
    modifiers = [
        "cinematic lighting", 
        "slow motion", 
        "golden hour", 
        "bokeh background", 
        "lifestyle footage"
    ]
    
    enhanced_query = f"{query} {random.choice(modifiers)}"
    url = "https://api.pexels.com/videos/search"
    params = {
        "query": enhanced_query,
        "per_page": count,
        "orientation": "portrait",
        "size": "medium"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    if not data.get("videos"):
        return []

    video_options = []
    for video_meta in data["videos"]:
        v_id = video_meta.get("id")
        duration = video_meta.get("duration", 0)
        
        # Skip low-quality or ultra-short clips
        if duration < 4: continue
        
        filename = f"pexels_{v_id}.mp4"
        save_path = STOCK_VIDEO_PATH / filename

        if not save_path.exists():
            video_files = video_meta.get("video_files", [])
            # Find vertical HD link (1080p+)
            video_url = next((f["link"] for f in video_files if f.get("height", 0) >= 1080 and f.get("height", 0) > f.get("width", 0)), video_files[0]["link"])
            
            print(f"📥 Downloading cinematic {query} video: {v_id}...")
            download_response = requests.get(video_url, stream=True)
            with open(save_path, "wb") as f:
                for chunk in download_response.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
        
        video_options.append({
            "id": v_id,
            "path": str(save_path),
            "duration": duration
        })
                
    return video_options

# Usage with your Pydantic model
