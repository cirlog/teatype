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

try:
    # Local imports
    from .launchpad import LaunchPad
    from .operations import Operations
    from .operations import Operations as ModuloOperations
    from .units.core import CoreUnit, parse_designation, print_designation
    from .units.service import ServiceUnit
    from .units.workhorse import WorkhorseUnit
    
    __MODULO_IMPORT_ERROR__ = None
    __MODULO_SUPPORT__ = True
except ImportError as ie:
    __MODULO_IMPORT_ERROR__ = ie
    __MODULO_SUPPORT__ = False
    
from .tracer import Tracer

def __getattr__(name):
    # Lazily import the hsdb registry so fastapi/uvicorn only load when it is used
    if name == 'hsdb':
        global hsdb
        from teatype.modulo.hsdb import hsdb
        return hsdb
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")