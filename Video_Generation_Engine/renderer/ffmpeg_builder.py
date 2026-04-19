def build_ffmpeg_command(images):
    return f"ffmpeg -loop 1 -i {images[0]} -t 30 output.mp4"
