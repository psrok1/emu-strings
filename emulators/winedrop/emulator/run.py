from gevent.monkey import patch_all
patch_all()

import logging
import sys


def setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()

    fh = logging.FileHandler('winedrop.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)
    log.propagate = True
    return log


log = setup_logger()


if __name__ == "__main__":
    from libs.wine import WineLauncher
    from fakenet import Fakenet
    import gevent

    try:
        context = WineLauncher()

        fakenet = Fakenet(context)
        fakenet.start()

        gevent.spawn(context.analyze_script).join()

        fakenet.shutdown()
        sys.exit(0)
    except Exception as e:
        import traceback
        log.exception(traceback.format_exc())
        sys.exit(1)
