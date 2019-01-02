import sys
import os
import daemon
import emulators
import emulators.analysis

samples_path = os.path.abspath(sys.argv[1])
samples = os.listdir(samples_path)


def add_sample(code, engine):
    # Create new analysis
    analysis = emulators.analysis.Analysis()
    # Add sample code to analysis
    analysis.add_sample(code, engine, filename="sample.js")
    # Spawn task to daemon
    daemon.analyze_sample.apply_async((str(analysis.aid), {}))
    # Return analysis id
    return analysis.aid

for file_path in samples:
    with open(os.path.join(samples_path, file_path), "r") as f:
        code = f.read()
        add_sample(code, "JScript.Encode")
