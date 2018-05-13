import json


class Report(object):
    def __init__(self):
        self.snippets = set()
        self.dns_reqs = set()
        self.urls = set()
        self.strings = set()

    def report_snippet(self, snippet):
        self.snippets.add(snippet)

    def report_url(self, url):
        self.urls.add(url)

    def report_dns(self, qname, qtype):
        self.dns_reqs.add((qname, qtype))

    def report_string(self, string):
        self.strings.add(string)

    def store(self):
        data = json.dumps({
            "snippets": list(self.snippets),
            "dns": list(self.dns_reqs),
            "urls": list(self.urls),
            "strings": list(self.strings)
        }, indent=4)
        with open("report.json", "w") as f: f.write(data)
