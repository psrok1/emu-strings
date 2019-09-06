import hashlib
import json
import os


class SetJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Report(object):
    def __init__(self):
        self.codes = []
        self.strings = {}

    def _report_string(self, string, store_in_file=False, types=None):
        h = hashlib.sha256(string).hexdigest()
        if h not in self.strings:
            self.strings[h] = {
                "refs": set(),
                "types": set(types or [])
            }
            if store_in_file:
                if not os.path.isdir("snippets"):
                    os.mkdir("snippets")
                with open("snippets/{}".format(h), "wb") as f:
                    f.write(string)
                self.strings[h]["in-file"] = True
            else:
                self.strings[h]["value"] = string
        elif types is not None:
            for typ in types:
                self.strings[h]["types"].add(typ)
        return h

    def report_string(self, string, code=False):
        store_in_file = code
        if not code:
            string = ''.join(map(lambda c: unichr(ord(c)), string)).encode("utf-8")
            if len(string) > 80:
                store_in_file = True
        h = self._report_string(string, store_in_file)
        if code:
            self.codes.append(h)
            self.strings[h]["types"].add("code")
        return h

    def report_http(self, url):
        self._report_string(url, types=["url"])

    def report_dns(self, qname, qtype):
        self._report_string(qname, types=["domain"])

    def report_extra(self, h, msg):
        code_id, pos_start, pos_end = map(int, msg.split(":"))
        code_id = self.codes[code_id]
        self.strings[h]["refs"].add((code_id, pos_start, pos_end))

    def store(self):
        """
        {
            "hash": {
                "types": ["code", "url", "domain"],
                "in-file": true,     // ./snippets/$hash
                "value": "value"     // in-file=False
                "refs": [
                    ["$source_hash", pos_start, pos_end]
                ]
            }
            ...
        }
        """
        data = json.dumps(self.strings, indent=4, cls=SetJSONEncoder)
        with open("report.json", "w") as f:
            f.write(data)
