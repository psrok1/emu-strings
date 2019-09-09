import logging
import os
import uuid

from datetime import datetime

from bson.objectid import ObjectId
from pymongo import MongoClient

from .results import ResultsStore
from .sample import Sample

logger = logging.getLogger(__name__)


class Analysis(object):
    """
    Analysis instance
    """
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_ORPHANED = "orphaned"

    MONGODB_URL = "mongodb://mongo:27017/"
    MONGODB_NAME = "emu-strings"

    ANALYSIS_PATH = "/app/results/analysis/"

    @staticmethod
    def db_collection():
        """
        Returns MongoDB collection for analysis objects
        """
        return MongoClient(Analysis.MONGODB_URL)[Analysis.MONGODB_NAME].analyses

    @property
    def workdir(self):
        """
        Getter for analysis working dir (mounted in container during emulation)
        """
        return os.path.join(self.ANALYSIS_PATH, str(self.aid))

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
        self.sample = None
        self.options = None
        self.status = None
        self.results = {}

        """
        Create new instance
        """
        if aid is None:
            self.aid = str(uuid.uuid4())
            os.makedirs(self.workdir)
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
            self.sample = Sample.load(self.workdir, params["sample"])
            self.options = params.get("options", {})
            self.results = params.get("results", {})
        except IndexError as e:
            raise IOError("Analysis {} is corrupted!".format(aid)) from e

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
            {"sample": 1, "aid": 1, "_id": 1, "timestamp": 1, "status": 1, "options": 1}
        ).sort("_id", -1).limit(limit))
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        return entries

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

    def add_sample(self, sample: Sample, options=None):
        """
        Adds sample to analysis workdir
        """
        if not self.empty:
            raise Exception("Sample is added yet!")

        self.sample = sample
        self.options = options or {}
        params = {
            "$set": {
                "sample": sample.to_dict(),
                "options": self.options
            }
        }
        self.db_collection().update({"aid": self.aid}, params)
        self.sample.store(self.workdir)
        logging.info("%s: Added sample %s for analysis", self.aid, str(self.sample))

    def start(self, docker_client):
        from .emulators import get_emulators

        if self.empty:
            raise RuntimeError("Sample must be added before analysis start")

        self.set_status(Analysis.STATUS_IN_PROGRESS)

        try:
            emulators = [emulator() for emulator in get_emulators(self.sample.language)]
            for emulator in emulators:
                logging.info("%s: Emulation started using %s (%s)", self.aid, emulator.name, emulator.emuid)
                emulator.start(
                    docker_client,
                    self.sample,
                    self.options)

            storage = ResultsStore(self.workdir)
            for emulator in emulators:
                emulator.join()
                logging.info("%s: Emulation finished using %s (%s)", self.aid, emulator.name, emulator.emuid)
                emulator.store_results(storage)

            logging.info("%s: Done", self.aid)

            self.results = storage.store_dict()
            self.db_collection().update({"aid": self.aid},
                                        {"$set": {
                                            "results": self.results
                                        }})
            self.set_status(Analysis.STATUS_SUCCESS)
        except Exception as exc:
            import traceback
            logging.exception("%s: Critical error occured", self.aid)
            self.set_status(Analysis.STATUS_FAILED, traceback.format_exc())

    def get_snippet(self, snippet_hash):
        return ResultsStore(self.workdir).read_snippet(snippet_hash)

    def get_logfile(self, emulator, logname):
        return ResultsStore(self.workdir).read_logfile(emulator, logname)

    def to_dict(self):
        return {
            "sample": self.sample.to_dict(),
            "status": self.status,
            "timestamp": self.timestamp,
            "options": self.options,
            "results": self.results
        }
