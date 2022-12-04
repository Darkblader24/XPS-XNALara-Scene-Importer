
import bpy
from . import operators as ops


# Initializes the main panel in the toolbar
class Panel(object):
    bl_label = 'XPS'
    bl_idname = 'VIEW3D_TS_xps_scene_importer'
    bl_category = 'XPS'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class MainPanel(Panel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_xps_importer_main'
    bl_label = 'XPS Scene Importer'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        # XPS install directory
        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text="XPS Install Dir:")
        row = layout.row(align=True)
        row.prop(context.scene, "xps_importer_install_dir", text="")
        row.operator(ops.SelectInstallDirButton.bl_idname, text="", icon="FILE_FOLDER")

        # XPS install directory
        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text="XPS Asset Dir:")
        row = layout.row(align=True)
        row.prop(context.scene, "xps_importer_asset_dir", text="")
        row.operator(ops.SelectAssetDirButton.bl_idname, text="", icon="FILE_FOLDER")

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.6
        row.operator(ops.ImportXPSButton.bl_idname, icon="IMPORT")

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.1
        row.operator(ops.ImportXPSTestButton.bl_idname, icon="IMPORT")


