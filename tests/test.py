import json
import os
import requests
import time

API_URL = os.getenv("API_URL", "http://127.0.0.1:64205")


def start_analysis(code, name, language):
    req = requests.post(API_URL+"/api/submit", files={
        'file': (name, code)
    }, data={
        'options': json.dumps({
            'language': language
        })
    })
    req.raise_for_status()
    print("Started analysis {} ({})".format(req.json()["aid"], name))
    return req.json()["aid"]


def get_analysis_status(aid):
    req = requests.get(API_URL+"/api/analysis/"+aid)
    req.raise_for_status()
    return req.json()


def expect_url(aid):
    for t in range(180):
        status = get_analysis_status(aid)
        print("{}: ({}) {}".format(aid, t, status["status"]))
        if status["status"] in ["pending", "in-progress"]:
            time.sleep(1)
            continue
        if status["status"] == "success":
            print("{}: {}".format(aid, json.dumps(status, indent=4)))
            assert "hello.example" in status["results"]["urls"]
            break
        else:
            raise Exception("Analysis failed ({})".format(status["status"]))
    else:
        raise Exception("Analysis took too long")


aid = start_analysis(b"""
WScript.echo("h"+"t"+"t"+"p"+":"+"/"+"/"+"h"+"e"+"l"+"l"+"o"+"."+"e"+"x"+"a"+"m"+"p"+"l"+"e")
""", "sample.js", "JScript")

expect_url(aid)

aid = start_analysis(b"""
WScript.echo "h" & "t" & "t" & "p" & ":" & "/" & "/" & "h" & "e" & "l" & "l" & "o" & "." & "e" & "x" & "a" & "m" & "p" & "l" & "e"
""", "sample.vbs", "VBScript")

expect_url(aid)
