from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from planner.visual_mapper import resolve_visual
from renderer.ffmpeg_scene_renderer import render_scene
from renderer.final_concat import concat_scenes

# Load product
prod_file = Path('data/products/sample_product.json')
product_images = []
product_name = ''
if prod_file.exists():
    p = json.loads(prod_file.read_text())
    product_images = p.get('images', [])
    product_name = p.get('name','')

# Build scene 2 dict (product intro)
scene2 = {
    'scene_id': 2,
    'scene_type': 'product_image',
    'duration': 4,
    'overlay': product_name,
}

visual = resolve_visual(scene2, product_images, 0)
print('Resolved visual for scene 2 ->', visual)

# Render scene 2 (use scene_id as index)
out = render_scene(scene=scene2, scene_index=2, visual=visual, product=None, execute=True)
print('Rendered:', out)

# Re-concatenate all scene_*.mp4 from the module's video_segments folder
video_dir = Path('Video_Generation_Engine/video_segments')
scenes = sorted(list(video_dir.glob('scene_*.mp4')))
print('Found scenes to concat:', [s.name for s in scenes])
final = concat_scenes(scenes)
print('Final video produced at:', final)
