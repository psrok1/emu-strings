from gevent.monkey import patch_all
patch_all()

import logging

def setup_logger():
    log = logging.getLogger("winedrop")

    fh = logging.FileHandler('winedrop.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    return log

log = setup_logger()

import gevent
from libs.context import AnalysisContext
from fakenet import Fakenet

try:
    context = AnalysisContext()

    fakenet = Fakenet(context)
    fakenet.start()

    gevent.spawn(context.analyze).join()

    fakenet.shutdown()
except Exception as e:
    import traceback
    log.exception(traceback.format_exc())