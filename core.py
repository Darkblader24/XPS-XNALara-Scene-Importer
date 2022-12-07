

import bpy
import math
import json
import copy
import time
import os.path
import pathlib
from math import radians, degrees
from mathutils import Color, Matrix, Euler, Vector
from threading import Thread
from bpy.app.handlers import persistent

from . import utils


class SceneConstructor:

    def __init__(self, name: str):
        self.name = name
        self.error_handler: ErrorHandler = ErrorHandler()

        self.collection, self.layer_collection, self.scene_controller = self._create_scene_collection()
        self.can_import_characters = utils.check_for_xps_importer()

        self.active_armature = None

    def _create_scene_collection(self):
        collection = bpy.data.collections.new(self.name)
        bpy.context.scene.collection.children.link(collection)

        layer_collection = utils.find_layer_collection(collection.name)

        scene_controller = utils.create_empty(link_collection=collection)
        scene_controller.name = "Scene Controller"
        return collection, layer_collection, scene_controller

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
            light.data.energy = intensity * 2.4
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
        
        # More camera settings
        bpy.context.scene.render.resolution_percentage = 200

        # Set this camera to active
        bpy.context.scene.camera = camera

    def add_character(self, file_directory, file_name, visibility):
        self.active_armature = None
        if not self.can_import_characters:
            self.error_handler.add_error("XPS Importer not installed, skipping character import.")
            return

        # Search for the model directory in the install and asset folders
        character_folder, mesh_file = utils.search_dirs_for_model(file_directory, file_name)

        if not character_folder or not character_folder.exists():
            folder_name = file_directory.split("\\")[-1]
            self.error_handler.add_error(f"Model '{folder_name}' was not found in any selected folder. Full original path: '{file_directory}'")
            return
        if not mesh_file:
            self.error_handler.add_error(f"Could not find any folder '{character_folder.name}' containing the file '{file_name}' (.xps, .mesh, .ascii).")
            return

        filepath_full = character_folder / mesh_file
        print(f"\nImporting character {str(filepath_full)}...")

        # Set the active collection to this XPS scene collection
        bpy.context.view_layer.active_layer_collection = self.layer_collection

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
            self.error_handler.add_error(f"Imported character '{filepath_full}' collection not found, skipping character import.")
            return

        # Hide all objects in the collection if they should be hidden
        for obj in character_collection.objects:
            utils.set_hide(obj, not visibility)

        # Get the armature from the collection and set it as active
        for obj in character_collection.objects:
            if obj.type == "ARMATURE":
                self.active_armature = obj
                self.active_armature.parent = self.scene_controller
                self.active_armature.name = character_folder.parts[-1]
                utils.set_hide(self.active_armature, True)
                break
        if not self.active_armature:
            self.error_handler.add_error(f"Character collection '{character_collection.name}' does not contain an armature, skipping character pose.")
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
            # print(f"Armature '{self.active_armature.name}' does not contain bone '{bone_name}', skipping bone pose.")
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

    def set_camera_resolution(self, width, height):
        if height > 10000 or width > 10000:
            self.error_handler.add_error(f"Camera resolution is too big (>10000), likely due to incorrect reading of the scene file."
                                         f"\n    Please report this in our Github repository and attach this scene file.")
            return
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height

    def create_ground(self, texture_path, visibility):
        # Problem is that the scene always contains "data/ground.png" as the texture path, but it doesn't exist as a file
        # XNALara probably defaults to the importing the floor mesh from data/Floor/Floor/Generic_Item.mesh
        # Therefore we just import this by default

        filepath = "data\\Floor\\Floor"
        self.add_character(filepath, "generic_item", visibility)
        plane_armature = self.active_armature
        if not plane_armature:
            self.error_handler.remove_error_containing_str(f"'{filepath}'")
            self.error_handler.add_error(f"Could not find ground model, probably due to an unknown XPS installation folder.")
            return

        for obj in plane_armature.children:
            if obj.type != "MESH":
                continue
            mat = obj.data.materials[0]
            mat.shadow_method = 'NONE'


class ErrorHandler:
    def __init__(self):
        self.errors = []

    def add_error(self, error):
        if error not in self.errors:
            self.errors.append(error)
        print(error)

    def get_error_message(self):
        error_msg = "Errors while importing scene:\n"
        for error in self.errors:
            error_msg += f"- {error}\n"

        print(error_msg)
        return error_msg
    
    def has_errors(self):
        return len(self.errors) > 0
    
    def remove_error_containing_str(self, containing_str):
        [self.errors.remove(error) for error in self.errors if containing_str in error]


class SettingsHandler:
    structure = {
        "xps_importer_install_dir": "",
        "xps_importer_asset_dir": "",
    }

    @staticmethod
    def init():
        # Add the load_settings function to the load_post handler in order to apply the settings as soon as a new file gets loaded
        bpy.app.handlers.load_post.append(SettingsHandler.load_settings)

    @staticmethod
    def save_settings():
        settings = copy.deepcopy(SettingsHandler.structure)
        for key in settings.keys():
            settings[key] = getattr(bpy.context.scene, key)
        with open(utils.settings_file, "w") as f:
            json.dump(settings, f, indent=4)

    @staticmethod
    @persistent
    def load_settings(arg1=None, arg2=None):
        if not utils.settings_file.exists():
            return
        with open(utils.settings_file, "r") as f:
            settings = json.load(f)
        for key, value in settings.items():
            if not value:
                return
            setattr(bpy.context.scene, key, value)

