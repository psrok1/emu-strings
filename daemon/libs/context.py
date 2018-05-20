import os
from libs import report, wine


class AnalysisContext(object):
    WINE_EXEC = "/root/daemon/wine-build/wine"
    WINE_PREFIX = "/root/daemon/wine-prefix/"
    SAMPLE_PATH = os.getcwd()
    SAMPLE_EXT = [".js", ".jse", ".vbs", ".vbe"]

    def __init__(self):
        self.report = report.Report()
        self.wine = wine.WineLauncher(self)
        samples = filter(lambda s: any([s.lower().endswith(ext)
                                        for ext in self.SAMPLE_EXT]),
                         os.listdir(self.SAMPLE_PATH))
        if len(samples) != 1:
            raise Exception("No valid WSH samples found in {}!".format(self.SAMPLE_PATH))
        self.sample = samples[0]

    def analyze(self):
        self.wine.analyze_script(self.sample)
        self.report.store()
