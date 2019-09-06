import json
import os

from emustrings.emulators import Emulator, with_tag
from emustrings.results import StringObject
from emustrings import language


class WinedropEmulator(Emulator):
    SUPPORTED_LANGUAGES = [
        language.JScript,
        language.JScriptEncode,
        language.VBScript,
        language.VBScriptEncode
    ]
    IMAGE_NAME = with_tag("psrok1/winedrop")

    def _load_report(self):
        report_path = os.path.join(self.workdir, "report.json")
        if not os.path.isfile(report_path):
            return {}
        with open(report_path) as f:
            return json.load(f)

    def store_results(self, storage):
        report = self._load_report()

        for hash, props in report.items():
            string_object = StringObject(
                hash=hash,
                path=os.path.join(self.workdir, "snippets", hash) if props.get("in-file", False) else None,
                value=props.get("value", None),
                types=props["types"],
                refs=props["refs"]
            )
            storage.push_string(string_object)

        logfiles = [
            ("stdout", os.path.join(self.workdir, "stdout.log")),
            ("wine", os.path.join(self.workdir, "wine.log")),
            ("winedrop", os.path.join(self.workdir, "winedrop.log"))
        ]
        for logname, logpath in logfiles:
            storage.push_logfile(self.__class__.__name__, logname, logpath)
