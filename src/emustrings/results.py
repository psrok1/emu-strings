import hashlib
import os
import re

from urllib.parse import urlparse


class StringObject(object):
    PRINTABLE_CHARS = '0123456789abcdefghijklmnopqrstuvwxyz' \
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()' \
                      '*+,-./:;<=>?@[\\]^_`{|}~ \t'
    URL_REGEX = r"(https?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]{2,})+(?:[/?][a-zA-Z-0-9?/:&+\-=.]+)?)"

    def __init__(self, value=None, hash=None, path=None, types=None, refs=None):
        self._hash = hash
        self._value = value
        self.path = path
        self.types = set(types)
        self.refs = set(map(tuple, refs))

    @property
    def value(self):
        if not self._value and self.path:
            with open(self.path) as f:
                self._value = f.read()
        return self._value

    @property
    def hash(self):
        if not self._hash:
            self._hash = hashlib.sha256(self._value.encode("utf8")).hexdigest()
        return self._hash

    def get_length(self):
        return len(self.value)

    def find_urls(self):
        for match in re.finditer(self.URL_REGEX, self.value):
            yield StringObject(value=match.group(0),
                               types=["url"],
                               refs=[(self.hash, match.start(0), match.end(0))])

    def is_printable(self):
        return all(map(lambda c: c in self.PRINTABLE_CHARS, self.value))

    def is_too_short(self):
        return self.get_length() < 3

    def is_short(self):
        return self.get_length() < 128

    def is_url(self):
        return "url" in self.types

    def is_domain(self):
        return "domain" in self.types

    def merge_object(self, other):
        for typ in other.types:
            self.types.add(typ)
        for ref in other.refs:
            self.refs.add(tuple(ref))


class ResultsStore(object):
    """
    Storage for incoming analysis results from emulator
    """
    def __init__(self, workdir):
        self.workdir = workdir
        self.logfiles = {}
        self.domains = {}
        self.strings = {}
        self.objects = {}

    def push_domain(self, domain):
        if domain not in self.domains:
            self.domains[domain] = set()

    def push_url(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        self.push_domain(domain)
        self.domains[domain].add(url)

    def push_string(self, string_object: StringObject):
        # Extracting domain/url artifacts
        if string_object.is_too_short():
            return
        if string_object.is_domain():
            self.push_domain(string_object.value)
        elif string_object.is_url():
            self.push_url(string_object.value)
        else:
            for url_object in string_object.find_urls():
                self.push_string(url_object)
        # Extracting easy-readable strings
        if string_object.is_short() and string_object.is_printable():
            self.strings[string_object.value] = string_object.hash
            string_object.types.add("short")
        # If object was registered yet (extracted url found in different place?) - merge refs
        if string_object.hash in self.objects:
            self.objects[string_object.hash].merge_object(string_object)
        else:
            self.objects[string_object.hash] = string_object
        # Store snippets
        os.makedirs(os.path.join(self.workdir, "snippets"), exist_ok=True)
        snippet_path = os.path.join(self.workdir, "snippets", string_object.hash)
        if "short" not in string_object.types and not os.path.exists(snippet_path):
            if string_object.path is None:
                with open(snippet_path, "w") as f:
                    f.write(string_object.value)
            else:
                os.symlink(string_object.path, snippet_path)

    def push_logfile(self, emulator_name, log_name, log_path):
        os.makedirs(os.path.join(self.workdir, "logfiles", emulator_name), exist_ok=True)
        logfile_path = os.path.join(self.workdir, "logfiles", emulator_name, log_name)
        if not os.path.exists(logfile_path):
            os.symlink(log_path, logfile_path)
        if emulator_name not in self.logfiles:
            self.logfiles[emulator_name] = [log_name]
        else:
            self.logfiles[emulator_name].append(log_name)

    def read_logfile(self, emulator_name, log_name):
        if "." in emulator_name or "." in log_name:
            return None
        logfile_path = os.path.join(self.workdir, "logfiles", emulator_name, log_name)
        if not os.path.exists(logfile_path):
            return None
        with open(logfile_path) as f:
            return f.read()

    def read_snippet(self, snippet_hash):
        if "." in snippet_hash:
            return None
        snippet_path = os.path.join(self.workdir, "snippets", snippet_hash)
        with open(snippet_path) as f:
            return f.read()

    def store_dict(self):
        return {
            "logfiles": self.logfiles,
            "domains": {domain: list(urls) for domain, urls in self.domains.items()},
            "strings": self.strings,
            "objects": {
                obj.hash: {
                    "types": list(obj.types),
                    "refs": list(obj.refs)
                } for obj in self.objects.values()
            }
        }
