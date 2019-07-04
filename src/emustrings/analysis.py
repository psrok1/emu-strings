import os
import uuid

from datetime import datetime

from bson.objectid import ObjectId
from pymongo import MongoClient

from config import StorageConfig, MongoConfig

from .emulators import get_emulators
from .language import Language, JScript
from .results import ResultsStore
from .sample import Sample


class Analysis(object):
    """
    Analysis instance
    """
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_ORPHANED = "orphaned"

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
        return self.sample is None

    def __init__(self, aid=None):
        """
        Creates new analysis (with unique id) or gets instance of existing one
        """
        self.sample = self.language = None
        self.options = None
        self.status = None

        """
        Create new instance
        """
        if aid is None:
            self.aid = str(uuid.uuid4())
            os.makedirs(self.workdir)
            self.results = ResultsStore(self.workdir)
            self.db_collection().insert({
                "aid": self.aid,
                "status": self.STATUS_PENDING,
                "timestamp": datetime.now()
            })
            return

        """
        Load existing instance
        """

        self.aid = aid

        if not os.path.isdir(self.workdir):
            raise IOError("Analysis path {} doesn't exist".format(aid))

        try:
            params = self.db_collection().find_one({"aid": aid})
            self.status = params["status"]
            self.timestamp = params["timestamp"]
            self.language = Language.get(params["language"])
            self.options = params.get("options", {})
            sample_path = os.path.join(self.workdir, "{}.{}".format(params["sha256"], self.language.extension))
            self.sample = Sample.load(sample_path)
        except IndexError as e:
            raise IOError("Analysis {} is corrupted!".format(aid)) from e

        self.results = ResultsStore(self.workdir)
        self.results.load(params)

    @staticmethod
    def find_analysis(sample):
        entry = Analysis.db_collection().find_one({
            "sha256": sample.sha256
        })
        return entry and Analysis(aid=entry["aid"])

    @staticmethod
    def get_analysis(aid):
        entry = Analysis.db_collection().find_one({
            "aid": aid})
        return entry and Analysis(aid=aid)

    @staticmethod
    def list_analyses(last_id=None, limit=7):
        last_id_query = {"_id": {"$lt": ObjectId(last_id)}} if last_id else {}
        entries = list(Analysis.db_collection().find(
            last_id_query,
            {"filename": 1, "sha256": 1, "aid": 1, "_id": 1, "timestamp": 1,
             "status": 1, "language": 1, "options": 1}
        ).sort("_id", -1).limit(limit))
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        return entries

    def add_sample(self, sample: Sample, language=None, options=None):
        """
        Adds sample to analysis workdir
        """
        if not self.empty:
            raise Exception("Sample is added yet!")

        language = language or Language.detect(sample) or JScript
        self.sample = sample
        self.language = language
        self.options = options or {}
        params = {
            "$set": {
                "md5": sample.md5,
                "sha256": sample.sha256,
                "language": str(language),
                "filename": sample.name,
                "options": self.options
            }
        }
        self.db_collection().update({"aid": self.aid}, params)
        self.sample.store(os.path.join(self.workdir, sample.sha256) + "." + self.language.extension)

    def set_status(self, status, exc=None):
        """
        Sets analysis status
        """
        params = {"status": status}
        if exc:
            params["exc"] = exc
        self.db_collection().update({"aid": self.aid},
                                    {"$set": params})
        self.status = status

    def start(self, docker_client):
        if self.empty:
            raise RuntimeError("Sample must be added before analysis start")

        self.set_status(Analysis.STATUS_IN_PROGRESS)

        try:
            emus = get_emulators(self)
            print("Found {} emulators".format(len(emus)))
            for emu in emus:
                print("Started in {}".format(emu.name))
                emu.start(docker_client)

            for emu in emus:
                emu.join()
                self.results.process(emu)

            self.db_collection().update({"aid": self.aid},
                                        {"$set": self.results.store()})
            self.set_status(Analysis.STATUS_SUCCESS)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.set_status(Analysis.STATUS_FAILED, traceback.format_exc())

    def to_dict(self):
        return {
            "sample": self.sample.to_dict(),
            "status": self.status,
            "timestamp": self.timestamp,
            "language": str(self.language),
            "results": self.results.store(),
            "options": self.options
        }