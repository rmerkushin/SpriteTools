import bpy
from math import radians
from bpy.types import Panel
from bpy.props import StringProperty, EnumProperty


class SprayPanel(Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Spray'
    bl_label = 'Spray'
    bl_context = 'objectmode'

    @classmethod
    def register(cls):
        directions = (
            ('0', 'South', ''),
            ('45', 'Southwest', ''),
            ('90', 'West', ''),
            ('135', 'Northwest', ''),
            ('180', 'North', ''),
            ('225', 'Northeast', ''),
            ('270', 'East', ''),
            ('315', 'Southeast', '')
        )
        bpy.types.Scene.camera_direction = EnumProperty(
            items=directions,
            name='Direction',
            update=cls.update_direction
        )
        bpy.types.Scene.camera_target = StringProperty(
            name='Target',
            description='Target object for camera alignment'
        )
        bpy.types.Scene.output_prefix = StringProperty(
            name='Prefix',
            description='Prefix for sprite name',
            default='sprite',
            maxlen=32
        )
        bpy.types.Scene.output_path = StringProperty(
            name='Path',
            description='Path to render output',
            default='',
            subtype='DIR_PATH'
        )

    def update_direction(self, context):
        direction = int(context.scene.camera_direction)
        iso_camera = bpy.data.objects['IsoCamera']
        iso_camera.rotation_euler.z = radians(direction)

    def draw(self, context):
        self.layout.operator('spray.add_iso_camera', icon='RENDER_STILL')
        if 'IsoCamera' in bpy.data.objects:
            # Camera
            box = self.layout.row().box()
            row = box.row()
            row.label(text='Camera', icon='CAMERA_DATA')
            row = box.row()
            row.prop(context.scene, 'camera_direction')
            camera = bpy.data.objects['_Camera']
            row = box.row()
            row.prop(camera, 'location', index=2, text='Height:')
            row = box.row()
            row.prop(camera.data, 'ortho_scale', 'Orthographic Scale:')
            row = box.row()
            row.prop(context.scene, 'camera_target')
            row = box.row()
            row.operator('spray.align_iso_camera', icon='BBOX')
            # Output
            box = self.layout.row().box()
            row = box.row()
            row.label(text='Output', icon='IMAGE_DATA')
            row = box.row()
            row.label(text='Resolution:')
            split = row.split()
            column = split.column(align=True)
            render = context.scene.render
            column.prop(render, 'resolution_x', index=0, text='X:')
            column.prop(render, 'resolution_y', index=1, text='Y:')
            row = box.row()
            row.prop(context.scene, 'output_prefix')
            row = box.row()
            row.prop(context.scene, 'output_path')
            row = box.row()
            row.operator('spray.render_sprites', text='Render Sprites', icon='RENDER_ANIMATION')
