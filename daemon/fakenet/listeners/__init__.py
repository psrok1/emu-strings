import threading
import logging

log = logging.getLogger("winedrop.fakenet.listener")

class FakenetListener(object):
    def __init__(self, ctx):
        self.context = ctx
        self.servers = []

    def _identify_server(self, s):
        if hasattr(s, "socket"):
            socket = s.socket
        else:
            socket = s
        host, port = socket.getsockname()
        return "{} {}:{}".format(s.__class__.__name__, host, port)

    def start(self):
        for s in self.servers:
            thread = threading.Thread(target=s.serve_forever)
            thread.daemon = True
            log.info("Starting {}".format(self._identify_server(s)))
            thread.start()

    def shutdown(self):
        for s in self.servers:
            log.info("Stopping {}".format(self._identify_server(s)))
            s.shutdown()
