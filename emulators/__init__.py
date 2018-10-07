import hashlib
import os
import pkgutil
import uuid

import engines

from config import StorageConfig
from emulators.analysis import Analysis


class Emulator(object):
    """
    Docker-based generic emulator module

    SUPPORTED_ENGINES - Supported WSH scripting engines (specified in emulators.engines)
    IMAGE_NAME - Name of emulator image

    Instances of this class should be created only in Celery context (daemon.py)
    """
    SUPPORTED_ENGINES = []
    IMAGE_NAME = ""

    @property
    def workdir(self):
        """
        Getter for emulator working dir (mounted in container during emulation)
        """
        return os.path.join(StorageConfig.EMULATION_PATH, str(self.emuid))

    def __init__(self, code, engine, **opts):
        """
        Creates Emulator instance with additional runtime opts

        Supported opts: soft_timeout, hard_timeout
        """
        self.engine = engines.Engine.get(engine)
        if not self.is_supported(self.engine):
            raise Exception("Engine {} is not supported by {} emulator".format(self.engine, self.__class__.__name__))
        self.container = None

        self.emuid = str(uuid.uuid4())
        os.makedirs(self.workdir)

        sha256 = hashlib.sha256(code).hexdigest()
        self.sample_file = "{}.{}".format(sha256, self.engine.EXTENSION)
        # Add sample to emulation folder
        with open(os.path.join(self.workdir, self.sample_file), "wb") as f:
            f.write(code)

        self.env = {
            "SOFT_TIMEOUT": opts.get("soft_timeout", 60.0),
            "HARD_TIMEOUT": opts.get("hard_timeout", 90.0),
            "SAMPLE": self.sample_file,
            "ENGINE": str(self.engine)
        }

    @classmethod
    def is_supported(cls, engine):
        """
        Checks whether scripting engine is supported by Emulator
        :param engine: Engine object, identifier or extension
        """
        return engine in cls.SUPPORTED_ENGINES

    def start(self, docker_client):
        """
        Starts analysis using emulator
        """
        self.container = docker_client.containers.run(
            self.IMAGE_NAME,
            detach=True,
            dns=['127.0.0.1'],
            network_mode="none",
            environment=self.env,
            volumes={
                os.path.abspath(self.workdir): {
                    "bind": "/opt/analysis",
                    "mode": "rw"
                }
            }
        )

    def join(self):
        try:
            for log in self.container.logs(stream=True):
                print log
            return self.container.wait()["StatusCode"] == 0
        finally:
            if self.container is not None:
                self.container.remove()

    def strings(self):
        """
        Returns list of strings found during emulation
        """
        return []

    def snippets(self):
        """
        Returns list of tuples (hash, path) for code snippets
        """
        return []

# Preloading all plugin submodules
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)
    exec('%s = module' % module_name)


def get_emulators(engine_name):
    return [emucls for emucls in Emulator.__subclasses__() if emucls.is_supported(engine_name)]
