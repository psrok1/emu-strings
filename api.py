import StringIO

from flask import Flask, jsonify, request

import daemon
import emulators
import emulators.analysis

app = Flask("winedrop")


@app.route("/api/capabilities", methods=["GET"])
def get_capabilities():
    return jsonify(emulators.get_capabilities())


@app.route("/api/analysis/<aid>")
def get_analysis(aid):
    db = emulators.analysis.Analysis.db_collection()
    entry = db.find_one({"aid": aid})
    if entry is None:
        return "{}"
    return jsonify(entry)


@app.route("/api/list/")
@app.route("/api/list/<soffs>")
def get_analysis_list(soffs=0):
    db = emulators.analysis.Analysis.db_collection()
    entries = list(db.find().sort([("timestamp", -1)]).skip(soffs).limit(30))
    return jsonify(entries)


@app.route("/api/submit", methods=["POST"])
def submit_analysis():
    try:
        file = request.files.get('file')
        if not file:
            raise Exception("File not specified")

        engine = request.form["engine"]
        emulator = request.form["emulator"]

        # Create analysis
        analysis = emulators.analysis.Analysis()
        # Create StringIO pseudo-file and store file from request
        strfd = StringIO.StringIO()
        file.save(strfd)
        # Add sample to analysis
        analysis.add_sample(strfd.getvalue(), engine)
        # Bind specified emulator
        analysis.bind_emulator(emulator)
        # Spawn task to daemon
        daemon.analyze_sample.apply_async(analysis.aid, request.form)
        # Return analysis id
        return jsonify({"aid": analysis.aid})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
