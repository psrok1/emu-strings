from datetime import datetime
import os
import uuid
import hashlib

from pymongo import MongoClient
from config import StorageConfig, MongoConfig


class Analysis(object):
    ENGINE_EXT = {
        "jscript": "js",
        "jscript.encode": "jse",
        "vbscript": "vbs",
        "vbscript.encode": "vbe"
    }

    STATUS_PENDING = 0
    STATUS_SUCCESS = 1
    STATUS_IN_PROGRESS = 2
    STATUS_FAILED = 3
    STATUS_ORPHANED = 255

    @staticmethod
    def db_collection():
        return MongoClient(MongoConfig.DB_URL)[MongoConfig.DB_NAME].analyses

    @property
    def workdir(self):
        return os.path.join(StorageConfig.ANALYSIS_PATH, str(self.aid))

    @property
    def empty(self):
        return self.sample_file is None

    def __init__(self, aid=None):
        self.sample_file = self.engine = None
        self.container = None
        self.status = None
        if aid is None:
            self.aid = uuid.uuid4()
            os.makedirs(self.workdir)
        else:
            self.aid = aid
            if not os.path.isdir(self.workdir):
                raise IOError("Analysis path {} doesn't exist".format(aid))
            try:
                self.sample_file = filter(lambda f: f.startswith("sample"), os.listdir(self.workdir))[0]
                self.engine = {ext: n for n, ext in self.ENGINE_EXT.iteritems()}[self.sample_file.split(".")[-1]]
            except IndexError:
                raise Exception("Analysis {} doesn't contain valid sample file!".format(aid))
        self.set_status(self.STATUS_PENDING)

    def add_sample(self, code, engine):
        if not self.empty:
            raise Exception("Sample is added yet!")
        self.engine = engine.lower()
        if self.engine not in self.ENGINE_EXT:
            raise Exception("Engine {} not supported".format(self.engine))
        self.db_collection().update(
            {"aid": self.aid},
            {
                "md5": hashlib.md5().update(code).hexdigest(),
                "sha1": hashlib.md5().update(code).hexdigest(),
                "sha256": hashlib.sha256().update(code).hexdigest(),
                "sha512": hashlib.sha512().update(code).hexdigest(),
                "engine": engine
            }
        )
        # Add sample to analysis folder
        with open(os.path.join(self.workdir, "sample.{}".format(self.ENGINE_EXT[self.engine])), "wb") as f:
            f.write(code)

    def set_status(self, status):
        self.db_collection().update(
            {"aid": self.aid},
            {
                "status": status,
                "$setOnInsert": {
                    "timestamp": datetime.now(),
                }
            },
            {
                "upsert": True
            }
        )
        self.status = status
