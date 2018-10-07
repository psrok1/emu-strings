from collections import defaultdict
import json
import os

from emulators import Emulator
from emulators import engines


class WinedropEmulator(Emulator):
    SUPPORTED_ENGINES = [
        engines.JScript,
        engines.JScriptEncode,
        engines.VBScript,
        engines.VBScriptEncode
    ]
    IMAGE_NAME = "winedrop"

    def _load_report(self):
        report_path = os.path.join(self.workdir, "report.json")
        if not os.path.isfile(report_path):
            return defaultdict(list)
        with open(report_path) as f:
            return json.load(f)

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
