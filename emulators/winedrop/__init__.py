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
