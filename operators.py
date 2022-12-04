import pathlib

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from . import import_handler
from . import utils


class ImportXPSButton(Operator, ImportHelper):
    bl_idname = "xps_importer.import_xps"
    bl_label = "Import XPS"
    bl_description = "Imports an XPS scene file"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        filepath = self.filepath
        print("\nInfo: Importing XPS file: " + filepath)
        if not filepath.lower().endswith(".scene"):
            self.report({"ERROR"}, "Please select a .scene file!")
            return {'CANCELLED'}

        try:
            import_handler.ImportXPS(filepath)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, f"Imported XPS file {filepath}")
        return {'FINISHED'}


class SelectInstallDirButton(Operator, ImportHelper):
    bl_idname = "xps_importer.select_install_dir"
    bl_label = "Select XNALara Installation Directory"
    bl_description = "Select the XNALara installation folder containing the 'XNALara XPS.exe' file and the 'data' folder." \
                     "\nThis will be used for character imports placed in this directory"

    def execute(self, context):
        filepath = pathlib.Path(self.filepath)
        context.scene.xps_importer_install_dir = str(filepath.parent.absolute())
        utils.update_viewport()
        return {'FINISHED'}


class SelectAssetDirButton(Operator, ImportHelper):
    bl_idname = "xps_importer.select_asset_dir"
    bl_label = "Select XNALara Asset Directory"
    bl_description = "Select the folder containing all of your XPS assets." \
                     "\nThis directory will be searched for any missing assets"

    def execute(self, context):
        filepath = pathlib.Path(self.filepath)
        context.scene.xps_importer_asset_dir = str(filepath.parent.absolute())
        utils.update_viewport()
        return {'FINISHED'}


class ImportXPSTestButton(Operator):
    bl_idname = "xps_importer.import_xps_test"
    bl_label = "Dev Test Button"
    bl_description = "Does lots of dev magic"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        test_path = pathlib.Path("E:\\Work\\judgearts - XPS Importer\\lara_scene.scene")
        if not test_path.exists():
            self.report({"ERROR"}, "Ey, you are not the dev! Don't touch this button!")
            return {'CANCELLED'}

        # Custom test scene
        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\pose_test.scene")
        self.report({'INFO'}, f"Small test successful!")
        return {'FINISHED'}

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\lara_scene.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.4:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\3lamptest_NOSCOTT.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.9:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        # Test all documented scene files
        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights1only.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights2only.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights3only.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights4only.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights5only.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        # Test all documented scene files with characters
        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest1.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest2.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest3.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest4.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest5.scene")
        if round(io_handler.light_shadow_depth, 2) != 0.85:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Lighting-Setting-XPS-2.scene")
        if round(io_handler.light_shadow_depth, 2) != 1.0:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        self.report({'INFO'}, f"All tests ran successfully!")
        return {'FINISHED'}
