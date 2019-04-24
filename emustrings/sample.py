import chardet
import hashlib
import os


class Sample(object):
    def __init__(self, code, name=None):
        self.code = code
        self.md5 = hashlib.md5(code).hexdigest()
        self.sha256 = hashlib.sha256(code).hexdigest()
        self.name = name or self.sha256
        try:
            self.str_code = code.decode(chardet.detect(code))
        except Exception:
            self.str_code = ""
        self.icase_str_code = self.str_code.lower()

    @property
    def extension(self):
        return next(self.name.rsplit("."), "")

    def has(self, pattern):
        if isinstance(pattern, bytes):
            return pattern in self.code
        return pattern in self.str_code

    def has_icase(self, pattern):
        return pattern in self.icase_str_code

    def ensure_extension(self, extension):
        if self.extension.lower() != extension.lower():
            self.name += "." + extension
        return self.extension

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            code = f.read()
        name = os.path.basename(path)
        return Sample(code, name)

    def store(self, path):
        with open(path, "wb") as f:
            f.write(self.code)
