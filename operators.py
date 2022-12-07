import pathlib

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from . import import_handler
from . import utils, core


class ImportXPSButton(Operator, ImportHelper):
    bl_idname = "xps_importer.import_xps"
    bl_label = "Import XPS"
    bl_description = "Imports an XPS scene file"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    filter_glob: bpy.props.StringProperty(default="*.scene", options={'HIDDEN'})

    import_models: bpy.props.BoolProperty(
        name="Import Models",
        description="Import characters and objects from the XPS file",
        default=True,
    )
    import_lights: bpy.props.BoolProperty(
        name="Import Lights",
        description="Import lights from the XPS file",
        default=True,
    )
    import_camera: bpy.props.BoolProperty(
        name="Import Camera",
        description="Import camera from the XPS file",
        default=True,
    )
    import_ground: bpy.props.BoolProperty(
        name="Import Ground",
        description="Import ground from the XPS file",
        default=True,
    )
    exclude_hidden_models: bpy.props.BoolProperty(
        name="Exclude Hidden Models",
        description="Excludes characters and objects that are hidden in the XPS file",
        default=True,
    )

    def execute(self, context):
        filepath = self.filepath
        print("\nInfo: Importing XPS file: " + filepath)
        if not filepath.lower().endswith(".scene"):
            self.report({"ERROR"}, "Please select a .scene file!")
            return {'CANCELLED'}

        try:
            importer = import_handler.ImportXPS(filepath, self.import_models, self.import_lights, self.import_camera, self.import_ground, self.exclude_hidden_models)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {'CANCELLED'}

        if importer.scene.error_handler.has_errors():
            self.report({"ERROR"}, importer.scene.error_handler.get_error_message())
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
        if filepath.is_file() or not filepath.exists():
            filepath = filepath.parent
        context.scene.xps_importer_install_dir = str(filepath.absolute())
        core.SettingsHandler.save_settings()
        utils.update_viewport()
        return {'FINISHED'}


class SelectAssetDirButton(Operator, ImportHelper):
    bl_idname = "xps_importer.select_asset_dir"
    bl_label = "Select XNALara Asset Directory"
    bl_description = "Select the folder containing all of your XPS assets." \
                     "\nThis directory will be searched for any missing assets"

    def execute(self, context):
        filepath = pathlib.Path(self.filepath)
        if filepath.is_file() or not filepath.exists():
            filepath = filepath.parent
        context.scene.xps_importer_asset_dir = str(filepath.absolute())
        core.SettingsHandler.save_settings()
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
        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\lara_scene.scene", import_models=True)
        self.report({'INFO'}, f"Small test successful!")
        # return {'FINISHED'}






        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\lara_scene.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.4 or io_handler.window_height != 700:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\3lamptest_NOSCOTT.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.9 or io_handler.window_height != 1358:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        # Test all documented scene files
        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights1only.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1331:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights2only.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1331:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights3only.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1331:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights4only.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1331:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lights5only.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1331:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        # Test all documented scene files with characters
        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest1.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1297:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest2.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1297:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest3.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1297:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest4.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1297:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Test Files\\lighttest5.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.85 or io_handler.window_height != 1297:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\Lighting-Setting-XPS-2.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 1.0 or io_handler.window_height != 972:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        io_handler = import_handler.ImportXPS("E:\\Work\\judgearts - XPS Importer\\background_test.scene", import_models=False)
        if round(io_handler.light_shadow_depth, 2) != 0.4 or io_handler.window_height != 700:
            self.report({'ERROR'}, f"Error importing XPS file {io_handler.filepath}")
            return {'CANCELLED'}
        io_handler.scene.remove()

        self.report({'INFO'}, f"All tests ran successfully!")
        return {'FINISHED'}
