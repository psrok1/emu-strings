class Engine(object):
    IDENTIFIER = ""
    EXTENSION = ""

    @classmethod
    def __eq__(cls, other):
        other_s = str(other).lower()
        return other_s == cls.IDENTIFIER.lower() or other_s == cls.EXTENSION.lower()

    @classmethod
    def __str__(cls):
        return cls.IDENTIFIER

    @classmethod
    def __hash__(cls):
        return hash(str(cls))

    @staticmethod
    def define(ident, ext):
        class SpecEngine(Engine):
            IDENTIFIER = ident
            EXTENSION = ext
        return SpecEngine

JScript = Engine.define("JScript", "js")
JScriptEncode = Engine.define("JScript.Encode", "jse")

VBScript = Engine.define("VBScript", "vbs")
VBScriptEncode = Engine.define("VBScript.Encode", "vbe")

