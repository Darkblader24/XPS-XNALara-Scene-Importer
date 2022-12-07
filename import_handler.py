import binascii
import io
import pathlib

from . import bin_ops
from . import core


class ImportXPS:
    latest_supported_version = (1, 21)
    latest_supported_version_str = '.'.join(str(x) for x in latest_supported_version)

    def __init__(self, filepath, import_models=True, import_lights=True, import_camera=True, import_ground=True, exclude_hidden_models=False):
        self.filepath = filepath
        self.import_models = import_models
        self.import_lights = import_lights
        self.import_camera = import_camera
        self.import_ground = import_ground
        self.exclude_hidden_models = exclude_hidden_models

        self.io_stream: io.BytesIO = None

        filepath = pathlib.Path(filepath)
        self.scene = core.SceneConstructor(filepath.stem)

        self.version = (0, 0)

        self.verbose = True

        self._read_file()

    def _print(self, *text):
        if self.verbose:
            print(*text)

    def _read_file(self):
        print(f"\nInfo: Reading file: {self.filepath}")

        print("Info: Getting IO stream..")
        self.io_stream = self._get_io_stream()

        print("Info: Reading file header..")
        self._read_header()

        print("Info: Reading items..")
        self._read_items()

        self._print()
        print("Info: Reading camera..")
        self._read_camera()

        self._print()
        print("Info: Reading lights..")
        self._read_lights()

        print("Info: Reading post processing..")
        self._read_post_processing()

        print("Info: Reading background..")
        self._read_background()

        print("Info: Reading sky dome..")
        self._read_sky_dome()

        print("Info: Reading window size..")
        self._read_window_size()

    def _get_io_stream(self):
        with open(self.filepath, 'rb') as file:
            io_stream = io.BytesIO(file.read())
        return io_stream

    def _read_header(self):
        # Read version
        version_major = bin_ops.readUInt16(self.io_stream)
        version_minor = bin_ops.readUInt16(self.io_stream)
        self.version = (version_major, version_minor)
        print(f"Info: Version: {self.version}")

        if self.version < self.latest_supported_version:
            raise ValueError(f"Unsupported file version {self.version}. Only file version {self.latest_supported_version_str} and above are supported.")

    def _read_items(self):
        # Read item count
        item_count = bin_ops.readUInt32(self.io_stream)
        self._print(f"Info: Item count: {item_count}")

        # Read items
        for i in range(item_count):
            # Read the item info
            item_name = bin_ops.readString(self.io_stream)
            item_path = bin_ops.readString(self.io_stream)
            self._print(f"Info: Item {i} type: '{item_name}'")
            self._print(f"Info: Item {i} path: '{item_path}'")

            # Read the item visibility
            item_visibility = bin_ops.readByte(self.io_stream)
            self._print(f"Info: Item {i} visibility: {item_visibility}")

            # Read the item scale
            if self.version >= (1, 8):
                item_scale = (bin_ops.readSingle(self.io_stream),
                              bin_ops.readSingle(self.io_stream),
                              bin_ops.readSingle(self.io_stream))
            else:
                scale = bin_ops.readSingle(self.io_stream)
                item_scale = (scale, scale, scale)
            self._print(f"Info: Item {i} scale: {item_scale}")

            # Add the character to the scene
            self.scene.active_armature = None
            if self.import_models:
                if item_visibility or not self.exclude_hidden_models:
                    self.scene.add_character(item_path, item_name, item_visibility)

            # Read the bone data
            bone_count = bin_ops.readUInt32(self.io_stream)
            print(f"Info: Item {i} bone count: {bone_count}")
            for _ in range(bone_count):
                bone_name = bin_ops.readString(self.io_stream)
                rotation = (round(bin_ops.readSingle(self.io_stream), 4),
                            round(bin_ops.readSingle(self.io_stream), 4),
                            round(bin_ops.readSingle(self.io_stream), 4))
                location = (round(bin_ops.readSingle(self.io_stream), 4),
                            round(bin_ops.readSingle(self.io_stream), 4),
                            round(bin_ops.readSingle(self.io_stream), 4))
                scale = (round(bin_ops.readSingle(self.io_stream), 4),
                         round(bin_ops.readSingle(self.io_stream), 4),
                         round(bin_ops.readSingle(self.io_stream), 4))
                # self._print(f"Info: Bone name: '{bone_name}'")
                # self._print(f"Info: Bone rot: {rotation}, loc: {location}, scale: {scale}")

                self.scene.pose_character(bone_name, rotation, location, scale)

            # Read character location
            item_location = (bin_ops.readSingle(self.io_stream),
                             bin_ops.readSingle(self.io_stream),
                             bin_ops.readSingle(self.io_stream))
            self._print(f"Info: Item {i} location: {item_location}")

            # Set character location
            self.scene.transform_character(item_location, item_scale)

            # Skip all the accessorises
            accessory_count = bin_ops.readUInt32(self.io_stream)
            for _ in range(accessory_count):
                name = bin_ops.readString(self.io_stream)
                self.io_stream.read(1)  # Skip one byte
                self._print(f"Info: Accessory name: '{name}'")

            # Skip all secondary accessories
            accessory_count = bin_ops.readUInt16(self.io_stream)
            for _ in range(accessory_count):
                name = bin_ops.readString(self.io_stream)
                self.io_stream.read(1)  # Skip one byte
                self._print(f"Info: Secondary accessory name: '{name}'")

            # Skip the glow information
            if self.version >= (1, 11):
                for j in range(6):
                    color = bin_ops.readSingle(self.io_stream, round_to=2)
                    self._print(f"Info: Item {i} glow color {j}: {color}")

    def _read_camera(self):
        camera_fov = bin_ops.readSingle(self.io_stream)
        self._print(f"Info: Camera fov: {camera_fov}")

        camera_target = (bin_ops.readSingle(self.io_stream),
                         bin_ops.readSingle(self.io_stream),
                         bin_ops.readSingle(self.io_stream))
        self._print(f"Info: Camera target: {camera_target}")

        camera_distance = bin_ops.readSingle(self.io_stream)
        self._print(f"Info: Camera distance: {camera_distance}")

        camera_rotation_horizontal = bin_ops.readSingle(self.io_stream)
        camera_rotation_vertical = bin_ops.readSingle(self.io_stream)
        self._print(f"Info: Camera rotation: {camera_rotation_horizontal}, {camera_rotation_vertical}")

        if self.import_camera:
            self.scene.create_camera(camera_fov, camera_target, camera_distance, camera_rotation_horizontal, camera_rotation_vertical)

    def _read_lights(self):
        self.io_stream.read(4)  # Skip one single
        for i in range(1, 4):
            # Skip one byte if it's not the first light
            if self.version >= (1, 30):
                if i != 1:
                    self.io_stream.read(1)

            light_direction = (bin_ops.readSingle(self.io_stream, round_to=6),
                               bin_ops.readSingle(self.io_stream, round_to=6),
                               bin_ops.readSingle(self.io_stream, round_to=6))
            self._print(f"Info: Light {i} direction: {light_direction}")

            light_intensity = 1
            if self.version >= (1, 2):
                light_intensity = bin_ops.readSingle(self.io_stream, round_to=2)
            self._print(f"Info: Light {i} intensity: {light_intensity}")

            light_color = (bin_ops.readByte(self.io_stream),
                           bin_ops.readByte(self.io_stream),
                           bin_ops.readByte(self.io_stream))
            self._print(f"Info: Light {i} color: {light_color}")

            self.light_shadow_depth = bin_ops.readSingle(self.io_stream, round_to=2)
            self._print(f"Info: Light {i} shadow depth: {self.light_shadow_depth}")

            if self.import_lights:
                self.scene.create_light(i, light_direction, light_intensity, light_color, self.light_shadow_depth)

    def _read_post_processing(self):
        if self.version < (1, 9):
            return

        if self.version > (1, 21):
            use_post_processing = bin_ops.readByte(self.io_stream)
            self._print(f"Info: Use post processing?: {use_post_processing}")

        brightness = bin_ops.readSingle(self.io_stream)
        self._print(f"Info: Brightness: {brightness}")

        gamma = bin_ops.readSingle(self.io_stream)
        self._print(f"Info: Gamma: {gamma}")

        contrast = bin_ops.readSingle(self.io_stream)
        self._print(f"Info: Contrast: {contrast}")

        saturation = bin_ops.readSingle(self.io_stream)
        self._print(f"Info: Saturation: {saturation}")

        self.io_stream.read(1)  # Skip 1 bytes

        if self.version > (1, 21):
            self.io_stream.read(4)  # Skip 4 bytes

    def _read_background(self):
        ground_visibility = bin_ops.readByte(self.io_stream)
        ground_texture_path = bin_ops.readString(self.io_stream)
        self._print(f"Info: Display ground?: {ground_visibility}")
        self._print(f"Info: Ground texture path: {ground_texture_path}")

        if self.import_ground:
            self.scene.create_ground(ground_texture_path, ground_visibility)

        if self.version >= (1, 1):
            background_color = (bin_ops.readByte(self.io_stream),
                                bin_ops.readByte(self.io_stream),
                                bin_ops.readByte(self.io_stream))
            self._print(f"Info: Background color: {background_color}")

        background_texture_path = bin_ops.readString(self.io_stream)
        self._print(f"Info: Background texture path: {background_texture_path}")

        if self.version > (1, 21):
            background_texture_type = bin_ops.readString(self.io_stream)  # Image scale setting: (Fit, Stretch, Crop, Center)
            self._print(f"Info: Background texture type: {background_texture_type}")

            hud_texture_path = bin_ops.readString(self.io_stream)
            self._print(f"Info: HUD texture path: {hud_texture_path}")

    def _read_sky_dome(self):
        if self.version >= (1, 6):
            display_sky_dome = bin_ops.readByte(self.io_stream)
            self._print(f"Info: Display sky dome?: {display_sky_dome}")

            sky_dome_type = bin_ops.readString(self.io_stream)
            self._print(f"Info: Sky dome type: {sky_dome_type}")

            sky_dome_rotation = bin_ops.readSingle(self.io_stream)
            self._print(f"Info: Sky dome rotation: {sky_dome_rotation}")

            sky_dome_elevation = bin_ops.readSingle(self.io_stream)
            self._print(f"Info: Sky dome elevation: {sky_dome_elevation}")

    def _read_window_size(self):
        if self.version >= (1, 7):
            is_maximized = bin_ops.readByte(self.io_stream)
            self.window_width = bin_ops.readUInt32(self.io_stream)
            self.window_height = bin_ops.readUInt32(self.io_stream)
            self._print(f"Info: Is maximized?: {is_maximized}")
            self._print(f"Info: Window size: {self.window_width}x{self.window_height}")

            self.scene.set_camera_resolution(self.window_width, self.window_height)
