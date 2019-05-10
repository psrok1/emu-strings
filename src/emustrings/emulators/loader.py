import os

from .boxjs import BoxJSEmulator
from .winedrop import WinedropEmulator


emulators = [
    WinedropEmulator,
    BoxJSEmulator
]


def load_images(docker_client):
    loaded = []
    for image_file in os.listdir("/app/images"):
        if image_file.endswith(".tar"):
            image_path = os.path.join("/app/images", image_file)
            with open(image_path, "rb") as f:
                print("Loading images from {}".format(image_path))
                images = docker_client.images.load(f.read())
                for image in images:
                    loaded += image.tags
    for emulator in emulators:
        if emulator.IMAGE_NAME in loaded:
            print("Loaded {}".format(emulator.__name__))
        else:
            print("Unloaded {}".format(emulator.__name__))
            emulator.SUPPORTED_LANGUAGES = []
