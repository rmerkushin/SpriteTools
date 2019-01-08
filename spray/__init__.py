import bpy

from .ui import SprayPanel
from .operators import AddIsoCamera, AlignCamera, RenderSprites

bl_info = {
    'name': 'Spray',
    'author': 'Roman Merkushin',
    'location': '3D View > Tools Panel > Spray',
    'version': (0, 1, 0),
    'description': 'Helps to render sprite images',
    'wiki_url': 'https://github.com/rmerkushin/Spray',
    'tracker_url': 'https://github.com/rmerkushin/Spray/issues',
    'support': 'COMMUNITY',
    'category': 'Render'
}


def register():
    bpy.utils.register_class(AddIsoCamera)
    bpy.utils.register_class(AlignCamera)
    bpy.utils.register_class(RenderSprites)
    bpy.utils.register_class(SprayPanel)


def unregister():
    bpy.utils.unregister_module(__name__)
