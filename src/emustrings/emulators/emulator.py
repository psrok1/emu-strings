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

    def __init__(self, analysis):
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

        self.sample_name = "{}.{}".format(self.analysis.sample.sha256, self.analysis.language.extension)
        # Add sample to emulation folder
        self.analysis.sample.store(os.path.join(self.workdir, self.sample_name))

        self.env = {
            "SOFT_TIMEOUT": int(self.analysis.options.get("soft_timeout", 60)),
            "HARD_TIMEOUT": int(self.analysis.options.get("hard_timeout", 90)),
            "SAMPLE": self.sample_name,
            "LANGUAGE": str(self.analysis.language)
        }

    @classmethod
    def is_supported(cls, language):
        """
        Checks whether scripting engine is supported by Emulator
        """
        print("{} - {} {}: {}".format(cls.__name__, language, list(map(str,cls.SUPPORTED_LANGUAGES)),
                                      language in cls.SUPPORTED_LANGUAGES))
        return language in cls.SUPPORTED_LANGUAGES

    def start(self, docker_client):
        """
        Starts analysis using emulator
        """
        self.container = docker_client.containers.run(
            self.IMAGE_NAME,
            detach=True,
            dns=['127.0.0.1'],
            dns_search=[],
            network_mode="none",
            environment=self.env,
            sysctls={
                "net.ipv4.ip_unprivileged_port_start": "0"
            },
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

    def connections(self):
        """
        Returns list of URLs that script connected with during analysis
        """
        return []

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
