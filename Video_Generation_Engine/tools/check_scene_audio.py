import subprocess
from pathlib import Path
import re

VIDEO_DIR = Path('Video_Generation_Engine/video_segments')
if not VIDEO_DIR.exists():
    print('Video segments directory missing:', VIDEO_DIR)
    raise SystemExit(1)

pattern_mean = re.compile(r'mean_volume:\s*([-0-9.]+)\s*dB')
pattern_max = re.compile(r'max_volume:\s*([-0-9.]+)\s*dB')

files = sorted(VIDEO_DIR.glob('scene_*.mp4'))
if not files:
    print('No scene files found in', VIDEO_DIR)
    raise SystemExit(0)

for f in files:
    print('==', f)
    # Run volumedetect
    cmd = ['ffmpeg', '-hide_banner', '-i', str(f), '-af', 'volumedetect', '-f', 'null', '-']
    p = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    stderr = p.stderr
    mean = pattern_mean.search(stderr)
    maxv = pattern_max.search(stderr)
    print('volumedetect mean:', mean.group(1) + ' dB' if mean else 'N/A')
    print('volumedetect max :', maxv.group(1) + ' dB' if maxv else 'N/A')

    # Get ffprobe stream info
    cmd2 = ['ffprobe', '-v', 'error', '-show_entries', 'stream=index,codec_type,codec_name,channels', '-of', 'json', str(f)]
    p2 = subprocess.run(cmd2, capture_output=True, text=True)
    print('ffprobe streams:')
    print(p2.stdout)
    print()

# Also run on final video
final = Path('Video_Generation_Engine/outputs/youtube_shorts/final_video.mp4')
if final.exists():
    print('==', final)
    cmd = ['ffmpeg', '-hide_banner', '-i', str(final), '-af', 'volumedetect', '-f', 'null', '-']
    p = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    stderr = p.stderr
    mean = pattern_mean.search(stderr)
    maxv = pattern_max.search(stderr)
    print('volumedetect mean:', mean.group(1) + ' dB' if mean else 'N/A')
    print('volumedetect max :', maxv.group(1) + ' dB' if maxv else 'N/A')

    cmd2 = ['ffprobe', '-v', 'error', '-show_entries', 'stream=index,codec_type,codec_name,channels', '-of', 'json', str(final)]
    p2 = subprocess.run(cmd2, capture_output=True, text=True)
    print('ffprobe streams:')
    print(p2.stdout)
else:
    print('Final video not found:', final)
