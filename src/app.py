import json

from io import BytesIO

from flask import Flask, jsonify, request

from emustrings import Analysis, Sample, Language
from emustrings.celery import celery_app

app = Flask("emu-strings", static_folder='/app/build')


@app.route("/api/analysis")
def analysis_list():
    last_id = request.args.get('lastId')
    return jsonify(Analysis.list_analyses(last_id))


@app.route("/api/analysis/<aid>")
def get_analysis(aid):
    entry = Analysis.get_analysis(aid)
    if entry is None:
        return "{}"
    return jsonify(entry.to_dict())


@app.route("/api/analysis/<aid>/<key>/<identifier>")
def get_artifact(aid, key, identifier):
    entry = Analysis.get_analysis(aid)
    return entry.results.load_element(key, identifier)


@app.route("/api/submit", methods=["POST"])
def submit_analysis():
    try:
        file = request.files.get('file')
        if not file:
            raise Exception("File not specified")
        # Create BytesIO pseudo-file and store file from request
        strfd = BytesIO()
        file.save(strfd)
        # Add sample to analysis
        code = strfd.getvalue()
        # Create new analysis
        analysis = Analysis()
        sample = Sample(code, file.filename)
        options = json.loads(request.form.get("options", "{}"))
        language = options.get("language", "auto-detect")
        if language == "auto-detect":
            language = None
        else:
            language = Language.get(language)
        # Add sample code to analysis
        analysis.add_sample(sample, language, options)
        # Spawn task to daemon
        celery_app.send_task("analyze_sample", args=(str(analysis.aid),))
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
    app.run(host='0.0.0.0', port=80)
