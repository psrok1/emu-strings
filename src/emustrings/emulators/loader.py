import logging
import os

from typing import Type, List, Iterator, cast

from docker import DockerClient
import docker.errors

from .emulator import Emulator
from ..language import Language

logger = logging.getLogger(__name__)

IMAGES_PATH = "/app/images"
LOADED_EMULATORS: List[Type[Emulator]] = []


def _preload_images(docker_client: DockerClient):
    """
    Load images stored in IMAGES_PATH into Docker server
    :param docker_client: Docker client instance
    """
    for image_file in os.listdir(IMAGES_PATH):
        if image_file.endswith(".tar"):
            image_path = os.path.join(IMAGES_PATH, image_file)
            with open(image_path, "rb") as f:
                images = docker_client.images.load(f.read())
                for image in images:
                    logger.info("%s loaded from %s", image.tags, image_file)


def load_emulators(docker_client: DockerClient):
    """
    Load images for emulators
    :param docker_client: Docker client instance
    :param emulators: Available emulators
    :return: Emulators for which the image was loaded
    """
    import importlib
    import pkgutil

    global LOADED_EMULATORS

    for loader, name, is_pkg in pkgutil.walk_packages([os.path.dirname(__file__)],
                                                      '.'.join(__name__.split(".")[:-1]) + "."):
        if not is_pkg:
            continue
        try:
            importlib.import_module(name)
            logger.info("Loaded subpackage %s", name)
        except Exception:
            logger.exception("Error during import %s", name)

    emulators = cast(List[Type[Emulator]], Emulator.__subclasses__())

    if not docker_client.images.list():
        logger.info("No images found on server - preloading from %s", IMAGES_PATH)
        _preload_images(docker_client)

    for emulator in emulators:
        if emulator.DISABLED:
            logger.info("%s is disabled and won't be loaded", emulator.__name__)
            continue
        try:
            # Check whether image is loaded on server
            docker_client.images.get(emulator.IMAGE_NAME)
            logger.info("%s required by %s found on server",
                        emulator.IMAGE_NAME,
                        emulator.__name__)
        except docker.errors.ImageNotFound:
            try:
                # Pull image if not loaded
                logger.info("%s not loaded - pulling from registry", emulator.IMAGE_NAME)
                docker_client.images.pull(emulator.IMAGE_NAME)
                logger.info("%s pulled successfully", emulator.IMAGE_NAME)
            except docker.errors.NotFound:
                logger.warning("Can't load %s: image %s not found in registry",
                               emulator.__name__,
                               emulator.IMAGE_NAME)
                # Don't load emulator
                continue
        # Emulator is ready
        LOADED_EMULATORS.append(emulator)

    if not LOADED_EMULATORS:
        raise RuntimeError("No emulators found.")


def get_emulators(language: Language) -> Iterator[Type[Emulator]]:
    """
    Get emulators for specified language
    :param language: Script language
    """
    for emulator in LOADED_EMULATORS:
        if emulator.supports(language):
            yield emulator
