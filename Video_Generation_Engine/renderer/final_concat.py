import subprocess
from pathlib import Path

OUTPUT_DIR = Path("outputs/youtube_shorts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def concat_scenes(scene_paths: list[Path]) -> Path:
    scene_paths = sorted(scene_paths, key=lambda p: int(p.stem.split("_")[1]))
    out = OUTPUT_DIR / "final_video.mp4"

    inputs = []
    filter_parts = []
    for i, p in enumerate(scene_paths):
        inputs.extend(["-i", str(p)])
        filter_parts.append(f"[{i}:v]")
        filter_parts.append(f"[{i}:a]")
    filter_parts.append(f"concat=n={len(scene_paths)}:v=1:a=1[outv][outa]")
    filter_str = "".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_str,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        str(out)
    ]
    print(f"🎬 Stitching {len(scene_paths)} scenes using concat filter...")
    subprocess.run(cmd, check=True)
    return out