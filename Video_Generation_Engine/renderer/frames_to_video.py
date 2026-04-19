import subprocess
from pathlib import Path

def frames_to_video(
    frames_dir: Path,
    audio_path: Path,
    output_path: Path,
    fps: int = 24
):
    frame_pattern = frames_dir / "%04d.png"

    cmd = [
        "ffmpeg",
        "-y",
        "-r", str(fps),
        "-i", str(frame_pattern),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(output_path)
    ]

    subprocess.run(cmd, check=True)
    return output_path
