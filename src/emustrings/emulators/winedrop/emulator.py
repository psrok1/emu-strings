from collections import defaultdict
import json
import os

from emustrings.emulators import Emulator
from emustrings import language


class WinedropEmulator(Emulator):
    SUPPORTED_LANGUAGES = [
        language.JScript,
        language.JScriptEncode,
        language.VBScript,
        language.VBScriptEncode
    ]
    IMAGE_NAME = "psrok1/winedrop"

    def _load_report(self):
        report_path = os.path.join(self.workdir, "report.json")
        if not os.path.isfile(report_path):
            return defaultdict(list)
        with open(report_path) as f:
            return json.load(f)

    def connections(self):
        report = self._load_report()
        return list(set(report["urls"]))

    def strings(self):
        """
        Returns list of strings found during emulation
        """
        report = self._load_report()
        return list(set(report["strings"] + report["urls"]))

    def snippets(self):
        """
        Returns list of paths relative to workdir to code snippets
        """
        report = self._load_report()
        return map(lambda h: (h, os.path.join(self.workdir, "snippets", h)), report["snippets"])

    def logfiles(self):
        return [
            ("stdout", os.path.join(self.workdir, "stdout.log")),
            ("wine", os.path.join(self.workdir, "wine.log")),
            ("winedrop", os.path.join(self.workdir, "winedrop.log"))
        ]
