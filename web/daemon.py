import os, re, sys
import uuid
import docker
import docker.errors


class Analysis(object):
    ANALYSIS_DIR = os.path.join(os.getcwd(), "./analyses/")
    ENGINE_EXT = {
        "jscript": "js",
        "jscript.encode": "jse",
        "vbscript": "vbs",
        "vbscript.encode": "vbe"
    }

    @property
    def workdir(self):
        return os.path.join(self.ANALYSIS_DIR, str(self.aid))

    @property
    def empty(self):
        return self.sample_file is None

    def __init__(self, aid=None):
        self.sample_file = self.engine = None
        self.container = None
        if aid is None:
            self.aid = uuid.uuid4()
            os.makedirs(self.workdir)
        else:
            self.aid = aid
            if not os.path.isdir(self.workdir):
                raise IOError("Analysis path {} doesn't exist".format(aid))
            try:
                self.sample_file = filter(lambda f: f.startswith("sample"), os.listdir(self.workdir))[0]
                self.engine = {ext: n for n, ext in self.ENGINE_EXT.iteritems()}[self.sample_file.split(".")[-1]]
            except IndexError:
                raise Exception("Analysis {} doesn't contain valid sample file!".format(aid))

    def add_sample(self, code, engine):
        if not self.empty:
            raise Exception("Sample is added yet!")
        self.engine = engine.lower()
        if self.engine not in self.ENGINE_EXT:
            raise Exception("Engine {} not supported".format(self.engine))
        # Add sample to analysis folder
        with open(os.path.join(self.workdir, "sample.{}".format(self.ENGINE_EXT[self.engine])), "wb") as f:
            f.write(code)

    def join(self):
        if self.container is None:
            raise Exception("Analysis not started!")
        status = self.container.wait()["StatusCode"]
        self.container.remove()
        return status


class Daemon(object):
    IMAGE_NAME = "winedrop"

    def __init__(self):
        self.client = docker.from_env()

    def start_analysis(self, analysis):
        if analysis.empty:
            raise Exception("Analysis doesn't have sample added")
        analysis.container = self.client.containers.run(
            self.IMAGE_NAME,
            detach=True,
            dns=["127.0.0.1"],
            network_mode="none",
            volumes={
                analysis.workdir: {
                    "bind": "/root/analysis",
                    "mode": "rw"
                }
            }
        )



def new_analysis():
    aid = uuid.uuid4()
    os.makedirs("./analyses/"+str(aid))
    return aid


def get_analysis_workdir(aid):
    path = os.path.join(os.getcwd(), "./analyses/"+str(aid))
    if not os.path.isdir(path):
        raise IOError("Analysis path {} doesn't exist".format(str(aid)))
    if len(os.listdir(path)) != 0:
        raise IOError("Analysis folder {} not empty".format(str(aid)))
    return path


def start_analysis(aid, code, lang):
    analysis_cwd = get_analysis_workdir(aid)
    with open(os.path.join(analysis_cwd, "sample.{}".format(lang)), "wb") as f:
        f.write(code)
    container = client.containers.run(
        "winedrop",
        detach=True,
        dns=["127.0.0.1"],
        network_mode="none",
        volumes={
            analysis_cwd: {
                "bind": "/root/analysis",
                "mode": "rw"
            }
        }
    )
    status = container.wait()["StatusCode"]
    print container.logs()
    container.remove()
    return status

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: analyze.py [sample_name] [sample_type]"
    fname = sys.argv[1]
    if len(sys.argv) < 3:
        ftype = fname.split(".")[-1].lower()
    else:
        ftype = sys.argv[2].lower()
    if ftype not in ["js", "jse", "vbs", "vbe"]:
        raise Exception("Unsupported type {}".format(ftype))
    with open(fname, "rb") as f:
        code = f.read()
    if re.search("#@~\^[a-zA-Z0-9+/]{6}==", code):
        print "[*] Encoded form detected"
        ftype = {"js": "jse", "vbs": "vbe"}.get(ftype, ftype)
    aid = new_analysis()
    if start_analysis(aid, code, ftype):
        print "[+] Analysis succeed."
    else:
        print "[-] Analysis failed."
