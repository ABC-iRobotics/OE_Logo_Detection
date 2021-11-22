import bpy
from math import pi
import random

scene = bpy.context.scene
plane = bpy.data.objects['Plane']
cam = bpy.data.objects['Camera']
oe_logo = bpy.data.objects['OE_logo_3D']

start_frame = 0
end_frame = 0

orig_render_filepath = scene.render.filepath

for frame_num in range(start_frame, end_frame+1, 1):
    cam.location[2] = 0.25 + random.random()*0.25
    cam.rotation_euler = (-0.25 + random.random()*0.5, -0.08 + random.random()*0.16, 0)
    scene.frame_set(frame_num)
    scene.render.filepath = scene.render.frame_path(frame=frame_num)
    for object in bpy.data.objects:
        object.select_set(False)
    plane.select_set(True)
    bpy.ops.object.duplicates_make_real()
    plane.modifiers.get('GeometryNodes').show_viewport=False  # Hide oe logo instances from viewport
    plane.modifiers.get('GeometryNodes').show_render=False # Hide oe logo instances from render
    
    oe_logos = bpy.context.selected_objects
    coll_target = bpy.data.collections['OE_logos']
    for oe_logo in oe_logos:
        for coll in oe_logo.users_collection:
            coll.objects.unlink(oe_logo)
            
            ## Random flip
            if random.random() > 0.5:
                oe_logo.rotation_euler = (pi, 0, 0)
                oe_logo.location[2] += 0.0075
            
            coll_target.objects.link(oe_logo)
    
    bpy.ops.render.render(write_still=True)
    scene.bat_properties.save_annotation = True
    bpy.ops.render.bat_render_annotation()
    scene.bat_properties.save_annotation = False
    
    bpy.ops.object.delete()
            
    plane.modifiers.get('GeometryNodes').show_viewport=True  # Hide oe logo instances from viewport
    plane.modifiers.get('GeometryNodes').show_render=True # Hide oe logo instances from render
    scene.render.filepath = orig_render_filepath