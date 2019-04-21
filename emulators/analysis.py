from datetime import datetime
import os
import uuid
import hashlib

from pymongo import MongoClient

from .engine import Engine
from .emulator import get_emulators

from config import StorageConfig, MongoConfig


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
        return self.sample_file is None

    def __init__(self, aid=None):
        """
        Creates new analysis (with unique id) or gets instance of existing one
        """
        self.sample_file = self.engine = None
        self.status = None
        if aid is None:
            # Create new instance
            self.aid = str(uuid.uuid4())
            os.makedirs(self.workdir)
            self.db_collection().insert({"aid": self.aid, "status": self.STATUS_PENDING, "timestamp": datetime.now()})
        else:
            # Bind to existing instance
            self.aid = aid
            if not os.path.isdir(self.workdir):
                raise IOError("Analysis path {} doesn't exist".format(aid))
            try:
                params = self.db_collection().find_one({"aid": aid})
                self.status = params["status"]
                self.timestamp = params["timestamp"]
                self.engine = Engine.get(params["engine"])
                self.sample_file = "{}.{}".format(params["sha256"], self.engine.EXTENSION)
                with open(os.path.join(self.workdir, self.sample_file), "rb") as f:
                    self.code = f.read()
            except IndexError as e:
                raise IOError("Analysis {} doesn't contain valid sample file!".format(aid)) from e

    def results(self):
        spath = os.path.join(self.workdir, "strings.txt")
        strings = ""
        if os.path.isfile(spath):
            with open(spath, "r") as f:
                strings = f.read()
        return {
            "status": self.status,
            "timestamp": self.timestamp,
            "sample": self.sample_file,
            "strings": strings
        }

    @staticmethod
    def find_analysis(code, engine):
        entry = Analysis.db_collection().find_one({
            "sha256": hashlib.sha256(code).hexdigest(),
            "engine": str(engine)})
        return entry and Analysis(aid=entry["aid"])

    @staticmethod
    def get_analysis(aid):
        entry = Analysis.db_collection().find_one({
            "aid": aid})
        return entry and Analysis(aid=aid)

    def add_sample(self, code, engine, filename=None):
        """
        Adds sample to analysis workdir
        """
        if not self.empty:
            raise Exception("Sample is added yet!")
        params = {
            "$set": {
                "md5": hashlib.md5(code).hexdigest(),
                "sha1": hashlib.sha1(code).hexdigest(),
                "sha256": hashlib.sha256(code).hexdigest(),
                "sha512": hashlib.sha512(code).hexdigest(),
                "engine": str(engine)
            }
        }
        self.code = code
        self.engine = Engine.get(engine)
        self.sample_file = "{}.{}".format(params["$set"]["sha256"], self.engine.EXTENSION)
        params["$set"]["filename"] = filename or self.sample_file
        self.db_collection().update({"aid": self.aid}, params)
        with open(os.path.join(self.workdir, self.sample_file), "wb") as f:
            f.write(code)

    def set_status(self, status):
        """
        Sets analysis status
        """
        self.db_collection().update({"aid": self.aid}, {"$set": {"status": status}})
        self.status = status

    def handle_results(self, emulators):
        printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t'
        snippets_dir = os.path.join(self.workdir, "snippets")

        os.makedirs(snippets_dir)
        strings = set()
        snippets = dict()
        
        for emulator in emulators:
            strs = emulator.strings()
            strings = strings.union(set(filter(lambda s: 3<len(s)<128 and all(map(lambda c: c in printable, s)), strs)))
            snippets.update({hashlib.sha256(snip).hexdigest(): {"code": snip} 
                            for snip in filter(lambda s: len(s)>=128, strings)})
            snippets.update({snip[0]: {"path": snip[1]} for snip in emulator.snippets()})
        
        with open(os.path.join(self.workdir, "strings.txt"), "w") as f:
            f.write('\n'.join(list(strings)))
        
        for h, snip in snippets.items():
            if "path" in snip:
                snippet_path = os.path.abspath(snip["path"])
                symlink_path = os.path.abspath(snippets_dir)
                relpath = os.path.relpath(snippet_path, symlink_path)
                print(relpath)
                os.symlink(relpath, os.path.join(snippets_dir, h))
            if "code" in snip:
                with open(os.path.join(snippets_dir, h), "wb") as f:
                    f.write(snip["code"])
        
    def start(self, docker_client, opts=None):
        opts = opts or {}
        if self.empty:
            raise ValueError("Sample must be added")
        self.set_status(Analysis.STATUS_IN_PROGRESS)
        try:
            emus = [emu_cls(self.code, self.engine, **opts) for emu_cls in get_emulators(self.engine)]
            for emu in emus:
                print("Started in {}".format(emu.__class__.__name__))
                emu.start(docker_client)
            for emu in emus:
                emu.join()
            self.handle_results(emus)
            self.set_status(Analysis.STATUS_SUCCESS)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.set_status(Analysis.STATUS_FAILED)
