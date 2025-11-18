# Copyright (C) 2024-2025 Burak Günaydin
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

# Standard library imports
import json
import statistics
import time
# Third-party imports
import msgspec
import orjson
import pytest
import rapidjson
import simdjson
import simplejson
import ujson
from teatype.io import file, path
from teatype.toolkit import fastjson, stopwatch

##########
# PyTest #
##########

@pytest.mark.skip()
def test_empirical_decode_and_read_speed():
    parent_directory = path.caller_parent(reverse_depth=3)
    dist_directory = path.join(parent_directory, 'dist')
    
    # Load file once as bytes
    full_path = path.join(dist_directory, 'full-test-inference.json')
    with open(full_path, 'rb') as f:
        json_bytes = f.read()

    parsers = [
        ('json',        lambda b: json.loads(b.decode('utf-8'))),
        ('ujson',       lambda b: ujson.loads(b.decode('utf-8'))),
        ('orjson',      lambda b: orjson.loads(b)),
        ('simdjson',    lambda b: simdjson.Parser().parse(b)),
        ('msgspec',     lambda b: msgspec.json.decode(b)),
        ('simplejson',  lambda b: simplejson.loads(b.decode('utf-8'))),
        ('rapidjson',   lambda b: rapidjson.loads(b.decode('utf-8'))),
    ]

    n_runs = 1_000 # Number of runs for each parser
    times = { name: [] for name, _ in parsers }

    for _ in range(n_runs):
        for name, fn in parsers:
            t0 = time.perf_counter()
            data = fn(json_bytes)
            times[name].append(time.perf_counter() - t0)

    # Compute mean times and rank
    mean_times = { name: statistics.mean(lst) for name, lst in times.items() }
    ranked = sorted(mean_times.items(), key=lambda x: x[1])

    print(f'\nJSON parsing performance over {n_runs} runs (mean seconds):')
    for i, (name, m) in enumerate(ranked, 1):
        print(f'{i}. {name:<10} {m:.6f}s')

    # Dummy assertion so pytest sees a passing test
    assert ranked
    
@pytest.mark.skip()
def test_empirical_encode_and_write_speed():
    parent_directory = path.caller_parent(reverse_depth=3)
    dist_directory = path.join(parent_directory, 'dist')
    full_path = path.join(dist_directory, 'full-test-inference.json')

    # Load and parse once
    with open(full_path, 'rb') as f:
        json_bytes = f.read()
    data = json.loads(json_bytes.decode('utf-8'))

    # Define encoders (must return bytes)
    encoders = [
        ('json',       lambda o: json.dumps(o).encode('utf-8')),
        ('ujson',      lambda o: ujson.dumps(o).encode('utf-8')),
        ('orjson',     lambda o: orjson.dumps(o)),
        ('msgspec',    lambda o: msgspec.json.encode(o)),
        ('simplejson', lambda o: simplejson.dumps(o).encode('utf-8')),
        ('rapidjson',  lambda o: rapidjson.dumps(o).encode('utf-8')),
    ]

    n_runs = 1_000
    times = { name: [] for name, _ in encoders }

    for _ in range(n_runs):
        for name, fn in encoders:
            t0 = time.perf_counter()
            out_bytes = fn(data)
            times[name].append(time.perf_counter() - t0)

    mean_times = { name: statistics.mean(lst) for name, lst in times.items() }
    ranked = sorted(mean_times.items(), key=lambda x: x[1])

    print(f'\nJSON encode+write performance over {n_runs} runs (mean seconds):')
    for i, (name, m) in enumerate(ranked, 1):
        print(f'{i}. {name:<10} {m:.6f}s')
        
    tmp_out = path.join(dist_directory, 'temp_out.json')
    
    stopwatch('file write json')
    file.write(tmp_out, data, force_format='json')
    stopwatch()
    
    stopwatch('file write json pretty')
    file.write(tmp_out, data, force_format='json', prettify=True)
    stopwatch()
    
    # stopwatch('json dumps')
    # json.dump(data, open(tmp_out, 'w'))
    # stopwatch()
    
    # # Writing (encode)
    # stopwatch('json dump indent 4')
    # json.dump(data, open(tmp_out, 'w'), indent=4)
    # stopwatch()
    
    stopwatch('with open write')
    # Optionally write to file as text
    with open(tmp_out, 'w') as f:
        json_str = json.dumps(data) 
        f.write(json_str)
    stopwatch()
    
    stopwatch('with open write bytes')
    # Write bytes directly to file
    with open(tmp_out, 'wb') as f:
        f.write(json_bytes)
    stopwatch()

    assert ranked
    
def test_compression():
    parent_directory = path.caller_parent(reverse_depth=3)
    dist_directory = path.join(parent_directory, 'dist')
    
    # Example compression map for inference JSON
    # Maps full keys to short keys (maximum available data keys)
    EXAMPLE_COMP_MAP = {
        "confidence": "cf",
        "created_at": "ca",
        "class_name": "cn",
        "class_name_map": "cnm",
        "bounding_box": "bbox",
        "image_id": "imd",
        "predictions": "pd",
        "prediction_sets": "ps",
        "rank": "rk",
        "timestamp": "ts",
        "verified_by_user": "vbu",
        "verified_by_multiModel": "vbm",
        "verified_by_ocr": "vbo",
    }

    data = fastjson.load(path.join(dist_directory, 'full-test-inference.json'))
    flat = fastjson.compress(data, EXAMPLE_COMP_MAP)
    fastjson.dump(flat, path.join(dist_directory, 'compressed-inference.json'))
    
    # # Assuming input is a flat JSON
    # with open(path, 'r') as f:
    #     flat_data = json.load(f)
    # nested = fastjson.decompress(flat_data, EXAMPLE_COMP_MAP)
