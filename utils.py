
import bpy
import math
import mathutils
import addon_utils
import numpy as np

from bpy.types import LayerCollection


def set_active(obj, select=False, deselect_others=False):
    if deselect_others:
        bpy.ops.object.select_all(action='DESELECT')
    if select:
        set_select(obj, True)

    bpy.context.view_layer.objects.active = obj


def set_select(obj, select):
    obj.select_set(select)


def set_hide(obj, hide):
    # obj.hide_viewport = hide
    obj.hide_set(hide)


# Recursively transverse layer_collection for a particular name
def find_layer_collection(name: str, layer_collection=None):
    if layer_collection is None:
        layer_collection = bpy.context.view_layer.layer_collection

    if layer_collection.name == name:
        return layer_collection

    for layer in layer_collection.children:
        found = find_layer_collection(name, layer)
        if found:
            return found
    return None


def delete_hierarchy(layer_collection: LayerCollection):
    for obj in layer_collection.collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    for child in layer_collection.children:
        delete_hierarchy(child)

    bpy.data.collections.remove(layer_collection.collection, do_unlink=True)


def create_empty(link_collection=None):
    if not link_collection:
        link_collection = bpy.context.scene.collection
    empty = bpy.data.objects.new(name="Empty", object_data=None)
    link_collection.objects.link(empty)
    return empty


def look_at(obj, location, keep_empty=False):
    # Create an empty at the location and targeting the object at the empty via the track to constraint
    empty_target = create_empty()
    empty_target.location = location
    constraint = obj.constraints.new(type='TRACK_TO')
    constraint.target = empty_target
    set_active(obj)
    bpy.ops.constraint.apply(constraint=constraint.name)
    if not keep_empty:
        bpy.data.objects.remove(empty_target, do_unlink=True)
        return empty_target


def rotate(vector, rot):
    vector = np.asarray(vector)
    rot = np.asarray(rot)
    rot = np.radians(rot)
    x, y, z = rot

    Rx = np.array(([
        [1, 0, 0],
        [0, math.cos(x), -math.sin(x)],
        [0, math.sin(x), math.cos(x)]
    ]))
    Ry = np.array(([
        [math.cos(y), 0, math.sin(y)],
        [0, 1, 0],
        [-math.sin(y), 0, math.cos(y)]
    ]))
    Rz = np.array(([
        [math.cos(z), -math.sin(z), 0],
        [math.sin(z), math.cos(z), 0],
        [0, 0, 1]
    ]))

    return Rx @ Ry @ Rz @ vector


def check_for_xps_importer():
    # then enable correct version
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "XNALara/XPS Import/Export":
            # if mod.bl_info['version'] < (2, 0, 2):
            #     continue
            if not addon_utils.check(mod.__name__)[0]:
                bpy.ops.preferences.addon_enable(module=mod.__name__)
            return True
    return False


def update_viewport():
    try:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    except:
        pass


# def cartesian_to_spherical(x, y, z):
#     r = (x**2 + y**2 + z**2)**0.5
#     theta = math.acos(z / r)
#     phi = math.atan2(y, x)
#     return r, theta, phi
#
#
# def spherical_to_euler(theta, phi):
#     x = 0
#     y = theta
#     z = phi
#     return x, y, z
#
#
# def rotate_vector_euler(vector, euler_angles):
#     # Convert euler angles to quaternion
#     q = mathutils.Euler(euler_angles).to_quaternion()
#
#     # Rotate vector
#     vector = q @ vector
#
#     return vector