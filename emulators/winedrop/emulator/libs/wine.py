import gevent
import subprocess
import logging
import os

log = logging.getLogger("winedrop.wine")


class WineLauncher(object):
    SOFT_TIMEOUT = os.getenv("SOFT_TIMEOUT", 30)
    HARD_TIMEOUT = os.getenv("HARD_TIMEOUT", 60)
    WINEDROP_PATH = "/root/winedrop/"
    WINE_EXEC = os.path.join(WINEDROP_PATH, "wine-build/wine")
    WINE_PREFIX = os.path.join(WINEDROP_PATH, "wine-prefix")
    WINE_USER = "winedrop"
    SCRIPT_ENGINE = {
        "js": "JScript",
        "jse": "JScript.Encode",
        "vbs": "VBScript",
        "vbe": "VBScript.Encode"
    }

    def handle_execution(self, proc):
        with open("wine.log", "w") as f:
            for line in proc.stdout:
                f.write(line)
        return True

    def analyze_script(self, script_name, engine_name=None):
        timeout = gevent.Timeout(self.HARD_TIMEOUT)
        timeout.start()

        if engine_name is None:
            engine_name = self.SCRIPT_ENGINE.get(script_name.split(".")[-1].lower())

        if engine_name is None:
            raise Exception("Unknown extension - specify scripting engine manually")

        log.info("Starting {} using {} engine".format(script_name, engine_name))
        proc = subprocess.Popen(
            [self.WINE_EXEC, "cscript", "//E:"+engine_name, "//T:"+str(self.SOFT_TIMEOUT), script_name],
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
