import gevent
import subprocess
import logging
import os

from libs import report

log = logging.getLogger("winedrop.wine")


class WineLauncher(object):
    WINEDROP_PATH = "/root/winedrop/"
    WINE_EXEC = os.path.join(WINEDROP_PATH, "wine-build/wine")
    WINE_PREFIX = os.path.join(WINEDROP_PATH, "wine-prefix")
    WINE_USER = "winedrop"

    def __init__(self):
        self.report = report.Report()
        self.soft_timeout = os.getenv("SOFT_TIMEOUT", 30)
        self.hard_timeout = os.getenv("HARD_TIMEOUT", 60)
        self.sample = os.getenv("SAMPLE")
        self.engine = os.getenv("ENGINE")

    def handle_execution(self, proc):
        with open("wine.log", "w") as f:
            for line in proc.stdout:
                f.write(line)
        return True

    def analyze_script(self):
        timeout = gevent.Timeout(self.hard_timeout)
        timeout.start()

        log.info("Starting {} using {} engine".format(self.sample, self.engine))
        proc = subprocess.Popen(
            [self.WINE_EXEC, "cscript", "//E:"+self.engine, "//T:"+str(self.soft_timeout), self.sample],
            env={
                "WINEPREFIX": self.WINE_PREFIX,
                "WINEDLLOVERRIDES": "jscript,vbscript=n",
                "WINEDEBUG": "trace+ole,wininet,winhttp,shell,winsock",
                "USER": self.WINE_USER
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
            timeout.cancel()

        if not finished:
            log.warning("Script interrupted - timeout reached!")
            pass
        self.report.store()
