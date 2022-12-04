import pathlib

import bpy
from mathutils import Color, Matrix, Euler, Vector
from math import radians, degrees
import math

from . import utils


class SceneConstructor:

    def __init__(self, name: str):
        self.name = name

        self.collection, self.scene_controller = self._create_scene_collection()
        self.can_import_characters = utils.check_for_xps_importer()

        self.active_armature = None

    def _create_scene_collection(self):
        collection = bpy.data.collections.new(self.name)
        bpy.context.scene.collection.children.link(collection)

        scene_controller = utils.create_empty(link_collection=collection)
        scene_controller.name = "Scene Controller"
        return collection, scene_controller

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

            empty.parent = self.scene_controller

    def create_camera(self, fov, target_pos, distance, rotation_horizontal, rotation_vertical):
        # Create camera object
        camera_data = bpy.data.cameras.new(name="Camera")
        camera = bpy.data.objects.new(name="Camera", object_data=camera_data)
        self.collection.objects.link(camera)

        # Create camera controller
        camera_controller = utils.create_empty(link_collection=self.collection)
        camera_controller.name = "Camera Controller"
        camera.parent = camera_controller
        camera_controller.parent = self.scene_controller

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

    def add_character(self, file_directory, visibility):
        self.active_armature = None
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

        print(f"\nStarting search for character folder '{folder.name}'")

        # Check each folder for the character folder
        character_folder = None
        for f in folders:
            print(f"Checking folder '{f}', exists: {f.exists()}")
            if f.exists():
                character_folder = f
                break

        # If the character folder was not found, search the full asset dir for it
        max_folder_depth = 5
        if not character_folder and folder_assets.exists():
            # Get all folders in the asset dir
            # TODO: Make this yield the folders instead of creating a list
            folders_all = utils.listdir_r(pathlib.Path(bpy.context.scene.xps_importer_asset_dir), max_depth=max_folder_depth)
            for f in folders_all:
                print(f"Checking folder '{f}'")
                if f.name == folder.name:
                    print(f"FOUND!")
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
        print(f"\nImporting character {str(filepath_full)}...")

        # Save all current collections to check witch one was added
        collections_pre = [c for c in bpy.data.collections]

        # Import the character from the given path
        bpy.ops.xps_tools.import_model(
            "EXEC_DEFAULT",
            filepath=str(filepath_full),
        )
        print(f"Imported character {str(filepath_full)}...\n")

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

        # Set the visibility of the character
        character_collection.hide_viewport = not visibility
        character_collection.hide_render = not visibility

        # Get the armature from the collection and set it as active
        for obj in character_collection.objects:
            if obj.type == "ARMATURE":
                self.active_armature = obj
                self.active_armature.parent = self.scene_controller
                self.active_armature.name = character_folder.parts[-1]
                break
        if not self.active_armature:
            print(f"Character collection '{character_collection.name}' does not contain an armature, skipping character pose.")
            return

        # Move all objects from the character-collection to this xps scene collection
        for obj in character_collection.objects:
            self.collection.objects.link(obj)
            character_collection.objects.unlink(obj)

        # Delete the character collection
        bpy.data.collections.remove(character_collection, do_unlink=True)

    def pose_character(self, bone_name, rot, loc, scale):
        if not self.active_armature:
            return

        # Get the bone
        bone = self.active_armature.pose.bones.get(bone_name)
        if not bone:
            print(f"Armature '{self.active_armature.name}' does not contain bone '{bone_name}', skipping bone pose.")
            return

        # Posing bone
        if rot[0] or rot[1] or rot[2]:
            utils.xps_bone_rotate(bone, Vector(rot))

        if loc[0] or loc[1] or loc[2]:
            utils.xps_bone_translate(bone, Vector(loc))

        if scale[0] != 1 or scale[1] != 1 or scale[2] != 1:
            # TODO: This is absolutely not like the XPS behavior, but it's somewhat close
            utils.xps_bone_scale(bone, Vector(scale))

    def transform_character(self, location, scale):
        if not self.active_armature:
            return
        x, y, z = location
        self.active_armature.location = (x, -z, y)
        x, y, z = scale
        self.active_armature.scale = (x, z, y)

    def remove(self):
        layer_collection = utils.find_layer_collection(self.collection.name)
        utils.delete_hierarchy(layer_collection)
