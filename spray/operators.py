import os
import bpy
from math import radians
from bpy.types import Operator
from bpy_extras.object_utils import world_to_camera_view

from .helpers import get_frames_info

azimuth = {0: 's', 45: 'sw', 90: 'w', 135: 'nw', 180: 'n', 225: 'ne', 270: 'e', 315: 'se'}


class AddIsoCamera(Operator):

    bl_idname = 'spray.add_iso_camera'
    bl_label = 'Add Isometric Camera'
    bl_description = 'Add Isometric Camera to scene'

    def execute(self, context):
        # delete isometric camera if exists
        for obj in bpy.data.objects:
            if obj.name in ('_Camera', 'IsoCamera'):
                obj.select = True
            else:
                obj.select = False
        bpy.ops.object.delete()
        # add isometric camera
        bpy.ops.object.camera_add(
            location=(10, -10, 10),
            rotation=(radians(60), 0, radians(45))
        )
        camera = context.object
        camera.name = '_Camera'
        camera.data.type = 'ORTHO'
        # add camera path
        bpy.ops.curve.primitive_bezier_circle_add(
            location=(0, 0, 10)
        )
        camera_path = context.object
        camera_path.data.path_duration = 1
        camera_path.scale = (14, 14, 1)
        # assign path to camera
        camera.select = True
        camera_path.select = True
        context.scene.objects.active = camera_path
        bpy.ops.object.parent_set(type='FOLLOW')
        # set camera name and add to scene
        iso_camera = context.object
        iso_camera.name = 'IsoCamera'
        context.scene.camera = camera
        # set render output settings
        context.scene.render.resolution_x = 300
        context.scene.render.resolution_y = 300
        context.scene.render.resolution_percentage = 100
        context.scene.render.alpha_mode = 'TRANSPARENT'
        context.scene.render.image_settings.file_format = 'PNG'
        context.scene.render.image_settings.color_mode = 'RGBA'
        context.scene.render.image_settings.compression = 100
        # debug info
        self.report({'INFO'}, 'Isometric camera has been created!')
        return {'FINISHED'}


class AlignCamera(Operator):

    bl_idname = 'spray.align_iso_camera'
    bl_label = 'Align To Target'
    bl_description = 'Align Isometric Camera to fit target object'

    @classmethod
    def poll(cls, context):
        target = bpy.data.objects.get(context.scene.camera_target, None)
        return target is not None

    def execute(self, context):
        target = bpy.data.objects[context.scene.camera_target]
        camera = bpy.data.objects['_Camera']
        iso_camera = bpy.data.objects['IsoCamera']
        frame_start, frame_end, frame_count = get_frames_info()
        # select only target object
        for obj in bpy.data.objects:
            obj.select = False
        target.select = True
        # align camera
        locations = []
        scales = []
        for angle in range(0, 360, 45):
            for frame in range(1, frame_count + 1):
                bpy.ops.view3d.camera_to_view_selected()
                bpy.context.scene.frame_current = frame + frame_start - 1
                iso_camera.rotation_euler.z = radians(angle)
                x, y, z = camera.location
                locations.append((x, y, z))
                scales.append(camera.data.ortho_scale)
        average_location = [0.0, 0.0, 0.0]
        for location in locations:
            average_location[0] += location[0]
            average_location[1] += location[1]
            average_location[2] += location[2]
        average_location = [l / len(locations) for l in average_location]
        camera.location = average_location
        x_locations = [l[0] for l in locations]
        camera.data.ortho_scale = max(scales) + max(x_locations) / 2
        # set camera direction to selected value
        direction = int(context.scene.camera_direction)
        iso_camera.rotation_euler.z = radians(direction)
        # debug info
        self.report({'INFO'}, 'Isometric camera has been aligned to {}!'.format(target.name))
        return {'FINISHED'}


class RenderSprites(Operator):

    bl_idname = 'spray.render_sprites'
    bl_label = 'Render Sprites'
    bl_description = 'Render sprites to output directory'

    @classmethod
    def poll(cls, context):
        path = context.scene.output_path
        prefix = context.scene.output_prefix
        target = bpy.data.objects.get(context.scene.camera_target, None)
        return path and os.path.isdir(path) and prefix and target is not None

    def execute(self, context):
        target = bpy.data.objects[context.scene.camera_target]
        scene = bpy.context.scene
        render_scale = scene.render.resolution_percentage / 100
        resolution_x = scene.render.resolution_x
        resolution_y = scene.render.resolution_y
        camera = bpy.data.objects['_Camera']
        frame_start, frame_end, frame_count = get_frames_info()
        iso_camera = bpy.data.objects['IsoCamera']
        path = context.scene.output_path
        prefix = context.scene.output_prefix
        # render sprites to png files
        for angle in range(0, 360, 45):
            for frame in range(1, frame_count + 1):
                frame_index = format(frame, '02d')
                bpy.context.scene.frame_current = frame + frame_start - 1
                direction = azimuth[angle]
                iso_camera.rotation_euler.z = radians(angle)
                file_name = '{}_{}_{}.png'.format(prefix, direction, frame_index)
                context.scene.render.filepath = os.path.join(path, file_name)
                bpy.ops.render.render(write_still=True)
        # set camera direction to selected value
        direction = int(context.scene.camera_direction)
        iso_camera.rotation_euler.z = radians(direction)
        # write sprites info
        with open(os.path.join(path, 'info.txt'), mode='w', encoding='utf_8') as out:
            camera_coords = world_to_camera_view(scene, camera, target.location)
            pivot = (round(camera_coords[0] * resolution_x * render_scale),
                     round(camera_coords[1] * resolution_y * render_scale))
            out.write('sprite.count = {}\n'.format(8 * frame_count))
            out.write('sprite.width = {}\n'.format(resolution_x))
            out.write('sprite.height = {}\n'.format(resolution_y))
            out.write('sprite.pivot.x = {}\n'.format(pivot[0]))
            out.write('sprite.pivot.y = {}\n'.format(pivot[1]))
        # debug info
        self.report({'INFO'}, 'Sprites has been rendered!')
        return {'FINISHED'}
