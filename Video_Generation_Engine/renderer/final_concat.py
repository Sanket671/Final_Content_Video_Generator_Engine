import subprocess
from pathlib import Path

OUTPUT_DIR = Path("outputs/youtube_shorts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def concat_scenes(scene_paths: list[Path]) -> Path:
    scene_paths = sorted(scene_paths, key=lambda p: int(p.stem.split("_")[1]))

    list_file = OUTPUT_DIR / "scenes.txt"
    with open(list_file, "w") as f:
        for p in scene_paths:
            f.write(f"file '{p.absolute()}'\n")

    out = OUTPUT_DIR / "final_video.mp4"

    # Re-encode audio from PCM to MP3 (robust, no corruption)
    cmd = (
        f'ffmpeg -y '
        f'-f concat -safe 0 -i "{list_file}" '
        f'-c:v copy '                     # video: keep as is
        f'-c:a libmp3lame -b:a 192k '    # audio: MP3 at 192k
        f'-ar 44100 -ac 2 '              # force stereo, 44.1 kHz
        f'"{out}"'
    )
    print(f"🎬 Stitching {len(scene_paths)} scenes into final video...")
    subprocess.run(cmd, shell=True, check=True)

    return out