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

# Local imports
from .application import ApplicationUnit
from .core import CoreUnit, parse_designation, print_designation
from .backend import BackendUnit
from .service import ServiceUnit
from .socket import SocketUnit, socket_handler
from .workhorse import WorkhorseUnit

__all__ = [
    'ApplicationUnit',
    'CoreUnit',
    'parse_designation',
    'print_designation',
    'BackendUnit',
    'ServiceUnit',
    'SocketUnit',
    'socket_handler',
    'WorkhorseUnit',
]

if __name__ == '__main__':
    import argparse
    from teatype.logging import *
    
    parser = argparse.ArgumentParser(description='Teatype Modulo unit definitions.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # TODO: Add launch key, so that only Launchpad can execute this script
    parser.add_argument('unit_type',
                        type=str,
                        choices=['backend', 'service', 'socket', 'workhorse'],
                        help='Type of the unit to launch')
    parser.add_argument('unit_name',
                        type=str,
                        help='Name of the unit to launch')
    parser.add_argument('--host',
                        type=str,
                        default=None,
                        help='Host address for backend units')
    parser.add_argument('--port',
                        type=int,
                        default=None,
                        help='Port number for backend units')
    
    args = parser.parse_args()
    unit_type = args.unit_type
    unit_name = args.unit_name
    
    try:
        from teatype.modulo.launchpad import LaunchPad
        println()
        unit = LaunchPad.create(args.unit_type, args.unit_name, host=args.host, port=args.port)
        # Run unit directly (blocking mode)
        unit.start()
        unit.join()
    except KeyboardInterrupt:
        println()
        hint('\nInterrupted. Shutting down gracefully...', use_prefix=False)
    finally:
        println()