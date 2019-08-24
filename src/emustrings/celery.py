import celery


class CeleryConfig(object):
    BROKER_URL = 'redis://redis/0'
    CELERY_ACCEPT_CONTENT = ['json']


celery_app = celery.Celery()
celery_app.config_from_object(CeleryConfig)
