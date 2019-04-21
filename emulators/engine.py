class MetaEngine(type):
    IDENTIFIER = None
    EXTENSION = None

    def __eq__(cls, other):
        other_s = str(other).lower()
        return other_s == cls.IDENTIFIER.lower() or other_s == cls.EXTENSION.lower()

    def __str__(cls):
        return cls.IDENTIFIER

    def __hash__(cls):
        return hash(str(cls))


class Engine(object):
    __metaclass__ = MetaEngine

    @staticmethod
    def define(ident, ext):
        class SpecEngine(Engine):
            IDENTIFIER = ident
            EXTENSION = ext

        return SpecEngine

    @staticmethod
    def get(name):
        engines = Engine.__subclasses__()
        return engines[engines.index(name)]


JScript = Engine.define("JScript", "js")
JScriptEncode = Engine.define("JScript.Encode", "jse")

VBScript = Engine.define("VBScript", "vbs")
VBScriptEncode = Engine.define("VBScript.Encode", "vbe")
