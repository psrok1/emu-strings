import os
import hashlib
import uuid

from datetime import datetime

from pymongo import MongoClient

from config import StorageConfig, MongoConfig
from emulators import get_emulators

from .language import Language, JScript
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
        self.status = None

        self.snippets = {}
        self.strings = set()
        self.logfiles = {}

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
            self.language = Language.get(params["language"])
            self.sample = Sample.load("{}.{}".format(params["sha256"], self.language.extension))
        except IndexError as e:
            raise IOError("Analysis {} is corrupted!".format(aid)) from e

        self.load_results()

    def load_results(self):
        snippets_dir = os.path.join(self.workdir, "snippets")
        if os.path.isdir(snippets_dir):
            self.snippets = {
                snip: os.path.join(snippets_dir, snip)
                for snip in os.listdir(snippets_dir)
            }

        logfiles_dir = os.path.join(self.workdir, "logfiles")
        if os.path.isdir(logfiles_dir):
            self.logfiles = {
                log: os.path.join(logfiles_dir, log)
                for log in os.listdir(logfiles_dir)
            }

        strings_path = os.path.join(self.workdir, "strings.txt")
        if os.path.isfile(strings_path):
            with open(strings_path, "r") as f:
                self.strings = set(list(map(str.strip, f.readlines())))

    def add_snippet(self, snippet):
        snippets_dir = os.path.join(self.workdir, "snippets")
        os.makedirs(snippets_dir, exist_ok=True)

        if isinstance(snippet, (list, tuple)):
            snip_id, emulation_path = snippet
        else:
            snip_id = hashlib.sha256(snippet).hexdigest()
            emulation_path = None

        if snip_id in self.snippets:
            return

        snippet_path = os.path.join(snippets_dir, snip_id)

        if emulation_path is None:
            with open(snippet_path, "wb") as f:
                f.write(snippet)
        else:
            emulation_path = os.path.abspath(emulation_path)
            symlink_path = os.path.abspath(snippets_dir)
            relpath = os.path.relpath(emulation_path, symlink_path)
            os.symlink(relpath, snippet_path)

        self.snippets[snip_id] = snippet_path

    def add_string(self, string):
        printable = '0123456789abcdefghijklmnopqrstuvwxyz' \
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()' \
                    '*+,-./:;<=>?@[\\]^_`{|}~ \t'
        if 3 < len(string) < 128 and all(map(lambda c: c in printable, string)):
            self.strings.add(string)
        if len(string) >= 128:
            self.add_snippet(string)

    def store_strings(self):
        with open(os.path.join(self.workdir, "strings.txt"), "w") as f:
            f.write('\n'.join(list(self.strings)))

    def add_logfile(self, logname, logpath):
        logfiles_dir = os.path.join(self.workdir, "logfiles")
        os.makedirs(logfiles_dir, exist_ok=True)
        if logname in self.logfiles:
            return
        logfile_path = os.path.join(logfiles_dir, logname)
        emulation_path = os.path.abspath(logpath)
        symlink_path = os.path.abspath(logfiles_dir)
        relpath = os.path.relpath(emulation_path, symlink_path)
        os.symlink(relpath, logfile_path)
        self.logfiles[logname] = logfile_path

    def store_results(self, emulators):
        for emulator in emulators:
            for string in emulator.strings():
                self.add_string(string)
            for snippet in emulator.snippets():
                self.add_snippet(snippet)
            for logfile in emulator.logfiles():
                self.add_logfile(*logfile)
        self.store_strings()

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

    def add_sample(self, sample: Sample, language=None):
        """
        Adds sample to analysis workdir
        """
        if not self.empty:
            raise Exception("Sample is added yet!")

        language = language or Language.detect(sample) or JScript
        params = {
            "$set": {
                "md5": sample.md5,
                "sha256": sample.sha256,
                "language": str(language),
                "filename": sample.name
            }
        }
        self.sample = sample
        self.language = language
        self.db_collection().update({"aid": self.aid}, params)
        self.sample.store(os.path.join(self.workdir, sample.sha256) + "." + self.language.extension)

    def set_status(self, status):
        """
        Sets analysis status
        """
        self.db_collection().update({"aid": self.aid},
                                    {"$set": {"status": status}})
        self.status = status

    def start(self, docker_client, opts=None):
        opts = opts or {}
        if self.empty:
            raise RuntimeError("Sample must be added before analysis start")

        self.set_status(Analysis.STATUS_IN_PROGRESS)

        try:
            emus = get_emulators(self, **opts)
            for emu in emus:
                print("Started in {}".format(emu.__class__.__name__))
                emu.start(docker_client)

            for emu in emus:
                emu.join()

            self.store_results(emus)
            self.set_status(Analysis.STATUS_SUCCESS)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.set_status(Analysis.STATUS_FAILED)
