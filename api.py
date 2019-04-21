import os

from io import BytesIO

from flask import Flask, jsonify, request

import daemon

from .emulators.analysis import Analysis

app = Flask("winedrop", static_folder=os.path.abspath('./web/build'))


@app.route("/api/analysis/<aid>")
def get_analysis(aid):
    entry = Analysis.get_analysis(aid)
    if entry is None:
        return "{}"
    return jsonify(entry.results())


@app.route("/api/submit", methods=["POST"])
def submit_analysis():
    try:
        file = request.files.get('file')
        if not file:
            raise Exception("File not specified")

        engine = request.form["engine"]
        # Create BytesIO pseudo-file and store file from request
        strfd = BytesIO()
        file.save(strfd)
        # Add sample to analysis
        code = strfd.getvalue()
        # Create new analysis
        analysis = Analysis()
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


@app.errorhandler(404)
def page_not_found(*args):
    return app.send_static_file("index.html")


@app.route('/')
@app.route('/<path:path>')
def send_files(path='index.html'):
    return app.send_static_file(path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=64205)
