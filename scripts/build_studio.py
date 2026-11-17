import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/studio_source.blend'))
s=bpy.context.scene
for o in s.objects:
 if o.type not in ['CAMERA','LIGHT'] and o.name!='Floor':o.hide_render=True
s.cycles.samples=32;s.render.filepath=str(R/'assets/studio.png')
bpy.ops.render.render(write_still=True)
