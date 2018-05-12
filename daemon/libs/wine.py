import gevent
import subprocess
import logging

log = logging.getLogger("winedrop.wine")


class WineLauncher(object):
    SOFT_TIMEOUT = 15
    HARD_TIMEOUT = 30

    def __init__(self, wine_exec, wine_prefix):
        self.wine = wine_exec
        self.wine_prefix = wine_prefix

    def handle_execution(self, proc):
        proc.communicate()
        return True

    def analyze_script(self, script_path):
        timeout = gevent.Timeout(self.HARD_TIMEOUT).start()
        log.info("Starting {}".format(script_path))
        proc = subprocess.Popen(
            [self.wine, script_path, "/T", str(self.SOFT_TIMEOUT)],
            env={
                "WINEPREFIX": self.wine_prefix,
                "WINEDEBUG": "trace+ole,wininet,winhttp"
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        finished = None
        try:
            finished = self.handle_execution(proc)
        except gevent.Timeout as t:
            if t is not timeout:
                raise
            proc.kill()
            log.warning("Wine killed - hard timeout reached!")
        finally:
            timeout.close()

        if not finished:
            log.warning("Script interrupted - timeout reached!")
            pass
