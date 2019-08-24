import os
import logging
import uuid

from typing import List, Tuple, Optional

from docker import DockerClient
from docker.models.containers import Container

from ..language import Language
from ..sample import Sample

LOCAL_EMULATION_PATH = "/app/results/emulation/"


def with_tag(image_name):
    tag = os.getenv("TAG", "latest")
    if ":" in image_name:
        return image_name
    return "{}:{}".format(image_name, tag)


class Emulator(object):
    """
    Docker-based generic emulator module

    SUPPORTED_LANGUAGES - Supported WSH scripting engines (specified in emu.language)
    IMAGE_NAME - Name of emulator image
    DISABLED - Emulator is disabled and won't be loaded
    """
    SUPPORTED_LANGUAGES = []
    IMAGE_NAME = ""
    DISABLED = False

    DEFAULT_SOFT_TIMEOUT = 60
    DEFAULT_HARD_TIMEOUT = 90
    EMULATION_PATH = "/opt/analysis"

    @property
    def workdir(self) -> str:
        """
        Getter for emulator working dir (mounted in container during emulation)
        """
        return os.path.join(LOCAL_EMULATION_PATH, str(self.emuid))

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __init__(self):
        """
        Creates Emulator instance with additional runtime opts

        Supported opts: soft_timeout, hard_timeout
        """
        self.emuid = str(uuid.uuid4())

        self.container: Optional[Container] = None
        self.sample: Optional[Sample] = None

        self.logger = logging.getLogger("{}.{}".format(self.__class__.__module__,
                                                       self.__class__.__name__))

        os.makedirs(self.workdir, exist_ok=True)

    @classmethod
    def supports(cls, language: Language) -> bool:
        """
        Checks whether scripting engine is supported by Emulator
        """
        return language in cls.SUPPORTED_LANGUAGES

    def start(self,
              docker_client: DockerClient,
              sample: Sample,
              options: dict):
        """
        Starts analysis using emulator
        """
        self.sample = sample
        sample.store(self.workdir)

        self.container = docker_client.containers.run(
            self.IMAGE_NAME,
            detach=True,
            dns=['127.0.0.1'],
            dns_search=[],
            network_mode="none",
            environment={
                "SOFT_TIMEOUT": int(options.get("soft_timeout", self.DEFAULT_SOFT_TIMEOUT)),
                "HARD_TIMEOUT": int(options.get("hard_timeout", self.DEFAULT_HARD_TIMEOUT)),
                "SAMPLE": sample.name,
                "LANGUAGE": str(sample.language)
            },
            sysctls={
                "net.ipv4.ip_unprivileged_port_start": "0"
            },
            volumes={
                os.path.abspath(self.workdir): {
                    "bind": self.EMULATION_PATH,
                    "mode": "rw"
                }
            }
        )

    def join(self) -> bool:
        try:
            for log in self.container.logs(stream=True):
                self.logger.info(log)
            return self.container.wait()["StatusCode"] == 0
        finally:
            if self.container is not None:
                self.container.remove()

    def store_results(self, storage):
        for connection in self.connections():
            storage.add_url(connection, "connection")
        for string in self.strings():
            storage.add_string(string)
        for snippet in self.snippets():
            storage.add_snippet(snippet)
        for logfile in self.logfiles():
            storage.add_logfile(self, *logfile)

    def connections(self) -> List[str]:
        """
        Returns list of URLs that script connected with during analysis
        """
        return []

    def strings(self) -> List[str]:
        """
        Returns list of strings found during emulation
        """
        return []

    def snippets(self) -> List[Tuple[str, str]]:
        """
        Returns list of tuples (hash, path) for code snippets
        """
        return []

    def logfiles(self) -> List[Tuple[str, str]]:
        """
        Returns list of tuples (key, path) with log relative paths
        """
        return []
