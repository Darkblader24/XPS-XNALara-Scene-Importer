
import io
import pathlib

from . import bin_ops
from . import core


class ImportXPS:
    latest_supported_version = (1, 21)
    latest_supported_version_str = '.'.join(str(x) for x in latest_supported_version)

    def __init__(self, filepath):
        self.filepath = filepath
        self.io_stream: io.BytesIO = None

        filepath = pathlib.Path(filepath)
        self.scene = core.SceneConstructor(filepath.stem)

        self.version = (0, 0)

        self._read_file()

    def _read_file(self):
        print(f"\nInfo: Reading file: {self.filepath}")

        print("Info: Getting IO stream..")
        self.io_stream = self._get_io_stream()

        print("Info: Reading file header..")
        self._read_header()

        print("Info: Reading items..")
        self._read_items()

        print("\nInfo: Reading camera..")
        self._read_camera()

        print("\nInfo: Reading lights..")
        self._read_lights()

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
        print(f"Info: Item count: {item_count}")

        # Read items
        for i in range(item_count):
            # Read the item info
            item_type = bin_ops.readString(self.io_stream)
            item_path = bin_ops.readString(self.io_stream)
            print(f"Info: Item {i} type: '{item_type}'")
            print(f"Info: Item {i} path: '{item_path}'")

            # Read the item visibility
            item_visibility = bin_ops.readByte(self.io_stream)
            print(f"Info: Item {i} visibility: {item_visibility}")

            # Read the item scale
            if self.version >= (1, 8):
                item_scale = (bin_ops.readSingle(self.io_stream),
                              bin_ops.readSingle(self.io_stream),
                              bin_ops.readSingle(self.io_stream))
            else:
                scale = bin_ops.readSingle(self.io_stream)
                item_scale = (scale, scale, scale)
            print(f"Info: Item {i} scale: {item_scale}")

            # Skip all the armature stuff
            self.io_stream.read(4)  # Skip one single
            while True:
                name = bin_ops.readString(self.io_stream)
                self.io_stream.read(6 * 4)
                rotation = (bin_ops.readSingle(self.io_stream),
                            bin_ops.readSingle(self.io_stream),
                            bin_ops.readSingle(self.io_stream))
                # print(f"Info: Bone name: '{name}'")
                # print(f"Info: Bone scale: {rotation}")

                # Check if is end of armature
                byte = self.io_stream.read(1)
                self.io_stream.seek(self.io_stream.tell() - 1)  # Go back to the previous byte
                if byte == b'\x00':
                    break

            # Skip all the accessorises
            self.io_stream.read(3 * 4)  # Skip three singles
            accessory_count = bin_ops.readUInt32(self.io_stream)
            for _ in range(accessory_count):
                name = bin_ops.readString(self.io_stream)
                self.io_stream.read(1)  # Skip one byte
                print(f"Info: Accessory name: '{name}'")

            # Skip all secondary accessories
            accessory_count = bin_ops.readUInt16(self.io_stream)
            for _ in range(accessory_count):
                name = bin_ops.readString(self.io_stream)
                self.io_stream.read(1)  # Skip one byte
                print(f"Info: Secondary accessory name: '{name}'")

            # Skip the glow information
            if self.version >= (1, 11):
                for j in range(6):
                    color = bin_ops.readSingle(self.io_stream, round_to=2)
                    print(f"Info: Item {i} glow color {j}: {color}")

            # Add the character to the scene
            self.scene.add_character(item_path, item_scale, item_visibility)

    def _read_camera(self):
        camera_fov = bin_ops.readSingle(self.io_stream)
        print(f"Info: Camera fov: {camera_fov}")

        camera_target = (bin_ops.readSingle(self.io_stream),
                         bin_ops.readSingle(self.io_stream),
                         bin_ops.readSingle(self.io_stream))
        print(f"Info: Camera target: {camera_target}")

        camera_distance = bin_ops.readSingle(self.io_stream)
        print(f"Info: Camera distance: {camera_distance}")

        camera_rotation_horizontal = bin_ops.readSingle(self.io_stream)
        camera_rotation_vertical = bin_ops.readSingle(self.io_stream)
        print(f"Info: Camera rotation: {camera_rotation_horizontal}, {camera_rotation_vertical}")

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
            print(f"Info: Light {i} direction: {light_direction}")

            light_intensity = 1
            if self.version >= (1, 2):
                light_intensity = bin_ops.readSingle(self.io_stream, round_to=2)
            print(f"Info: Light {i} intensity: {light_intensity}")

            light_color = (bin_ops.readByte(self.io_stream),
                           bin_ops.readByte(self.io_stream),
                           bin_ops.readByte(self.io_stream))
            print(f"Info: Light {i} color: {light_color}")

            self.light_shadow_depth = bin_ops.readSingle(self.io_stream, round_to=2)
            print(f"Info: Light {i} shadow depth: {self.light_shadow_depth}")

            self.scene.create_light(i, light_direction, light_intensity, light_color, self.light_shadow_depth)
