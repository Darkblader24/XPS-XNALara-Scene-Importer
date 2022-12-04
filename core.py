import pathlib

import bpy
from mathutils import Color, Matrix, Euler
from math import radians, degrees
import math

from . import utils


class SceneConstructor:

    def __init__(self, name: str):
        self.name = name

        self.collection = self._create_scene_collection()
        self.can_import_characters = utils.check_for_xps_importer()

    def _create_scene_collection(self):
        collection = bpy.data.collections.new(self.name)
        bpy.context.scene.collection.children.link(collection)
        return collection

    def create_light(self, index, direction, intensity, color, shadow_depth):
        # Set name
        name = f"Light {index}"

        # Create light
        light_data = bpy.data.lights.new(name=name, type='SUN')
        light = bpy.data.objects.new(name=name, object_data=light_data)
        self.collection.objects.link(light)

        # Rotate light direction from XPS to Blender
        direction = utils.rotate(direction, (90, 0, 0))

        sun = False

        if sun:
            # Set light properties
            light.data.color = color
            light.data.energy = 0.03
            light.data.energy = 10 / 3 * intensity / 100

            # Apply direction to light by pointing the light at the direction location
            utils.look_at(light, direction)

            # Move light above the scene
            light.location[2] = 5

        # Setup lights as point lights
        else:
            c = Color(color)
            c.s += 0.1

            light.data.type = "POINT"
            light.location = -direction * 3
            light.data.energy = intensity * 1.5
            light.data.color = c
            light.data.shadow_soft_size = 2
            light.data.use_contact_shadow = True
            light.data.contact_shadow_thickness = 0.005

            # Create empty at the center so the light can be easily rotated
            empty = utils.create_empty(link_collection=self.collection)
            empty.location[2] += 1
            empty.name = f"{light.name} Controller"
            light.parent = empty

    def create_camera(self, fov, target_pos, distance, rotation_horizontal, rotation_vertical):
        # Create camera object
        camera_data = bpy.data.cameras.new(name="Camera")
        camera = bpy.data.objects.new(name="Camera", object_data=camera_data)
        self.collection.objects.link(camera)

        # Create camera controller
        camera_controller = utils.create_empty(link_collection=self.collection)
        camera_controller.name = "Camera Controller"
        camera.parent = camera_controller

        # Move camera to the correct distance
        camera.location[2] = distance

        # Make camera look at the empty
        utils.look_at(camera, camera_controller.location)

        # Rotate target location from XPS space to Blender space
        target_pos = utils.rotate(target_pos, (90, 0, 0))

        # Move the controller to the target location
        camera_controller.location = target_pos

        # Rotate controller by the rotation values
        camera_controller.rotation_euler = (radians(90) - rotation_vertical, 0, rotation_horizontal)

        # Calculate the field of view angle
        angle_unit = 0.0872664600610733 / 5
        camera_angle = int(fov / angle_unit)

        # Calculate focal length from angle
        focal_length = camera.data.sensor_width / 2 / math.tan(radians(camera_angle) / 2)

        # Apply the focal length
        camera.data.lens = focal_length

        # Set this camera to active
        bpy.context.scene.camera = camera

    def add_character(self, file_directory, scale, visibility):
        if not self.can_import_characters:
            print("XPS Importer not installed, skipping character import.")
            return
        # Create paths
        folder = pathlib.Path(file_directory)
        folder_installation = pathlib.Path(bpy.context.scene.xps_importer_install_dir)
        folder_assets = pathlib.Path(bpy.context.scene.xps_importer_install_dir)

        # Create a list of all the possible folders
        folders = [folder,
                   folder_installation / folder]
        if folder_assets.exists():
            # Add all variations of the character path to the asset dir to see if any of give contain the character
            for i in range(len(folder.parts) - 1, -1, -1):
                path = bpy.context.scene.xps_importer_asset_dir / pathlib.Path(*folder.parts[i:])
                if path not in folders:
                    folders.append(path)

        # Check each folder for the character folder
        character_folder = None
        for f in folders:
            if f.exists():
                character_folder = f
                break
        
        # If the character folder was not found, search the full asset dir for it
        max_folder_depth = 5
        if not character_folder and folder_assets.exists():
            character_folder_name = folder.parts[-1]

            # Get all folders in the asset dir
            # TODO: Make this yield the folders instead of creating a list
            folders_all = utils.listdir_r(pathlib.Path(bpy.context.scene.xps_importer_asset_dir), max_depth=5)
            for f in folders_all:
                if f.name == character_folder_name:
                    character_folder = f
                    break

        if not character_folder or not character_folder.exists():
            print(f"Character folder '{file_directory}' does not exist and was not found in any selected directory, skipping character import.")
            return

        # Search in the folder for a .mesh file
        mesh_file = None
        for file in character_folder.iterdir():
            if file.suffix in [".mesh", ".xps", ".ascii"]:
                mesh_file = file
                break
        if not mesh_file:
            print(f"Character folder '{character_folder}' does not contain a character file (.xps, .mesh, .ascii), skipping character import.")
            return

        filepath_full = character_folder / mesh_file
        print(f"Importing character {str(filepath_full)}...")

        # Save all current collections to check witch one was added
        collections_pre = [c for c in bpy.data.collections]

        # Import the character from the given path
        bpy.ops.xps_tools.import_model(
            "EXEC_DEFAULT",
            filepath=str(filepath_full),
        )

        # Get the added collection
        character_collection = None
        for c in bpy.data.collections:
            if c not in collections_pre:
                character_collection = c
                break
        if not character_collection:
            print(f"Imported character '{filepath_full}' collection not found, skipping character import.")
            return

        # Move the character collection into the scene collection
        self.collection.children.link(character_collection)
        bpy.context.scene.collection.children.unlink(character_collection)
        
        # Scale the character
        for obj in character_collection.objects:
            obj.scale = scale

        # Set the visibility of the character
        character_collection.hide_viewport = not visibility
        character_collection.hide_render = not visibility

        return character_collection

    def pose_character(self, char_collection, bone_name, rot, loc, scale):
        return
        # Get the armature
        armature = None
        for obj in char_collection.objects:
            if obj.type == "ARMATURE":
                armature = obj
                break
        if not armature:
            print(f"Character collection '{char_collection.name}' does not contain an armature, skipping character pose.")
            return

        # Get the bone
        bone = armature.pose.bones.get(bone_name)
        if not bone:
            print(f"Character collection '{char_collection.name}' does not contain bone '{bone_name}', skipping character pose.")
            return

        if not rot[0] and not rot[1] and not rot[2]:
            return

        print(f"Pose character {char_collection.name} bone {bone_name} rot {rot} loc {loc} scale {scale}")

        # Calc new rotation from XPS to Blender space
        rot = utils.rotate((radians(rot[0]), radians(rot[1]), radians(rot[2])), (90, 0, 0))
        rot_in_degrees = (degrees(rot[0]), degrees(rot[1]), degrees(rot[2]))

        # Set the bone rotation
        bone.rotation_mode = 'XYZ'
        # bone.rotation_euler = (radians(rot[0]), radians(rot[1]), radians(rot[2]))

        #
        # print("GLOBAL EULER", bone.matrix.to_euler())
        #
        # loc = bone.matrix.to_translation()
        #
        # # Rotation only (strip location and scale)
        # rot_euler = bone.matrix.to_euler()
        # rot_euler_rotated = Euler(utils.rotate((rot_euler.x, rot_euler.y, rot_euler.z), rot_in_degrees))
        # rot = rot_euler_rotated.to_matrix().to_4x4()
        #
        # s = bone.matrix.to_scale()
        # scale = Matrix()
        # scale[0][0] = s[0]
        # scale[1][1] = s[1]
        # scale[2][2] = s[2]
        #
        # mat = loc * rot * scale
        #
        # bone.matrix = mat

        # Enter pose mode
        utils.set_active(armature, select=True, deselect_others=True)
        bpy.ops.object.mode_set(mode='POSE')

        # Select the bone
        bone.select = True

        # Rotate
        bpy.ops.transform.rotate(value=0.785398, orient_axis="Y", orient_type='GLOBAL')

    def remove(self):
        layer_collection = utils.find_layer_collection(self.collection.name)
        utils.delete_hierarchy(layer_collection)
