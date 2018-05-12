import os
from libs import report, wine


class AnalysisContext(object):
    WINE_EXEC = "/root/wine/wine"
    WINE_PREFIX = "/root/.wine"
    SAMPLE_PATH = "/root/sample/"
    SAMPLE_EXT = [".js", ".jse", ".vbs", ".vbe"]
    ANALYSIS_PATH = "/root/analysis/"

    def __init__(self):
        self.report = report.Report()
        self.wine = wine.WineLauncher(self.WINE_EXEC, self.WINE_PREFIX)
        samples = filter(lambda s: any([s.lower().endswith(ext)
                                        for ext in self.SAMPLE_EXT]),
                         os.listdir(self.SAMPLE_PATH))
        if len(samples) != 1:
            raise Exception("No valid WSF samples found in {}!".format(self.SAMPLE_PATH))
        self.sample = samples[0]

    def analyze(self):
        self.wine.analyze_script(self.sample)