import os
import logging
import subprocess

from threading import Thread
from Queue import Queue

import gevent

from libs import report

log = logging.getLogger("winedrop.wine")


class WineChannel(object):
    def __init__(self, fstdout):
        self.lmagic = "*$wdrop"
        self.initialized = False
        self.line_buffer = None
        self.fstdout = fstdout
        self.recvlen = 0
        self.recvbuf = []

    def flush(self):
        if self.line_buffer:
            self.fstdout.write(self.line_buffer)
            self.line_buffer = None

    def consume(self, data):
        # If no data remaining and line starts with magic
        if self.recvlen == 0 and data.startswith(self.lmagic):
            # If some data were buffered - "\n" was added by monitor. Flush buffer
            if self.line_buffer:
                self.line_buffer = self.line_buffer[:-1]
                self.flush()
            # Parse message
            magic, recvlen, data = data.split(":", 2)
            self.recvlen = int(recvlen)
            # Check whether initialized with nonce
            if not self.initialized:
                self.lmagic = magic
                self.initialized = True
        # If there are data remaining
        if self.recvlen > 0:
            # Receive
            recv = data[:self.recvlen]
            self.recvbuf.append(recv)
            if len(recv) < self.recvlen:
                # Not finished yet - decrement recvlen
                self.recvlen -= len(recv)
            else:
                # Finished? Return
                self.line_buffer = data[self.recvlen:]
                self.recvlen = 0
                result = ''.join(self.recvbuf)
                self.recvbuf = []
                return result
        else:
            # If not - it's standard output
            self.flush()
            self.line_buffer = data


class WineLauncher(object):
    WINE_EXEC = os.getenv("WINE")
    WINE_PREFIX = os.getenv("WINEPREFIX")

    def __init__(self):
        self.report = report.Report()
        self.soft_timeout = float(os.getenv("SOFT_TIMEOUT", 30.0))
        self.hard_timeout = float(os.getenv("HARD_TIMEOUT", 60.0))
        self.sample = os.getenv("SAMPLE")
        self.engine = os.getenv("ENGINE")

    def get_user(self):
        userpath = "/opt/.username"
        with open(userpath) as f:
            return f.read().strip()

    def handle_log(self, channel, msg):
        if channel == "snippet":
            self.report.report_snippet(msg)
        elif channel == "notice":
            log.info(msg)
        elif channel == "string":
            self.report.report_string(msg)

    def handle_execution(self, proc):
        def reader(pipe, queue):
            try:
                for line in pipe:
                    queue.put((pipe, line))
            finally:
                queue.put(None)

        wine = None
        stdout = None
        try:
            wine = open("wine.log", "w")
            stdout = open("stdout.log", "w")
            channel = WineChannel(stdout)

            msgq = Queue()
            stdout_reader = Thread(target=reader, args=[proc.stdout, msgq])
            stderr_reader = Thread(target=reader, args=[proc.stderr, msgq])
            stdout_reader.start()
            stderr_reader.start()

            parts = []

            while stdout_reader.is_alive() or stderr_reader.is_alive():
                element = msgq.get()

                if element is None:
                    continue
                source, data = element

                if source == proc.stdout:
                    msg = channel.consume(data)
                    if msg is None:
                        continue
                    type = msg[0]
                    parts.append(msg[1:])
                    if type != "p":
                        payload = ''.join(parts)
                        parts = []
                        if type == "s":
                            self.handle_log("string", payload)
                        elif type == "c":
                            self.handle_log("snippet", payload)
                        elif type == "n":
                            self.handle_log("notice", payload)
                elif source == proc.stderr:
                    wine.write(data)
        finally:
            if wine:
                wine.close()
            if stdout:
                stdout.close()
        return True

    def analyze_script(self):
        timeout = gevent.Timeout(self.hard_timeout)
        timeout.start()

        log.info("Starting {} using {} engine".format(self.sample, self.engine))
        proc = subprocess.Popen(
            [self.WINE_EXEC, "cscript", "//E:"+self.engine, "//T:10", self.sample],
            env={
                "WINEPREFIX": self.WINE_PREFIX,
                "WINEDLLOVERRIDES": "jscript,vbscript=n",
                #"WINEDEBUG": "trace+module,imports",
                "USER": self.get_user()
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
