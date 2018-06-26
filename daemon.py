import celery
import docker

from libs.analysis import Analysis

celery_app = celery.Celery()
#@todo
#celery_app.config_from_object(CeleryConfig)

docker_client = docker.from_env()

IMAGE_NAME = "winedrop"
DEFAULT_SOFT_TIMEOUT = 30
DEFAULT_HARD_TIMEOUT = 60


@celery_app.task(ignore_result=True)
def analyze_sample(analysis_id, opts):
    container = None
    analysis = None
    try:
        analysis = Analysis(analysis_id)
        container = docker_client.containers.run(
            IMAGE_NAME,
            detach=True,
            dns=['127.0.0.1'],
            network_mode="none",
            environment={
                "SOFT_TIMEOUT": opts.get("soft_timeout", DEFAULT_SOFT_TIMEOUT),
                "HARD_TIMEOUT": opts.get("hard_timeout", DEFAULT_HARD_TIMEOUT)
            },
            volumes={
                analysis.workdir: {
                    "bind": "/root/analysis",
                    "mode": "rw"
                }
            }
        )
        analysis.set_status(Analysis.STATUS_IN_PROGRESS)
        if container.wait()["StatusCode"] == 0:
            analysis.set_status(Analysis.STATUS_SUCCESS)
        else:
            analysis.set_status(Analysis.STATUS_FAILED)
    except Exception as e:
        if analysis:
            analysis.set_status(Analysis.STATUS_FAILED)
        raise e
    finally:
        if container is not None:
            container.remove()
