import docker

from emustrings import Analysis
from emustrings.celery import celery_app
from emustrings.emulators import load_images

docker_client = docker.from_env()
load_images(docker_client)


@celery_app.task(name="analyze_sample", ignore_result=True)
def analyze_sample(aid):
    docker_client = docker.from_env()
    analysis = Analysis(aid)
    analysis.start(docker_client)
