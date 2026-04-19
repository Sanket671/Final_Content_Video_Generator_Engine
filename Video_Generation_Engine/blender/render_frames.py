import bpy
import sys
import os

# -------- Read arguments --------
args = sys.argv
args = args[args.index("--") + 1:]

product_image = args[0]
duration = float(args[1])
output_dir = args[2]

fps = 24
frames = int(duration * fps)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.fps = fps

scene.frame_start = 1
scene.frame_end = frames

# -------- Load product image --------
img = bpy.data.images.load(product_image)

product = bpy.data.objects.get("Product")
mat = product.active_material
nodes = mat.node_tree.nodes
nodes["Image Texture"].image = img

# -------- Subtle camera move --------
cam = bpy.data.objects["Camera"]
cam.location.y -= 0.2
cam.keyframe_insert(data_path="location", frame=1)
cam.location.y += 0.2
cam.keyframe_insert(data_path="location", frame=frames)

# -------- Output --------
scene.render.filepath = os.path.join(output_dir, "")
bpy.ops.render.render(animation=True)
