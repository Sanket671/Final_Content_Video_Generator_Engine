import subprocess
import urllib.request
import urllib.error
from pathlib import Path
import json
import shutil

WIDTH = 1080
HEIGHT = 1920
FPS = 30
BRAND_BG = "#0EA49F"
PRODUCT_SCALE = 900
SHADOW_BLUR = 18
# Use module-relative directories so behavior is consistent regardless of CWD
MODULE_ROOT = Path(__file__).resolve().parents[1]
VIDEO_DIR = MODULE_ROOT / "video_segments"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR = MODULE_ROOT / "data" / "audio_cache"


def _format_ass_time(seconds: float) -> str:
    # ASS time format: H:MM:SS.cs (centiseconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ensure_resampled_audio(src: Path, scene_index: int) -> Path:
    """Ensure audio is resampled to 44100 Hz, stereo PCM WAV.

    Returns the resampled Path (creates it if missing).
    """
    dest = AUDIO_DIR / f"scene_{scene_index}_pcm.wav"
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = (
        f'ffmpeg -y -i "{src.as_posix()}" -ar 44100 -ac 2 -c:a pcm_s16le "{dest.as_posix()}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    return dest

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
    # Fallbacks: try a few known default images bundled with the repo
    default_candidates = [
        Path("default_product.png"),
        Path("defaults/Card_image.png"),
        Path("defaults/search_bar.png"),
        Path("defaults/search_bar_.png"),
    ]
    for default_img in default_candidates:
        if default_img.exists():
            print(f"⚠️ Using default product image: {default_img}")
            return default_img
    return None

def create_ass_subtitle(text: str, duration: float, font_size: int = 48) -> Path:
    """Create a minimal ASS subtitle that shows `text` for the full `duration`.

    Uses forward slashes in the written path (Path.as_posix()).
    """
    ass_file = VIDEO_DIR / f"temp_sub_{abs(hash(text))}.ass"
    ass_file.parent.mkdir(parents=True, exist_ok=True)

    safe_text = text.replace("\n", "\\N")
    start = _format_ass_time(0)
    end = _format_ass_time(max(0.5, duration))

    ass_content = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {WIDTH}\n"
        f"PlayResY: {HEIGHT}\n"
        "WrapStyle: 2\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,5,10,10,20,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        f"Dialogue: 0,{start},{end},Default,,0,0,0,,{safe_text}\n"
    )

    ass_file.write_text(ass_content, encoding="utf-8")
    return ass_file

