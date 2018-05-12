from fakenet.listeners import FakenetListener
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ssl
import logging

log = logging.getLogger("winedrop.fakenet.http")


class HTTPListener(FakenetListener):
    def __init__(self, ctx):
        super(HTTPListener, self).__init__(ctx)

        class HTTPRequestHandler(BaseHTTPRequestHandler):
            SCHEME = "http"

            def _get_url(self):
                host = self.headers["Host"] if "Host" in self.headers else self.client_address[0]
                path = self.path
                return "{}://{}{}".format(self.SCHEME, host, path)

            def _set_headers(self):
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctx.report.report_url(self._get_url())

            def do_GET(self):
                self._set_headers()
                log.debug("GET {}".format(self._get_url()))
                self.wfile.write("<h1>It works!</h1>")

            def do_HEAD(self):
                log.debug("HEAD {}".format(self._get_url()))
                self._set_headers()

            def do_POST(self):
                self._set_headers()
                log.debug("POST {}".format(self._get_url()))
                self.wfile.write("<h1>It works!</h1>")

        class HTTPSRequestHandler(HTTPRequestHandler):
            SCHEME = "https"

        self.servers = [
            HTTPServer(("127.0.0.1", 80), HTTPRequestHandler)
        ]
        try:
            httpsd = HTTPServer(("127.0.0.1", 443), HTTPSRequestHandler)
            httpsd.socket = ssl.wrap_socket(httpsd.socket, certfile='./server.pem', server_side=True)
            self.servers.append(httpsd)
        except Exception as e:
            pass
