import hashlib
import json
import os


class Report(object):
    def __init__(self):
        self.codes = []
        self.dns_reqs = set()
        self.urls = set()
        self.strings = {}

    def report_string(self, string, code=False):
        store_in_file = code
        if not code:
            string = ''.join(map(lambda c: unichr(ord(c)), string)).encode("utf-8")
            if len(string) > 80:
                store_in_file = True
        h = hashlib.sha256(string).hexdigest()
        if code:
            self.codes.append(h)
        if h not in self.strings:
            self.strings[h] = {
                "from": [],
                "types": []
            }
            if store_in_file:
                if not os.path.isdir("snippets"):
                    os.mkdir("snippets")
                with open("snippets/{}".format(h), "wb") as f:
                    f.write(string)
                self.strings[h]["in-file"] = True
            else:
                self.strings[h]["value"] = string
        if code and "code" not in self.strings[h]["types"]:
            self.strings[h]["types"].append("code")
        elif "string" not in self.strings[h]["types"]:
            self.strings[h]["types"].append("string")
        return h

    def report_url(self, url):
        self.urls.add(url)

    def report_dns(self, qname, qtype):
        self.dns_reqs.add((qname, qtype))

    def report_extra(self, h, msg):
        code_id, pos_start, pos_end = map(int, msg.split(":"))
        code_id = self.codes[code_id]
        self.strings[h]["from"].append((code_id, pos_start, pos_end))

    def store(self):
        data = json.dumps({
            "dns": list(self.dns_reqs),
            "urls": list(self.urls),
            "strings": self.strings,
        }, indent=4)
        with open("report.json", "w") as f: f.write(data)
