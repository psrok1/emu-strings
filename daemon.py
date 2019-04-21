import celery
import docker

from config import CeleryConfig

from emulators.analysis import Analysis

celery_app = celery.Celery()
celery_app.config_from_object(CeleryConfig)

docker_client = docker.from_env()


@celery_app.task(ignore_result=True)
def analyze_sample(aid, opts):
    analysis = Analysis(aid)
    analysis.start(docker_client, opts)
