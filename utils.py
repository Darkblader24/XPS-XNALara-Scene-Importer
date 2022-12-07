
import os
import bpy
import math
import time
import pathlib
import mathutils
import addon_utils
import numpy as np
from mathutils import Vector, Euler
from threading import Thread
from math import radians

from bpy.types import LayerCollection


main_dir = pathlib.Path(os.path.dirname(__file__))
resources_dir = main_dir / "resources"
settings_file = resources_dir / "settings.json"
if not resources_dir.exists():
    resources_dir.mkdir()


def set_active(obj, select=False, deselect_others=False):
    if deselect_others:
        bpy.ops.object.select_all(action='DESELECT')
    if select:
        set_select(obj, True)

    bpy.context.view_layer.objects.active = obj


def set_select(obj, select):
    obj.select_set(select)


def set_hide(obj, hide, hide_render=None):
    if hide_render is None:
        hide_render = hide

    if obj.hide_get() != hide:
        obj.hide_set(hide)
    if obj.hide_render != hide_render:
        obj.hide_render = hide_render


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


def look_at_2(obj, location, keep_empty=False):
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


def look_at(obj: bpy.types.Object, target: mathutils.Vector):
    """ Rotate the object to look at a target point """
    direction = target - obj.location
    q = direction.to_track_quat("-Z", "Y")

    obj.rotation_euler = q.to_euler()


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


def listdir_r(dirpath: pathlib.Path, depth=0, max_depth=5):
    """lists directories and sub-directories recursively. """
    paths = [dirpath]
    if depth >= max_depth:
        return paths
    for path in dirpath.iterdir():
        if not path.is_dir():
            continue
        rpath = dirpath / path
        subdirs = listdir_r(rpath, depth + 1, max_depth)
        paths.extend(subdirs)
    return paths


def rotate_bone_global(rot):
    # This requires the armature to be in pose mode and the bone to be selected
    # Make sure to select the bone view armature.data.bones
    area = [a for a in bpy.context.screen.areas if a.type == "VIEW_3D"][0]
    with bpy.context.temp_override(area=area):
        bpy.ops.transform.rotate(value=-rot[0], orient_axis="X", orient_type='GLOBAL')
        bpy.ops.transform.rotate(value=-rot[1], orient_axis="Y", orient_type='GLOBAL')
        bpy.ops.transform.rotate(value=-rot[2], orient_axis="Z", orient_type='GLOBAL')


def move_bone_global(bone, loc: Vector):
    # This requires the armature to be in pose mode and the bone to be selected
    # Make sure to select the bone view armature.data.bones

    # Get the current global bone location and add the new location
    bone_global_pos = bone.matrix @ bone.location
    pos_new = bone_global_pos + loc

    # Set the new global location
    bone.location = bone.bone.matrix_local.inverted() @ pos_new


def xps_bone_rotate(bone, rot_delta):
    current_rotation_mode = bone.rotation_mode
    bone.rotation_mode = 'QUATERNION'
    rotation = vector_transform(rot_delta)
    eulerRot = xps_rot_to_euler(rotation)
    origRot = bone.bone.matrix_local.to_quaternion()  # LOCAL EditBone

    rotation = eulerRot.to_quaternion()
    bone.rotation_quaternion = origRot.inverted() @ rotation @ origRot
    bone.rotation_mode = current_rotation_mode


def xps_bone_translate(bone, loc_delta):
    translate = vector_transform_translate(loc_delta)
    origRot = bone.bone.matrix_local.to_quaternion()  # LOCAL EditBone

    bone.location = origRot.inverted() @ translate


def xps_bone_scale(bone, scale):
    newScale = vector_transform_scale(scale)
    bone.scale = newScale


def xps_rot_to_euler(rot_delta):
    xRad = radians(rot_delta.x)
    yRad = radians(rot_delta.y)
    zRad = radians(rot_delta.z)
    return Euler((xRad, yRad, zRad), 'YXZ')


def vector_transform(vec):
    x = vec.x
    y = vec.y
    z = vec.z
    z = -z
    newVec = Vector((x, z, y))
    return newVec


def vector_transform_translate(vec):
    x = vec.x
    y = vec.y
    z = vec.z
    z = -z
    newVec = Vector((x, z, y))
    return newVec


def vector_transform_scale(vec):
    x = vec.x
    y = vec.y
    z = vec.z
    newVec = Vector((x, y, z))
    return newVec


def create_ground_material(image: bpy.types.Image):
    mat = bpy.data.materials.new(name="Ground Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Get existing BSDF node
    bsdf_node = mat.node_tree.nodes["Principled BSDF"]

    # Create image node
    image_node = nodes.new(type="ShaderNodeTexImage")
    image_node.image = image
    image_node.location = (-300, 300)

    # Link image with BSDF
    mat.node_tree.links.new(image_node.outputs["Color"], bsdf_node.inputs["Base Color"])

    return mat


def search_dir_for_file(path: pathlib.Path, file_name: str):
    # Search in the folder for the file name + ".mesh" or ".xps" or ".ascii"
    for file in path.iterdir():
        if file.suffix in [".mesh", ".xps", ".ascii"]:
            if file.stem.lower() == file_name.lower():
                return file

    print(f"Character folder '{path}' does not contain the file {file_name} (.xps, .mesh, .ascii), continuing search..")


def search_dirs_for_model(filepath, filename):
    # Turn windows path into a path independent on os
    filepath_split = filepath.split("\\")

    has_install_dir = bool(bpy.context.scene.xps_importer_install_dir)
    has_asset_dir = bool(bpy.context.scene.xps_importer_asset_dir)

    # Create paths
    folder = pathlib.Path(*filepath_split)
    folder_installation = pathlib.Path(bpy.context.scene.xps_importer_install_dir)
    folder_assets = pathlib.Path(bpy.context.scene.xps_importer_asset_dir)

    print(f"\nStarting search for character '{folder.name}/{filename}.mesh/.xps/.ascii'")

    # Create a list of all the possible folders
    folders = [filepath]
    if has_install_dir:
        folders.append(folder_installation / folder)
    if has_asset_dir and folder_assets.exists():
        # Add all variations of the character path to the asset dir to see if any of give contain the character
        for i in range(len(folder.parts) - 1, -1, -1):
            path = folder_assets / pathlib.Path(*folder.parts[i:])
            if path not in folders:
                folders.append(path)

    # Check each folder for the character folder
    character_folder = None
    mesh_file = None
    for f in folders:
        # print(f"Checking folder '{f}', exists: {os.path.isdir(str(f))}")
        if os.path.isdir(str(f)):
            character_folder = pathlib.Path(str(f))
            mesh_file = search_dir_for_file(character_folder, filename)
            if mesh_file:
                break

    # If the character folder was not found, search the full asset dir for it
    max_folder_depth = 5
    if not character_folder and has_asset_dir and folder_assets.exists():
        # Get all folders in the asset dir
        # TODO: Make this yield the folders instead of creating a list
        folders_all = listdir_r(folder_assets, max_depth=max_folder_depth)
        for f in folders_all:
            # print(f"Checking folder '{f}'")
            if f.name == folder.name:
                # print(f"FOUND!")
                character_folder = f
                mesh_file = search_dir_for_file(character_folder, filename)
                if mesh_file:
                    break

    return character_folder, mesh_file


def run_func_after_blender_startup(func):

    def wait_for_scene_load():
        while True:
            print("Has scene?")
            if hasattr(bpy.context, "scene"):
                print("YES")
                func()
                return
            print("NO")
            time.sleep(0.1)

    thread = Thread(target=wait_for_scene_load, args=[])
    thread.start()


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
