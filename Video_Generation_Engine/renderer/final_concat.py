# renderer/final_concat.py
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("outputs/youtube_shorts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def concat_scenes(scene_paths: list[Path]) -> Path:
    # 🔒 Sort strictly by scene index to prevent order mixing
    # This assumes filenames are 'scene_1.mp4', 'scene_2.mp4', etc.
    scene_paths = sorted(
        scene_paths,
        key=lambda p: int(p.stem.split("_")[1])
    )

    list_file = OUTPUT_DIR / "scenes.txt"
    with open(list_file, "w") as f:
        for p in scene_paths:
            # Using absolute paths is safer for FFmpeg
            f.write(f"file '{p.absolute()}'\n")

    out = OUTPUT_DIR / "final_video.mp4"

    # We use -c copy because we standardized the formats in the render_scene step
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy", 
        str(out)
    ]

    print(f"🎬 Stitching {len(scene_paths)} scenes into final video...")
    subprocess.run(cmd, check=True)

    return out