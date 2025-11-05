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
import os
import sys
import subprocess
from typing import Literal

# Local imports
from teatype.io import path
from teatype.modulo.units import *

class LaunchPad:
    """
    Launcher for Teatype Modulo applications.
    """
    ##############
    # Interfaces #
    ##############
    
    # TODO: write decorators that enforce type checks on create and fire methods
    
    #################
    # Class methods #
    #################
    
    @classmethod
    def create(cls,
               unit_name:str,
               unit_type:Literal['backend','service','workhorse'],
               host:str|None=None,
               port:int|None=None) -> BackendUnit|ServiceUnit|WorkhorseUnit:
        """
        Launch a Teatype Modulo unit.
        
        Args:
            unit_name: Name of the unit to launch
            unit_type: Type of the unit ('backend', 'service', 'workhorse')
            host: Optional server host
            port: Optional server port
        
        Returns:
            Instance of the launched unit
        """
        if unit_type == 'backend':
            if host is None or port is None:
                raise err('Host and port must be specified for backend units.',
                          raise_exception=ValueError)
            unit = BackendUnit.create(name=unit_name, host=host, port=port)
        elif unit_type == 'service':
            unit = ServiceUnit.create(name=unit_name)
        elif unit_type == 'workhorse':
            unit = WorkhorseUnit.create(name=unit_name)
        else:
            raise err(f'Invalid unit type: {unit_type}',
                      raise_exception=ValueError)
        return unit
    
    @classmethod
    def fire(cls,
             unit_name:str,
             unit_type:Literal['backend','service','workhorse'],
             host:str|None=None,
             port:int|None=None) -> bool:
        """
        Launch the worker in its own detached process.
        """
        python_executable = sys.executable
        script_path = path.caller()
        print(python_executable)
        print(script_path)
        
        return

        # DETACHED process flags
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200

        subprocess.Popen(
            [python_exe, script_path, worker_id],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            close_fds=True,
            start_new_session=True  # Unix only
        )
        print(f"Worker '{worker_id}' launched.")
        
if __name__ == "__main__":
    import argparse
    
    println()
    
    parser = argparse.ArgumentParser(
        description='Launch Teatype Modulo units',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('unit_type',
                        type=str,
                        choices=['backend', 'service', 'workhorse'],
                        help='Type of unit to launch')
    parser.add_argument('unit_name',
                        type=str,
                        help='Name of the unit to launch')
    parser.add_argument('--host',
                        type=str,
                        default=None,
                        help='Server host (required for backend units)')
    parser.add_argument('--port',
                        type=int,
                        default=None,
                        help='Server port (required for backend units)')
    parser.add_argument('--detached',
                        action='store_true',
                        help='Launch unit in detached mode')
    args = parser.parse_args()
    
    # Validate backend-specific requirements
    if args.unit_type == 'backend':
        if args.host is None or args.port is None:
            parser.error('--host and --port are required for backend units')
    
    # Launch the unit
    if args.detached:
        LaunchPad.fire(args.unit_name, args.unit_type, host=args.host, port=args.port)
    else:
        try:
            unit = LaunchPad.create(args.unit_name, args.unit_type, host=args.host, port=args.port)
            # Run unit directly (blocking mode)
            unit.start()
            unit.join()
        except KeyboardInterrupt:
            println()
            hint('\nInterrupted. Shutting down gracefully...', use_prefix=False)
        finally:
            println()