import pkgutil
from .emulator import Emulator

# Preloading all plugin submodules
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)

emulators = Emulator.__subclasses__()


def get_emulators(analysis, **opts):
    return [emucls(analysis, **opts)
            for emucls in emulators
            if emucls.is_supported(analysis.language)]
