class CeleryConfig(object):
    BROKER_URL = 'redis://redis/0'
    CELERY_ACCEPT_CONTENT = ['json']


class MongoConfig(object):
    DB_URL = "mongodb://mongo:27017/"
    DB_NAME = "winedrop"


class StorageConfig(object):
    ANALYSIS_PATH = "/app/results/analysis/"
    EMULATION_PATH = "/app/results/emulation/"
