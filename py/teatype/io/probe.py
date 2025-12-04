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
import importlib
import sys

# Third-party imports
from teatype.logging import *

def ip(ip: str) -> bool:
    pass

def memory(obj:object, print_results:bool=False) -> int:
    def _get_size(obj, seen=None):
        """
        Recursively finds size of objects in bytes
        """
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        
        target_id = id(obj)
        if target_id in seen:
            return 0
        
        seen.add(target_id)
        
        if isinstance(obj, dict):
            size += sum([_get_size(v, seen) for v in obj.values()])
            size += sum([_get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += _get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([_get_size(i, seen) for i in obj])
        return size
            
    memory_bytes = _get_size(obj)
    if print_results:
        memory_kb = memory_bytes / 1024
        memory_mb = memory_kb / 1024
        print(f'\nMemory footprint of {obj.__class__.__name__}:')
        print(f'  {memory_bytes:,} bytes')
        print(f'  {memory_kb:.2f} KB')
        print(f'  {memory_mb:.4f} MB')
    return memory_bytes

def port(port: int) -> bool:
    pass

def package(package_name:str, silent:bool=True) -> bool:
    try:
        importlib.import_module(package_name)
        return True
    except:
        if not silent:
            err(f'Probe failed: Package {package_name} not found')
        return False

def process(process: str) -> bool:
    pass

def url(url: str) -> bool:
    pass