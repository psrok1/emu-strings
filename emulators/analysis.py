from datetime import datetime
import os
import uuid
import hashlib

from pymongo import MongoClient

import emulators

from emulators import engines
from config import StorageConfig, MongoConfig


class Analysis(object):
    """
    Analysis instance
    """
    STATUS_PENDING = 0
    STATUS_SUCCESS = 1
    STATUS_IN_PROGRESS = 2
    STATUS_FAILED = 3
    STATUS_ORPHANED = 255

    @staticmethod
    def db_collection():
        """
        Returns MongoDB collection for analysis objects
        """
        return MongoClient(MongoConfig.DB_URL)[MongoConfig.DB_NAME].analyses

    @property
    def workdir(self):
        """
        Getter for analysis working dir (mounted in container during emulation)
        """
        return os.path.join(StorageConfig.ANALYSIS_PATH, str(self.aid))

    @property
    def empty(self):
        """
        Is sample file bound with analysis yet?
        """
        return self.sample_file is None

    def __init__(self, aid=None):
        """
        Creates new analysis (with unique id) or gets instance of existing one
        """
        self.sample_file = self.engine = self.emulator_class = None
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
                params = self.db_collection().find_one({"aid": aid})
                self.status = params["status"]
                self.engine = engines.Engine.get(params["engine"])
                self.sample_file = "{}.{}".format(params["sha256"], self.engine.EXTENSION)
                if "emulator" in params:
                    self.emulator_class = emulators.get_emulator_class(params["emulator"])
            except IndexError:
                raise Exception("Analysis {} doesn't contain valid sample file!".format(aid))

    def add_sample(self, code, engine, filename=None):
        """
        Adds sample to analysis workdir
        """
        if not self.empty:
            raise Exception("Sample is added yet!")
        self.engine = engine
        params = {
            "md5": hashlib.md5().update(code).hexdigest(),
            "sha1": hashlib.md5().update(code).hexdigest(),
            "sha256": hashlib.sha256().update(code).hexdigest(),
            "sha512": hashlib.sha512().update(code).hexdigest(),
            "engine": str(engine),
            "status": self.STATUS_PENDING,
            "$setOnInsert": {
                "timestamp": datetime.now(),
            }
        }
        self.sample_file = "{}.{}".format(params["sha256"], engine.EXTENSION)
        params["filename"] = filename or self.sample_file
        self.db_collection().update({"aid": self.aid}, params, {"upsert": True})
        # Add sample to analysis folder
        with open(os.path.join(self.workdir, self.sample_file), "wb") as f:
            f.write(code)

    def bind_emulator(self, emulator):
        """
        Binds emulator class with current analysis context (sample must have been added before).
        """
        if self.empty:
            raise Exception("Sample is not added yet!")
        emulator_cls = emulators.get_emulator_class(emulator)
        if not emulator_cls.is_supported(self.engine):
            raise Exception("{} is not supported by {} emulator".format(str(self.engine),
                                                                        emulator_cls.__name__))

        self.emulator_class = emulator_cls

        params = {
            "emulator": emulator_cls.__name__
        }
        self.db_collection().update({"aid": self.aid}, params)

    def set_status(self, status):
        """
        Sets analysis status
        """
        self.db_collection().update({"aid": self.aid}, {"status": status})
        self.status = status
