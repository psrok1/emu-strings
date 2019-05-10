from .emulator import Emulator
from .loader import emulators, load_images


def get_emulators(analysis, **opts):
    return [emucls(analysis, **opts)
            for emucls in emulators
            if emucls.is_supported(analysis.language)]
