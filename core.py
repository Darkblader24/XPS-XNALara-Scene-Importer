import bpy

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

        # Link object to collection in context
        self.collection.objects.link(light)

        # Rotate light direction from XPS to Blender
        direction = utils.rotate(direction, (90, 0, 0))

        # Set light properties
        light.data.color = color
        light.data.energy = 0.03
        light.data.energy = 10 / 3 * intensity / 100
        # light.data.shadow_soft_size = shadow_depth

        # Apply direction to light by pointing the light at the direction location
        # This is done by creating an empty at the direction location and targeting the light at the empty via the track to constraint
        empty_target = utils.create_empty()
        empty_target.location = direction
        constraint = light.constraints.new(type='TRACK_TO')
        constraint.target = empty_target
        utils.set_active(light)
        bpy.ops.constraint.apply(constraint=constraint.name)
        bpy.data.objects.remove(empty_target, do_unlink=True)

        # Move light above the scene
        light.location[2] = 5

    def remove(self):
        layer_collection = utils.find_layer_collection(self.collection.name)
        utils.delete_hierarchy(layer_collection)
