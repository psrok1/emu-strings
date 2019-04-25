import os
import uuid

from config import StorageConfig


class Emulator(object):
    """
    Docker-based generic emulator module

    SUPPORTED_LANGUAGES - Supported WSH scripting engines (specified in emu.language)
    IMAGE_NAME - Name of emulator image

    Instances of this class should be created only in Celery context (daemon.py)
    """
    SUPPORTED_LANGUAGES = []
    IMAGE_NAME = ""

    @property
    def workdir(self):
        """
        Getter for emulator working dir (mounted in container during emulation)
        """
        return os.path.join(StorageConfig.EMULATION_PATH, str(self.emuid))

    @property
    def name(self):
        return self.__class__.__name__

    def __init__(self, analysis, **opts):
        """
        Creates Emulator instance with additional runtime opts

        Supported opts: soft_timeout, hard_timeout
        """
        self.analysis = analysis
        if not self.is_supported(self.analysis.language):
            raise ValueError("Language {} is not supported by {} emulator".format(
                self.analysis.language, self.__class__.__name__))
        self.container = None

        self.emuid = str(uuid.uuid4())
        os.makedirs(self.workdir)

        self.sample_name = "{}.{}".format(self.analysis.sample.sha256, self.analysis.language.EXTENSION)
        # Add sample to emulation folder
        self.analysis.sample.store(os.path.join(self.workdir, self.sample_name))

        self.env = {
            "SOFT_TIMEOUT": opts.get("soft_timeout", 60.0),
            "HARD_TIMEOUT": opts.get("hard_timeout", 90.0),
            "SAMPLE": self.sample_name,
            "LANGUAGE": str(self.analysis.language)
        }

    @classmethod
    def is_supported(cls, engine):
        """
        Checks whether scripting engine is supported by Emulator
        :param engine: Engine object, identifier or extension
        """
        return engine in cls.SUPPORTED_LANGUAGES

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
                print(log)
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

    def logfiles(self):
        """
        Returns list of tuples (key, path) with log relative paths
        """
        return []
