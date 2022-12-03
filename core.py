import bpy
from mathutils import Color
from math import radians
import math

from . import utils


class SceneConstructor:

    def __init__(self, name: str):
        self.name = name

        self.collection = self._create_scene_collection()

    def _create_scene_collection(self):
        # Delete any existing collection with this name
        # collection = bpy.data.collections.get(self.name)
        # if collection:
        #       layer_collection = utils.find_layer_collection(collection)
        #       utils.delete_hierarchy(layer_collection)

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

    def remove(self):
        layer_collection = utils.find_layer_collection(self.collection.name)
        utils.delete_hierarchy(layer_collection)
