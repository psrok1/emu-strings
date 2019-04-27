from .emulator import Emulator
from .winedrop import WinedropEmulator
from .boxjs import BoxJSEmulator

emulators = [
    WinedropEmulator,
    BoxJSEmulator
]


def get_emulators(analysis, **opts):
    return [emucls(analysis, **opts)
            for emucls in emulators
            if emucls.is_supported(analysis.language)]
