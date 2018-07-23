from emulators import Emulator
from emulators import engines


class BoxJSEmulator(Emulator):
    SUPPORTED_ENGINES = [
        engines.JScript,
        engines.JScriptEncode,
    ]
    IMAGE_NAME = "boxjs"