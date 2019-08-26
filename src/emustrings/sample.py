import chardet
import hashlib
import os

from .language import Language, JScript


class Sample(object):
    DEFAULT_LANGUAGE = JScript

    def __init__(self, code, name=None, language=None):
        self.code = code

        self.md5 = hashlib.md5(code).hexdigest()
        self.sha256 = hashlib.sha256(code).hexdigest()
        self.name = (name and os.path.basename(name)) or self.sha256

        try:
            encoding = chardet.detect(code)["encoding"]
            self.stringified_code = code.decode(encoding or "utf8")
        except Exception:
            self.stringified_code = ""

        self.icase_stringified_code = self.stringified_code.lower()

        self.language = Language.get(language) or Language.detect(self) or self.DEFAULT_LANGUAGE
        self.ensure_extension(self.language.extension)

    @property
    def extension(self):
        if "." not in self.name:
            return ""
        return self.name.rsplit(".", 1)[-1]

    def ensure_extension(self, extension):
        if self.extension.lower() != extension.lower():
            self.name += "." + extension

    def has(self, pattern):
        if isinstance(pattern, bytes):
            return pattern in self.code
        return pattern in self.stringified_code

    def has_icase(self, pattern):
        return pattern in self.icase_stringified_code

    @staticmethod
    def load(workdir, params):
        with open(os.path.join(workdir, params["name"]), "rb") as f:
            code = f.read()
        return Sample(code, params["name"], params["language"])

    def store(self, workdir):
        with open(os.path.join(workdir, self.name), "wb") as f:
            f.write(self.code)

    def to_dict(self):
        return {
            "name": self.name,
            "md5": self.md5,
            "sha256": self.sha256,
            "language": str(self.language)
        }

    def __str__(self):
        return "{} ({})".format(self.name, str(self.language))
