from renderer.blender_scene_renderer import render_product_scene

frames_dir = render_product_scene(
    product_image=Path("tmp_product_2.png"),
    duration=audio_duration,
    output_dir=Path("outputs/scene_2_frames")
)
