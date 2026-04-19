import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parents[1]))

from renderer.ffmpeg_scene_renderer import render_scene
from planner.visual_mapper import resolve_visual

# Load product images from sample product
prod_file = Path('data/products/sample_product.json')
product_images = []
if prod_file.exists():
    product_images = json.loads(prod_file.read_text()).get('images', [])

scenes = [
    {'scene_id': 3, 'scene_type': 'review_text', 'duration': 3, 'overlay': f"⭐ 4.6+ Rated"},
    {'scene_id': 5, 'scene_type': 'blue_bg_bullets', 'duration': 5, 'overlay': 'High quality protein'},
]

out_dir = Path('video_segments_rerender')
out_dir.mkdir(parents=True, exist_ok=True)

for scene in scenes:
    idx = scene['scene_id']
    visual = resolve_visual(scene, product_images, 0)
    print('Rendering scene', idx, 'visual:', visual)
    out = render_scene(scene=scene, scene_index=idx, visual=visual, product=None, execute=True)
    target = out_dir / f"scene_{idx}.mp4"
    Path(out).replace(target)
    print('Wrote', target)
