from fakenet.listeners.http import HTTPListener
from fakenet.listeners.dns import DNSListener


class Fakenet(object):
    def __init__(self, ctx):
        self.listeners = [
            HTTPListener(ctx),
            DNSListener(ctx)
        ]

    def start(self):
        for l in self.listeners:
            l.start()

    def shutdown(self):
        for l in self.listeners:
            l.shutdown()
