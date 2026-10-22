# Copyright (C) 2024-2026 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# Standard-library imports
import importlib.util
import json
import sys

# Local imports
from teatype.modulo.tracer.workhorse import Workhorse

"""
Subprocess entry point of a Workhorse.

Invoked as: python -m teatype.modulo.tracer.runner <script_path>

Reads the JSON payload from stdin, imports the workload script, finds its Workhorse
and runs the steps with the payload.
"""

def run(script_path:str, payload:dict=None) -> None:
    spec = importlib.util.spec_from_file_location('workload', script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    workhorse = next((attr for attr in vars(module).values() if isinstance(attr, Workhorse)), None)
    if workhorse is None:
        print(f'No Workhorse instance found in {script_path}', file=sys.stderr)
        sys.exit(1)
    
    for step in workhorse.steps:
        step(payload)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python -m teatype.modulo.tracer.runner <script_path>', file=sys.stderr)
        sys.exit(1)
    
    payload_raw = sys.stdin.read()
    run(sys.argv[1], json.loads(payload_raw) if payload_raw.strip() else None)
