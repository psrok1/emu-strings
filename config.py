class CeleryConfig(object):
    BROKER_URL = 'redis://localhost/0'
    CELERY_ACCEPT_CONTENT = ['json']


class MongoConfig(object):
    DB_URL = "mongodb://localhost:27017/"
    DB_NAME = "winedrop"


class StorageConfig(object):
    ANALYSIS_PATH = "./analysis/"

