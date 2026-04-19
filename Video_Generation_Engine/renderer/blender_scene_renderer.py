import subprocess
from pathlib import Path

BLENDER_BIN = "/Applications/Blender.app/Contents/MacOS/Blender"

def render_product_scene(
    product_image: Path,
    duration: float,
    output_dir: Path
):
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        BLENDER_BIN,
        "--background",
        "blender/studio.blend",
        "--python",
        "blender/render_frames.py",
        "--",
        str(product_image),
        str(duration),
        str(output_dir)
    ]

    subprocess.run(cmd, check=True)
    return output_dir
