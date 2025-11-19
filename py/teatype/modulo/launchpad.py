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
import sys
import inspect
from typing import Literal
# Local imports
from teatype.io import path, shell
from teatype.logging import *
from teatype.modulo.units import *
from teatype.toolkit import dt

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
               unit_type:Literal['backend','service','workhorse']|type,
               unit_name:str=None,
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
        if type(unit_type) == str:
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
        else:
            if unit_name is None:
                unit = unit_type.create()
            else:
                unit = unit_type.create(name=unit_name)
        return unit
    
    @classmethod
    def fire(cls,
             unit_type:Literal['backend','service','workhorse']|type,
             unit_name:str=None,
             host:str|None=None,
             port:int|None=None,
             detached:bool=True) -> bool:
        """
        Launch the worker in its own detached process.
        """
        python_executable = sys.executable
        script_directory = path.caller_parent()
        script_path = path.join(script_directory, 'units.py')
        
        if type(unit_type) == str:
            launch_command = f'{python_executable} {script_path} {unit_type} {unit_name}'
            if unit_type == 'backend':
                if host is None or port is None:
                    raise err('Host and port must be specified for backend units.',
                            raise_exception=ValueError)
                launch_command += f' --host={host} --port={port}'
        else:
            class_path = inspect.getfile(unit_type)
            launch_command = f'{python_executable} {class_path}'
            unit_type = unit_type.__name__.lower()
        if detached:
            log_directory = '/tmp/modulo/logs'
            timestamp = dt.now()
            if unit_name is None:
                log_path = f'{log_directory}/{unit_type}-{timestamp}.log'
            else:
                log_path = f'{log_directory}/{unit_type}-{unit_name}-{timestamp}.log'
            path.create('/tmp/modulo/logs')
            launch_command = f'nohup {launch_command} > {log_path} 2>&1 &'
        shell(launch_command, mute=True)
        return True
        
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