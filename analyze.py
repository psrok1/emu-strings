import os, sys, re
import uuid
import docker
import docker.errors

client = docker.from_env()


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
        raise Exception("Unsupported type {}".format(fype))
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
