import pkgutil

import docker

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

    def __init__(self, anal, **opts):
        """
        Creates Emulator instance with bound Analysis and additional runtime opts

        Supported opts: soft_timeout, hard_timeout
        """
        self.analysis = anal
        self.env = {
            "SOFT_TIMEOUT": opts.get("soft_timeout", 60),
            "HARD_TIMEOUT": opts.get("hard_timeout", 90),
            "SAMPLE": anal.sample_file,
            "ENGINE": str(anal.engine)
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
        container = None
        try:
            container = docker_client.containers.run(
                self.IMAGE_NAME,
                detach=True,
                dns=['127.0.0.1'],
                network_mode="none",
                environment=self.env,
                volumes={
                    self.analysis.workdir: {
                        "bind": "/root/analysis",
                        "mode": "rw"
                    }
                }
            )
            self.analysis.set_status(Analysis.STATUS_IN_PROGRESS)
            if container.wait()["StatusCode"] == 0:
                self.analysis.set_status(Analysis.STATUS_SUCCESS)
                self._report()
            else:
                self.analysis.set_status(Analysis.STATUS_FAILED)
        except Exception as e:
            if analysis:
                self.analysis.set_status(Analysis.STATUS_FAILED)
            raise e
        finally:
            if container is not None:
                container.remove()

    def _report(self):
        """
        Creates file with summary information from emulator-dependent artifacts.
        Called by Emulator.start()
        """
        return

# Preloading all plugin submodules
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)
    exec('%s = module' % module_name)


def get_emulator_class(emulator_name):
    emulator_class = {emucls.__name__: emucls for emucls in Emulator.__subclasses__()}.get(emulator_name)
    if emulator_class is None:
        raise Exception("Emulator {} not installed".format(emulator_name))
    return emulator_class


def get_capabilities():
    return {emucls.__name__: map(str, emucls.SUPPORTED_ENGINES) for emucls in Emulator.__subclasses__()}
