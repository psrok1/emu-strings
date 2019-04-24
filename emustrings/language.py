class Language(object):
    registered = []

    def __init__(self, ident, ext):
        self.identifier = ident
        self.extension = ext
        Language.registered.append(self)

    def __eq__(self, other):
        other_s = str(other).lower()
        return other_s == self.identifier.lower() or other_s == self.extension.lower()

    def __str__(self):
        return self.identifier

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def get(name):
        languages = Language.registered
        return languages[languages.index(name)]

    def match(self, sample):
        return self == sample.extension

    @staticmethod
    def detect(sample):
        for language in Language.registered:
            if language.match(sample):
                return language
        return None


class ScrencLanguage(Language):
    def match(self, sample):
        if sample.has(b"#@~^"):
            return True
        return super().match(sample)


class JScriptLanguage(Language):
    def match(self, sample):
        if sample.has("function(") or \
           sample.has("return ") or \
           sample.has("new ") or \
           sample.has("ActiveXObject"):
            return True
        return super().match(sample)


class VBScriptLanguage(Language):
    def match(self, sample):
        if sample.has_icase("set ") or \
           sample.has_icase("dim ") or \
           sample.has_icase("sub ") or \
           sample.has_icase("end "):
            return True
        return super().match(sample)


JScriptEncode = ScrencLanguage("JScript.Encode", "jse")
VBScriptEncode = ScrencLanguage("VBScript.Encode", "vbe")

JScript = JScriptLanguage("JScript", "js")
VBScript = VBScriptLanguage("VBScript", "vbs")
