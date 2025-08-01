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

# System imports
import json
import pprint

# Package imports
import orjson

# From system imports
from typing import Any, Dict, List, Union

# From package imports
from simdjson import Parser, Object, Array

JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

simdjson_parser = Parser()

def compress(data:JSONType,
                  compression_map:Dict[str, str],
                  delimiter:str=".",
                  flatten:bool=False) -> JSONType:
    """
    :param data: JSON data to compress
    :param compression_map: full → short key map
    :param delimiter: used only when flatten=True
    :param flatten: if True, returns a flat dict; else, nested with renamed keys
    """
    if not flatten:
        def _recurse(obj: Any) -> JSONType:
            if isinstance(obj, dict):
                return {
                    compression_map.get(k, k): _recurse(v)
                    for k, v in obj.items()
                }
            if isinstance(obj, list):
                return [_recurse(item) for item in obj]
            return obj
        return _recurse(data)

    # existing flatten algorithm
    flat: Dict[str, Any] = {}
    def _flat(obj: Any, parents: List[str]):
        if isinstance(obj, dict):
            for k, v in obj.items():
                ck = compression_map.get(k, k)
                _flat(v, parents + [ck])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _flat(v, parents + [str(i)])
        else:
            flat[delimiter.join(parents)] = obj

    _flat(data, [])
    return flat

def decompress(flat:Union[Dict[str, Any], JSONType],
                    compression_map:Dict[str, str],
                    delimiter:str=".",
                    flatten:bool=False) -> JSONType:
    """
    :param flat: flat dict if flatten=True, else nested with compressed keys
    :param compression_map: full→short key map
    :param delimiter: used only when flatten=True
    :param flatten: should match the flag used in compress_json
    """
    inv_map = {v: k for k, v in compression_map.items()}

    if not flatten:
        def _recurse(obj: Any) -> JSONType:
            if isinstance(obj, dict):
                return {
                    inv_map.get(k, k): _recurse(v)
                    for k, v in obj.items()
                }
            if isinstance(obj, list):
                return [_recurse(item) for item in obj]
            return obj
        return _recurse(flat)  # type: ignore

    # existing un-flatten algorithm
    root: Dict[str, Any] = {}
    for compound_key, value in flat.items():  # type: ignore
        parts = compound_key.split(delimiter)
        cur: Any = root
        for idx, part in enumerate(parts):
            orig = inv_map.get(part, part)
            last = (idx == len(parts) - 1)
            if not last:
                nxt = parts[idx + 1]
                if nxt.isdigit():
                    cur = cur.setdefault(orig, [])
                else:
                    cur = cur.setdefault(orig, {})
            else:
                if part.isdigit() and isinstance(cur, list):
                    i = int(part)
                    while len(cur) <= i:
                        cur.append(None)
                    cur[i] = value
                else:
                    cur[orig] = value
    return root

def dump(data:JSONType, file_path:str) -> None:
    """
    Dump JSON data to a file.
    
    :param data: JSON data to write.
    :param file_path: Path to the output file.
    """
    with open(file_path, 'wb') as f:
        orjson_bytes = orjson.dumps(data)
        f.write(orjson_bytes)

def load(file_path:str) -> JSONType:
    """
    Load JSON data from a file.
    
    :param file_path: Path to the JSON file.
    :return: Parsed JSON data.
    """
    with open(file_path, 'rb') as f:
        json_bytes = f.read()
        
    simdjson_object = simdjson_parser.parse(json_bytes)
    if isinstance(simdjson_object, Object):
        return simdjson_object.as_dict()
    elif isinstance(simdjson_object, Array):
        return simdjson_object.as_list()
    else:
        raise TypeError(f'Unsupported top-level JSON type: {type(simdjson_object)}')

def pretty_print(data:JSONType) -> str:
    pprint.pprint(data, indent=4, width=80, compact=True)
    # return json.dumps(data, indent=4)