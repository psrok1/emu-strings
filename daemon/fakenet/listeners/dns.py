import SocketServer
from dnslib import *
from fakenet.listeners import FakenetListener
import logging

log = logging.getLogger("winedrop.fakenet.dns")


class DNSListener(FakenetListener):
    def __init__(self, ctx):
        super(DNSListener, self).__init__(ctx)

        class DNSRequestHandler(SocketServer.BaseRequestHandler):
            def get_data(self):
                raise NotImplementedError

            def send_data(self, data):
                raise NotImplementedError

            def dns_response(self, data):
                request = DNSRecord.parse(data)
                reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

                qname = request.q.qname
                qn = str(qname)
                qtype = request.q.qtype
                qt = QTYPE[qtype]

                log.debug("Request {} {}".format(qt, qn))
                ctx.report.report_dns(qn, qt)

                if qt == '*':
                    log.debug("* -> A")
                    qt = A

                if qt == A:
                    log.debug("Reply -> 127.0.0.1")
                    reply.add_answer(RR(rname=qname,
                                        rtype=QTYPE[qt],
                                        rclass=1,
                                        ttl=60 * 5,
                                        rdata=A("127.0.0.1")))
                else:
                    log.warning("Unsupported query: {} {}".format(qt, qn))

                return reply.pack()

            def handle(self):
                try:
                    data = self.get_data()
                    self.send_data(self.dns_response(data))
                except Exception:
                    import traceback
                    log.exception(traceback.format_exc())

        class TCPRequestHandler(DNSRequestHandler):
            def get_data(self):
                data = self.request.recv(8192).strip()
                sz = int(data[:2].encode('hex'), 16)
                if sz < len(data) - 2:
                    log.error("Wrong size of TCP packet")
                    return
                elif sz > len(data) - 2:
                    log.error("Too big TCP packet")
                    return
                return data[2:]

            def send_data(self, data):
                sz = hex(len(data))[2:].zfill(4).decode('hex')
                return self.request.sendall(sz + data)

        class UDPRequestHandler(DNSRequestHandler):
            def get_data(self):
                return self.request[0].strip()

            def send_data(self, data):
                return self.request[1].sendto(data, self.client_address)

        self.servers = [
            SocketServer.ThreadingUDPServer(('127.0.0.1', 53), UDPRequestHandler),
            SocketServer.ThreadingTCPServer(('127.0.0.1', 53), TCPRequestHandler),
        ]
