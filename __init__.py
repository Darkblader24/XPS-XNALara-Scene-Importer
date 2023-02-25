
bl_info = {
    'name': 'XPS/XNALara Scene Importer',
    'category': '3D View',
    'author': 'Hotox',
    'location': 'View 3D > Tool Shelf > XPS',
    'description': 'Import XPS and XNALara scenes',
    'version': (1, 0, 0),
    'blender': (3, 3, 0),
}

first_startup = "bpy" not in locals()
import bpy
import sys

from . import bin_ops
from . import core
from . import import_handler
from . import operators
from . import panels
from . import properties
from . import utils

if not first_startup:
    import importlib
    importlib.reload(bin_ops)
    importlib.reload(core)
    importlib.reload(import_handler)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(properties)
    importlib.reload(utils)


classes = [
    panels.MainPanel,

    operators.ImportXPSButton,
    operators.ImportXPSTestButton,
    operators.SelectInstallDirButton,
    operators.SelectAssetDirButton,
]


def check_unsupported_blender_versions():
    version = (3, 3)
    version_str = ".".join([str(v) for v in version])

    # Don't allow older Blender versions
    if bpy.app.version < version:
        unregister()
        sys.tracebacklimit = 0
        raise ImportError(f'\n\nBlender versions older than {version_str} are not supported by this plugin. '
                          f'\nPlease use Blender {version_str}.'
                          '\n')


def register():
    print("\n#### Loading XPS/XNALara Scene Importer.. ####")

    # Check if Blender version is supported
    check_unsupported_blender_versions()

    # Load all classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except:
            print("Failed to load", cls)

    properties.register()

    # Load settings
    core.SettingsHandler.init()

    print("#### Loaded XPS/XNALara Scene Importer ####\n")


def unregister():
    print("#### Unloading XPS/XNALara Scene Importer.. ####")

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            print("Failed to unload", cls)

    print("#### Unloaded XPS/XNALara Scene Importer ####")


if __name__ == '__main__':
    register()
