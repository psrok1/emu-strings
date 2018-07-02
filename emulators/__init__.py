import docker

from emulators.analysis import Analysis


class Emulator(object):
    SUPPORTED_ENGINES = []
    IMAGE_NAME = ""

    def __init__(self, anal, **opts):
        self.analysis = anal
        if not self.is_supported(anal.engine):
            raise Exception("{} is not supported by {} emulator".format(anal.engine, self.__class__.__name__))
        self.env = {
            "SOFT_TIMEOUT": opts.get("soft_timeout", 60),
            "HARD_TIMEOUT": opts.get("hard_timeout", 90)
        }
        self.docker_client = docker.from_env()

    def is_supported(self, engine):
        return engine in self.SUPPORTED_ENGINES

    def start(self):
        container = None
        try:
            container = self.docker_client.containers.run(
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
        return
