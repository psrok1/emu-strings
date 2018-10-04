import base64
import os
import logging
import select
import subprocess

from threading import Thread
from Queue import Queue

import gevent

from libs import report

log = logging.getLogger("winedrop.wine")


class WineLauncher(object):
    WINE_EXEC = os.getenv("WINE")
    WINE_PREFIX = os.getenv("WINEPREFIX")
    WINE_USER = "winedrop"

    def __init__(self):
        self.report = report.Report()
        self.soft_timeout = float(os.getenv("SOFT_TIMEOUT", 30.0))
        self.hard_timeout = float(os.getenv("HARD_TIMEOUT", 60.0))
        self.sample = os.getenv("SAMPLE")
        self.engine = os.getenv("ENGINE")
        self.lmagic = "*$winedrop"

    def handle_log(self, channel, msg):
        if channel == "snippet":
            self.report.report_snippet(msg)
        elif channel == "notice":
            log.info(msg)
        elif channel == "string":
            alen, blen, strs = msg.split(":", 2)
            alen, blen = map(int, [alen, blen])
            astr = strs[:alen]
            bstr = strs[alen:alen+blen]
            print (alen, blen, strs)
            self.report.report_string(astr+bstr, components=(None if not bstr else [astr, bstr]))

    def handle_execution(self, proc):
        def reader(pipe, queue):
            try:
                for line in pipe:
                    queue.put((pipe, line))
            finally:
                queue.put(None)            
        
        try:
            wine = open("wine.log", "w")
            stdout = open("stdout.log", "w")
            
            msgq = Queue()
            stdout_reader = Thread(target=reader, args=[proc.stdout, msgq])
            stderr_reader = Thread(target=reader, args=[proc.stderr, msgq])
            stdout_reader.start()
            stderr_reader.start()
            while stdout_reader.is_alive() or stderr_reader.is_alive():
                element = msgq.get()
                if element is None:
                    continue
                source, msg = element
                if source == proc.stdout:
                    print msg
                    if msg.startswith(self.lmagic):
                        try:
                            magic, channel, message, terminator = msg.strip().split(":",3)
                            if message == "init" and self.lmagic.endswith("winedrop"):
                                self.lmagic = magic
                            else:
                                self.handle_log(channel, base64.b64decode(message))
                        except Exception:
                            import traceback
                            log.exception(traceback.format_exc())
                    else:
                        stdout.write(msg)
                elif source == proc.stderr:
                    print msg
                    wine.write(msg)
        finally:
            wine.close()
            stdout.close()
        return True
        

    def analyze_script(self):
        timeout = gevent.Timeout(self.hard_timeout)
        timeout.start()

        log.info("Starting {} using {} engine".format(self.sample, self.engine))
        proc = subprocess.Popen(
            [self.WINE_EXEC, "cscript", "//E:"+self.engine, "//T:"+str(int(self.soft_timeout)), self.sample],
            env={
                "WINEPREFIX": self.WINE_PREFIX,
                "WINEDLLOVERRIDES": "jscript,vbscript=n",
                #"WINEDEBUG": "trace+module,imports",
                "USER": self.WINE_USER
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

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