def render_scene(scene: dict, scene_index: int, visual: dict, product=None, execute=True) -> Path:
    check_ffmpeg_installed()
    output = VIDEO_DIR / f"scene_{scene_index}.mp4"
    original_audio = Path("defaults/default_outro.wav") if scene.get("scene_id") == 9 else AUDIO_DIR / f"scene_{scene_index}.wav"
    if not original_audio.exists():
        raise FileNotFoundError(f"Missing audio: {original_audio}")

    # Resample/convert to consistent PCM WAV (44100 Hz, stereo) for perfect sync
    audio = ensure_resampled_audio(original_audio, scene_index)
    audio_dur = get_audio_duration(audio)
    overlay_text = scene.get("overlay", "") or ""
    font_size = 48 if len(overlay_text) < 40 else 36

    # ------------------------------------------------------------------
    # SCENE 1 – HOOK VIDEO (with ASS subtitles)
    # ------------------------------------------------------------------
    if scene.get("scene_id") == 1 and visual.get("type") == "video":
        video = Path(visual["path"])
        speed = audio_dur / get_video_duration(video)
        ass_file = create_ass_subtitle(overlay_text, audio_dur, font_size)
        ass_path = ass_file.as_posix()  # forward slashes
        try:
            ass_rel = Path(ass_path).relative_to(Path.cwd()).as_posix()
        except Exception:
            ass_rel = ass_path
        ass_filter = ass_rel.replace(":", "\\:").replace("'", "\\'")

        # Use subtitles filter with a safe, quoted path
        cmd = (
            f'ffmpeg -y '
            f'-i "{video.as_posix()}" '
            f'-i "{audio.as_posix()}" '
            f'-filter_complex "[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,'
            f'crop={WIDTH}:{HEIGHT},setpts={speed}*PTS,fps={FPS},subtitles=\'{ass_filter}\'[v];'
            f'[1:a]aresample=44100,volume=1.0[a]" '
            f'-map "[v]" -map "[a]" '
            f'-t {audio_dur} '
            f'-c:v libx264 -preset fast -pix_fmt yuv420p '
            f'-c:a pcm_s16le -ar 44100 -ac 2 '
            f'"{output}"'
        )
        run(cmd)
        ass_file.unlink()
        return output

    # ------------------------------------------------------------------
    # GENERIC VIDEO (stock b-roll or other video visuals)
    # ------------------------------------------------------------------
    if visual.get("type") == "video":
        video = Path(visual.get("path"))
        if not video.exists():
            # If it's a URL-like string, attempt to download it to a temp file
            # (download_image handles HTTP/HTTPS). Otherwise fall back to solid.
            target = Path(f"tmp_broll_{scene_index}.mp4")
            try:
                if download_image(str(visual.get("path")), target):
                    video = target
            except Exception:
                video = Path(visual.get("path"))

        if video.exists():
            speed = audio_dur / get_video_duration(video)
            ass_file = create_ass_subtitle(overlay_text, audio_dur, font_size)
            ass_path = ass_file.as_posix()
            try:
                ass_rel = Path(ass_path).relative_to(Path.cwd()).as_posix()
            except Exception:
                ass_rel = ass_path
            ass_filter = ass_rel.replace(":", "\\:").replace("'", "\\'")
            cmd = (
                f'ffmpeg -y '
                f'-i "{video.as_posix()}" '
                f'-i "{audio.as_posix()}" '
                f'-filter_complex "[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,'
                f'crop={WIDTH}:{HEIGHT},setpts={speed}*PTS,fps={FPS},subtitles=\'{ass_filter}\'[v];'
                f'[1:a]aresample=44100,volume=1.0[a]" '
                f'-map "[v]" -map "[a]" '
                f'-t {audio_dur} '
                f'-c:v libx264 -preset fast -pix_fmt yuv420p '
                f'-c:a pcm_s16le -ar 44100 -ac 2 '
                f'"{output}"'
            )
            run(cmd)
            ass_file.unlink()
            return output

    # ------------------------------------------------------------------
    # PRODUCT HERO (image with zoom + ASS subtitles)
    # ------------------------------------------------------------------
    if visual.get("type") == "image":
        img = prepare_image_source(visual["path"], scene_index)
        if img is None:
            visual = {"type": "solid"}
        else:
            ass_file = create_ass_subtitle(overlay_text, audio_dur, font_size)
            ass_path = ass_file.as_posix()
            try:
                ass_rel = Path(ass_path).relative_to(Path.cwd()).as_posix()
            except Exception:
                ass_rel = ass_path
            ass_filter = ass_rel.replace(":", "\\:").replace("'", "\\'")
            cmd = (
                f'ffmpeg -y '
                f'-f lavfi -i color=c={BRAND_BG}:s={WIDTH}x{HEIGHT}:d={audio_dur}:r={FPS} '
                f'-loop 1 -i "{img.as_posix()}" '
                f'-i "{audio.as_posix()}" '
                f'-filter_complex "'
                f'[1:v]scale={PRODUCT_SCALE}:-1,format=rgba,boxblur={SHADOW_BLUR}:1,'
                f"zoompan=z='1.02+0.0006*on':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',"
                f'eq=contrast=1.05:saturation=0.92[product];'
                f'[0:v][product]overlay=(W-w)/2:(H-h)/2[v];'
                f'[v]subtitles=\'{ass_filter}\'[vsub];'
                f'[2:a]aresample=44100,volume=1.0[a]" '
                f'-map "[vsub]" -map "[a]" '
                f'-t {audio_dur} '
                f'-c:v libx264 -preset fast -pix_fmt yuv420p '
                f'-c:a pcm_s16le -ar 44100 -ac 2 '
                f'"{output}"'
            )
            run(cmd)
            ass_file.unlink()
            return output

    # ------------------------------------------------------------------
    # OUTRO (end credits) – no text
    # ------------------------------------------------------------------
    if scene.get("scene_id") == 9:
        credits = Path("defaults/end_credits.mp4")
        speed = audio_dur / get_video_duration(credits)
        ass_file = create_ass_subtitle(overlay_text, audio_dur, font_size)
        ass_path = ass_file.as_posix()
        try:
            ass_rel = Path(ass_path).relative_to(Path.cwd()).as_posix()
        except Exception:
            ass_rel = ass_path
        ass_filter = ass_rel.replace(":", "\\:").replace("'", "\\'")
        cmd = (
            f'ffmpeg -y '
            f'-i "{credits.as_posix()}" '
            f'-i "{audio.as_posix()}" '
            f'-filter_complex "[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,'
            f'crop={WIDTH}:{HEIGHT},setpts={speed}*PTS,fps={FPS},subtitles=\'{ass_filter}\'[v];'
            f'[1:a]aresample=44100,volume=1.0[a]" '
            f'-map "[v]" -map "[a]" '
            f'-t {audio_dur} '
            f'-c:v libx264 -preset fast -pix_fmt yuv420p '
            f'-c:a pcm_s16le -ar 44100 -ac 2 '
            f'"{output}"'
        )
        run(cmd)
        ass_file.unlink()
        return output

    # ------------------------------------------------------------------
    # FALLBACK (solid colour + ASS subtitles)
    # ------------------------------------------------------------------
    ass_file = create_ass_subtitle(overlay_text, audio_dur, font_size)
    ass_path = ass_file.as_posix()
    try:
        ass_rel = Path(ass_path).relative_to(Path.cwd()).as_posix()
    except Exception:
        ass_rel = ass_path
    ass_filter = ass_rel.replace(":", "\\:").replace("'", "\\'")
    cmd = (
        f'ffmpeg -y '
        f'-f lavfi -i color=c={BRAND_BG}:s={WIDTH}x{HEIGHT}:d={audio_dur}:r={FPS} '
        f'-i "{audio.as_posix()}" '
        f'-filter_complex "[0:v]subtitles=\'{ass_filter}\'[v];[1:a]aresample=44100,volume=1.0[a]" '
        f'-map "[v]" -map "[a]" '
        f'-t {audio_dur} '
        f'-c:v libx264 -pix_fmt yuv420p '
        f'-c:a pcm_s16le -ar 44100 -ac 2 '
        f'"{output}"'
    )
    run(cmd)
    ass_file.unlink()
    return output