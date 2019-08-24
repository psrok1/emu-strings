import hashlib
import json
import os

from emustrings.emulators import Emulator
from emustrings.language import JScript, JScriptEncode


class BoxJSEmulator(Emulator):
    SUPPORTED_LANGUAGES = [
        JScript,
        JScriptEncode,
    ]
    IMAGE_NAME = "psrok1/emu-strings-boxjs"
    DISABLED = not bool(os.getenv("ENABLE_BOXJS", ""))

    def _local_path(self, fname):
        return os.path.join(self.workdir, self.sample.name+".results", fname)

    def _get_urls(self):
        urls_path = self._local_path("urls.json")
        if not os.path.isfile(urls_path):
            return []
        with open(urls_path) as f:
            return json.load(f)

    def _get_IOCs(self):
        iocs_path = self._local_path("IOC.json")
        if not os.path.isfile(iocs_path):
            return
        with open(iocs_path) as f:
            iocs = json.load(f)
        for ioc in iocs:
            if ioc["type"] == "UrlFetch":
                yield ioc["value"]["url"]
            if ioc["type"] == "FileWrite":
                yield ioc["value"]["file"]
            if ioc["type"] == "FileRead":
                yield ioc["value"]["file"]
            if ioc["type"] == "Run":
                yield ioc["value"]["command"]

    def connections(self):
        return list(set(self._get_urls()))

    def strings(self):
        """
        Returns list of strings found during emulation
        """
        return list(set(self._get_urls() + list(self._get_IOCs())))

    def _snippets(self):
        snippets_path = self._local_path("snippets.json")
        if not os.path.isfile(snippets_path):
            return

        with open(snippets_path) as f:
            snippets = json.load(f)

        for snip in snippets.keys():
            with open(self._local_path(snip), "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            yield (h, os.path.join(self.workdir, "results", snip))

    def snippets(self):
        return list(self._snippets())

    def logfiles(self):
        return list(filter(lambda f: os.path.isfile(f[1]), [
            ("analysis", self._local_path("analysis.log")),
            ("resources", self._local_path("resources.json")),
            ("IOC", self._local_path("IOC.json"))
        ]))
