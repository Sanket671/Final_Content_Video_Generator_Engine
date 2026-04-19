import subprocess
import urllib.request
import urllib.error
from pathlib import Path
import json
import shutil

# ============================================================
# GLOBAL CONFIG
# ============================================================

WIDTH = 1080
HEIGHT = 1920
FPS = 30

BRAND_BG = "#0EA49F"

PRODUCT_SCALE = 900
SHADOW_BLUR = 18

VIDEO_DIR = Path("video_segments")
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_DIR = Path("data/audio_cache")


# ============================================================
# HELPERS
# ============================================================

def run(cmd: str):
    subprocess.run(cmd, shell=True, check=True)


def check_ffmpeg_installed():
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        raise FileNotFoundError("FFmpeg not found in PATH")


def get_audio_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def get_video_duration(path: Path) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
        ).decode().strip()
    )


def download_image(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        return True
    except Exception as e:
        print(f"⚠️ Image download failed: {e}")
        return False


def prepare_image_source(source: str, scene_index: int) -> Path | None:
    p = Path(source)
    if p.exists():
        return p
    target = Path(f"tmp_product_{scene_index}.png")
    if download_image(source, target):
        return target
    return None


# ============================================================
# MAIN RENDER FUNCTION – PCM audio (safe, no corruption)
# ============================================================

def render_scene(scene: dict, scene_index: int, visual: dict, product=None, execute=True) -> Path:
    check_ffmpeg_installed()
    output = VIDEO_DIR / f"scene_{scene_index}.mp4"

    audio = Path("defaults/default_outro.wav") if scene.get("scene_id") == 9 else AUDIO_DIR / f"scene_{scene_index}.wav"
    if not audio.exists():
        raise FileNotFoundError(f"Missing audio: {audio}")

    audio_dur = get_audio_duration(audio)

    # ------------------------------------------------------------------
    # SCENE 1 – HOOK VIDEO (video + boosted PCM audio)
    # ------------------------------------------------------------------
    if scene.get("scene_id") == 1 and visual.get("type") == "video":
        video = Path(visual["path"])
        speed = audio_dur / get_video_duration(video)

        cmd = (
            f'ffmpeg -y '
            f'-i "{video}" '
            f'-i "{audio}" '
            f'-filter_complex "[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},setpts={speed}*PTS,fps={FPS}[v];[1:a]aresample=44100,volume=3.0[a]" '
            f'-map "[v]" -map "[a]" '
            f'-t {audio_dur} '
            f'-c:v libx264 -preset fast -pix_fmt yuv420p '
            f'-c:a pcm_s16le '          # PCM audio – safe for concatenation
            f'"{output}"'
        )
        run(cmd)
        return output

    # ------------------------------------------------------------------
    # PRODUCT HERO (image with zoom, PCM audio)
    # ------------------------------------------------------------------
    if visual.get("type") == "image":
        img = prepare_image_source(visual["path"], scene_index)
        if img is None:
            visual = {"type": "solid"}
        else:
            cmd = (
                f'ffmpeg -y '
                f'-f lavfi -i color=c={BRAND_BG}:s={WIDTH}x{HEIGHT}:d={audio_dur}:r={FPS} '
                f'-loop 1 -i "{img}" '
                f'-i "{audio}" '
                f'-filter_complex "[1:v]scale={PRODUCT_SCALE}:-1,format=rgba,boxblur={SHADOW_BLUR}:1,zoompan=z=\'1.02+0.0006*on\':d=1:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\',eq=contrast=1.05:saturation=0.92[product];[0:v][product]overlay=(W-w)/2:(H-h)/2[v];[2:a]aresample=44100,volume=3.0[a]" '
                f'-map "[v]" -map "[a]" '
                f'-t {audio_dur} '
                f'-c:v libx264 -preset fast -pix_fmt yuv420p '
                f'-c:a pcm_s16le '
                f'"{output}"'
            )
            run(cmd)
            return output

    # ------------------------------------------------------------------
    # OUTRO (end credits, PCM audio)
    # ------------------------------------------------------------------
    if scene.get("scene_id") == 9:
        credits = Path("defaults/end_credits.mp4")
        speed = audio_dur / get_video_duration(credits)
        cmd = (
            f'ffmpeg -y '
            f'-i "{credits}" '
            f'-i "{audio}" '
            f'-filter_complex "[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},setpts={speed}*PTS,fps={FPS}[v];[1:a]aresample=44100,volume=3.0[a]" '
            f'-map "[v]" -map "[a]" '
            f'-t {audio_dur} '
            f'-c:v libx264 -preset fast -pix_fmt yuv420p '
            f'-c:a pcm_s16le '
            f'"{output}"'
        )
        run(cmd)
        return output

    # ------------------------------------------------------------------
    # FALLBACK (solid colour, PCM audio)
    # ------------------------------------------------------------------
    cmd = (
        f'ffmpeg -y '
        f'-f lavfi -i color=c={BRAND_BG}:s={WIDTH}x{HEIGHT}:d={audio_dur}:r={FPS} '
        f'-i "{audio}" '
        f'-c:v libx264 -pix_fmt yuv420p '
        f'-c:a pcm_s16le '
        f'-map 0:v -map 1:a '
        f'-t {audio_dur} '
        f'"{output}"'
    )
    run(cmd)
    return output