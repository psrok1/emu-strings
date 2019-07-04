from .emulator import Emulator
from .loader import emulators, load_images


def get_emulators(analysis):
    return [emucls(analysis)
            for emucls in emulators
            if emucls.is_supported(analysis.language)]
