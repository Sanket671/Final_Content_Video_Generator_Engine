import subprocess
import shlex
import urllib.request
import urllib.error
from pathlib import Path
import json
import shutil

# ============================================================
# GLOBAL CONFIG — COMMERCIAL MODE
# ============================================================

WIDTH = 1080
HEIGHT = 1920
FPS = 30

BRAND_BG = "#0EA49F"

PRODUCT_SCALE = 900
PRODUCT_ZOOM = "1.02+0.0008*n"
PRODUCT_CONTRAST = 1.05
PRODUCT_SATURATION = 0.92
SHADOW_BLUR = 18

VIDEO_DIR = Path("video_segments")
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_DIR = Path("data/audio_cache")


# ============================================================
# HELPERS
# ============================================================

def run(cmd: str):
    subprocess.run(shlex.split(cmd), check=True)


def check_ffmpeg_installed():
    """Verifies that ffmpeg and ffprobe are available in the system PATH."""
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        raise FileNotFoundError(
            "❌ FFmpeg or FFprobe not found! This project requires FFmpeg installed system-wide.\n"
            "   👉 On macOS, run: brew install ffmpeg\n"
            "   👉 On Ubuntu, run: sudo apt install ffmpeg"
        )


def get_audio_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(path)
        ],
        capture_output=True,
        text=True,
        check=True
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def get_video_duration(path: Path) -> float:
    return float(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path)
            ]
        ).decode().strip()
    )


def escape_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
            .replace("'", "'\\''")
            .replace(":", "\\:")
            .replace("%", "\\%")
            .replace("#", "\\#")
            .replace(",", "\\,")
    )


def download_image(url: str, dest: Path) -> bool:
    if dest.exists():
        return True

    try:
        req = urllib.request.Request(
            str(url),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req) as response, open(dest, "wb") as out:
            out.write(response.read())
        return True
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"⚠️ Could not download product image: {url} ({exc})")
        return False


def prepare_image_source(source: str, scene_index: int) -> Path | None:
    source_path = Path(source)
    if source_path.exists():
        return source_path

    suffix = Path(source).suffix or ".png"
    target = Path(f"tmp_product_{scene_index}{suffix}")
    if download_image(source, target):
        return target

    return None


# ============================================================
# MAIN RENDER FUNCTION
# ============================================================

def render_scene(
    scene: dict,
    scene_index: int,
    visual: dict,
    product=None,
    execute: bool = True
) -> Path:
    
    # Ensure FFmpeg is available before starting
    check_ffmpeg_installed()

    output = VIDEO_DIR / f"scene_{scene_index}.mp4"

    # ----------------------------
    # AUDIO
    # ----------------------------
    audio = (
        Path("defaults/default_outro.wav")
        if scene.get("scene_id") == 9
        else AUDIO_DIR / f"scene_{scene_index}.wav"
    )

    if not audio.exists():
        raise FileNotFoundError(f"Missing audio file: {audio}")

    audio_dur = get_audio_duration(audio)
    overlay_text = escape_text(scene.get("overlay", ""))

    # ============================================================
    # SCENE: SILENCE (COMMERCIAL PAUSE)
    # ============================================================
    if scene.get("scene_type") == "silence":
        cmd = f"""
        ffmpeg -y
        -f lavfi -i color=black:s={WIDTH}x{HEIGHT}:d={scene['duration']}
        -c:v libx264 -pix_fmt yuv420p
        "{output}"
        """
        run(cmd)
        return output

    # ============================================================
    # SCENE 1 — HOOK VIDEO
    # ============================================================
    if scene.get("scene_id") == 1 and visual.get("type") == "video":
        video = Path(visual["path"])
        speed = audio_dur / get_video_duration(video)

        cmd = f"""
        ffmpeg -y
        -i "{video}"
        -i "{audio}"
        -filter_complex "
            [0:v]
            scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,
            crop={WIDTH}:{HEIGHT},
            setpts={speed}*PTS,
            fps={FPS}[v];
            [1:a]aresample=44100[a]
        "
        -map "[v]" -map "[a]"
        -t {audio_dur}
        -c:v libx264 -preset slow -pix_fmt yuv420p
        -c:a aac -b:a 192k
        "{output}"
        """
        run(cmd)
        return output

    # ============================================================
    # SCENE: PRODUCT HERO (COMMERCIAL CORE)
    # ============================================================
    if visual.get("type") == "image":
        img = prepare_image_source(visual["path"], scene_index)
        if img is None:
            visual = {"type": "solid"}
        else:
            cmd = f"""
            ffmpeg -y
            -f lavfi -i color=c={BRAND_BG}:s={WIDTH}x{HEIGHT}:d={audio_dur}:r={FPS}
            -loop 1 -i "{img}"
            -i "{audio}"
            -filter_complex "
                [1:v]
                scale={PRODUCT_SCALE}:-1,
                format=rgba,
                boxblur={SHADOW_BLUR}:1,
                zoompan=
        z='1.02+0.0006*on':
        d=1:
        x='iw/2-(iw/zoom/2)':
        y='ih/2-(ih/zoom/2)',

                eq=contrast={PRODUCT_CONTRAST}:saturation={PRODUCT_SATURATION}
                [product];

                [0:v][product]
                overlay=(W-w)/2:(H-h)/2
                [v];

                [2:a]aresample=44100[a]
            "
            -map "[v]" -map "[a]"
            -t {audio_dur}
            -c:v libx264 -preset slow -pix_fmt yuv420p
            -c:a aac -b:a 192k
            "{output}"
            """
            run(cmd)
            return output

    # ============================================================
    # SCENE 9 — OUTRO / END CREDITS
    # ============================================================
    if scene.get("scene_id") == 9:
        credits = Path("defaults/end_credits.mp4")
        speed = audio_dur / get_video_duration(credits)

        cmd = f"""
        ffmpeg -y
        -i "{credits}"
        -i "{audio}"
        -filter_complex "
            scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,
            crop={WIDTH}:{HEIGHT},
            setpts={speed}*PTS,
            fps={FPS}[v];
            [1:a]aresample=44100[a]
        "
        -map "[v]" -map "[a]"
        -t {audio_dur}
        -c:v libx264 -preset slow -pix_fmt yuv420p
        -c:a aac -b:a 192k
        "{output}"
        """
        run(cmd)
        return output

    # ============================================================
    # FALLBACK (SHOULD NEVER HIT IN COMMERCIAL MODE)
    # ============================================================
    cmd = f"""
    ffmpeg -y
    -f lavfi -i color=c={BRAND_BG}:s={WIDTH}x{HEIGHT}:d={audio_dur}:r={FPS}
    -i "{audio}"
    -filter_complex "
        drawtext=text='{overlay_text}':
        fontcolor=white:
        fontsize=52:
        x=(w-text_w)/2:
        y=(h-text_h)/2
        [v];
        [1:a]aresample=44100[a]
    "
    -map "[v]" -map "[a]"
    -t {audio_dur}
    -c:v libx264 -pix_fmt yuv420p
    -c:a aac -b:a 192k
    "{output}"
    """
    run(cmd)
    return output
