
import bpy
from bpy.types import Scene, Object, LayerCollection, Collection, PropertyGroup
from bpy.props import IntProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty, PointerProperty, FloatProperty


def register():
    Scene.xps_importer_install_dir = StringProperty(
        name="XNALara Install Directory",
        description="XNALara installation folder containing the 'XNALara XPS.exe' file and the 'data' folder",
        default="",
    )
    Scene.xps_importer_asset_dir = StringProperty(
        name="Asset Directory",
        description="The folder containing all of your XPS assets. This folder will be searched for any missing assets",
        default="",
    )




