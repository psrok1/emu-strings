import os
import StringIO

from flask import Flask, jsonify, request, send_from_directory

import daemon
import emulators
import emulators.analysis

app = Flask("winedrop")


@app.route("/api/analysis/<aid>")
def get_analysis(aid):
    db = emulators.analysis.Analysis.db_collection()
    entry = db.find_one({"aid": aid})
    if entry is None:
        return "{}"
    del entry["_id"]
    return jsonify(entry)


@app.route("/api/analysis/<aid>/strings")
def get_strings(aid):
    pass


@app.route("/api/analysis/<aid>/snippet/<sid>")
def get_snippet(aid, sid):
    pass


@app.route("/api/submit", methods=["POST"])
def submit_analysis():
    try:
        file = request.files.get('file')
        if not file:
            raise Exception("File not specified")

        engine = request.form["engine"]
        # Create StringIO pseudo-file and store file from request
        strfd = StringIO.StringIO()
        file.save(strfd)
        # Add sample to analysis
        code = strfd.getvalue()
        # Try to find existing analysis
        #analysis = emulators.analysis.Analysis.find_analysis(code, engine)
        analysis=None
        if analysis is None:
            # Create new analysis
            analysis = emulators.analysis.Analysis()
            # Add sample code to analysis
            analysis.add_sample(code, engine, filename=file.filename)
            # Spawn task to daemon
            daemon.analyze_sample.apply_async((str(analysis.aid), {}))
        # Return analysis id
        return jsonify({"aid": str(analysis.aid)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
