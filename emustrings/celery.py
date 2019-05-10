import celery

from config import CeleryConfig

celery_app = celery.Celery()
celery_app.config_from_object(CeleryConfig)
