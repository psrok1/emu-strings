import gevent
import subprocess
import logging

log = logging.getLogger("winedrop.wine")


class WineLauncher(object):
    SOFT_TIMEOUT = 90
    HARD_TIMEOUT = 120

    def __init__(self, ctx):
        self.wine = ctx.WINE_EXEC
        self.wine_prefix = ctx.WINE_PREFIX
        self.wine_user = ctx.WINE_USER

    def handle_execution(self, proc):
        with open("wine.log", "w") as f:
            for line in proc.stdout:
                f.write(line)
        return True

    def analyze_script(self, script_name):
        timeout = gevent.Timeout(self.HARD_TIMEOUT)
        timeout.start()
        log.info("Starting {}".format(script_name))
        proc = subprocess.Popen(
            [self.wine, "cscript", script_name, "/T", str(self.SOFT_TIMEOUT)],
            env={
                "WINEPREFIX": self.wine_prefix,
                "WINEDLLOVERRIDES": "jscript,vbscript=n",
                "WINEDEBUG": "trace+ole,wininet,winhttp,shell,winsock",
                "USER": self.wine_user
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
