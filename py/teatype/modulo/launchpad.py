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
import sys
import inspect
from typing import Literal

# Local imports
from teatype.io import path, shell
from teatype.logging import *
from teatype.modulo.units import *
from teatype.modulo.units.application import ApplicationUnit
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
               unit_type:Literal['application','backend','service','socket','workhorse']|type,
               unit_name:str=None,
               host:str|None=None,
               port:int|None=None,
               dashboard_host:str|None=None,
               dashboard_port:int|None=None,
               include_dashboard:bool=True,
               **kwargs) -> ApplicationUnit|BackendUnit|ServiceUnit|SocketUnit|WorkhorseUnit:
        """
        Launch a Teatype Modulo unit.
        
        Args:
            unit_type: Type of the unit ('application', 'backend', 'service', 'workhorse')
            unit_name: Name of the unit to launch
            host: Optional server host (for backend and application units)
            port: Optional server port (for backend and application units)
            dashboard_host: Optional dashboard host (for application units)
            dashboard_port: Optional dashboard port (for application units)
            include_dashboard: Whether to include React dashboard dev server (for application units)
        
        Returns:
            Instance of the launched unit
        """
        if type(unit_type) == str:
            if unit_type == 'application':
                if host is None:
                    host = '127.0.0.1'
                if port is None:
                    port = 8080
                if dashboard_host is None:
                    dashboard_host = '127.0.0.1'
                if dashboard_port is None:
                    dashboard_port = 5173
                unit = ApplicationUnit.create(
                    name=unit_name,
                    backend_host=host,
                    backend_port=port,
                    dashboard_host=dashboard_host,
                    dashboard_port=dashboard_port,
                    include_dashboard=include_dashboard,
                    **kwargs
                )
            elif unit_type == 'backend':
                if host is None or port is None:
                    raise err('Host and port must be specified for backend units.',
                            raise_exception=ValueError)
                unit = BackendUnit.create(name=unit_name, host=host, port=port, **kwargs)
            elif unit_type == 'service':
                unit = ServiceUnit.create(name=unit_name, **kwargs)
            elif unit_type == 'workhorse':
                unit = WorkhorseUnit.create(name=unit_name, **kwargs)
            elif unit_type == 'socket':
                unit = SocketUnit.create(name=unit_name, **kwargs)
            else:
                raise err(f'Invalid unit type: {unit_type}',
                        raise_exception=ValueError)
        else:
            # TODO: Build in check, that verifies its a subclass of CoreUnit
            if unit_name is None:
                unit = unit_type.create(**kwargs)
            else:
                unit = unit_type.create(name=unit_name, **kwargs)
        return unit
    
    @classmethod
    def fire(cls,
             unit_type:Literal['application','backend','service','socket','workhorse']|type,
             unit_name:str=None,
             host:str|None=None,
             port:int|None=None,
             dashboard_host:str|None=None,
             dashboard_port:int|None=None,
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
            elif unit_type == 'application':
                if host is not None:
                    launch_command += f' --host={host}'
                if port is not None:
                    launch_command += f' --port={port}'
                if dashboard_host is not None:
                    launch_command += f' --dashboard-host={dashboard_host}'
                if dashboard_port is not None:
                    launch_command += f' --dashboard-port={dashboard_port}'
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
                        choices=['application', 'backend', 'service', 'socket', 'workhorse'],
                        help='Type of unit to launch')
    parser.add_argument('unit_name',
                        type=str,
                        help='Name of the unit to launch')
    parser.add_argument('--host',
                        type=str,
                        default=None,
                        help='Server host (required for backend units, optional for application)')
    parser.add_argument('--port',
                        type=int,
                        default=None,
                        help='Server port (required for backend units, optional for application)')
    parser.add_argument('--dashboard-host',
                        type=str,
                        default='127.0.0.1',
                        help='Dashboard dev server host (for application units)')
    parser.add_argument('--dashboard-port',
                        type=int,
                        default=5173,
                        help='Dashboard dev server port (for application units)')
    parser.add_argument('--no-dashboard',
                        action='store_true',
                        help='Disable React dashboard dev server (for application units)')
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
        LaunchPad.fire(
            args.unit_type, 
            args.unit_name, 
            host=args.host, 
            port=args.port,
            dashboard_host=args.dashboard_host if hasattr(args, 'dashboard_host') else None,
            dashboard_port=args.dashboard_port if hasattr(args, 'dashboard_port') else None
        )
    else:
        try:
            if args.unit_type == 'application':
                unit = LaunchPad.create(
                    args.unit_type, 
                    args.unit_name, 
                    host=args.host or '127.0.0.1', 
                    port=args.port or 8080,
                    dashboard_host=args.dashboard_host,
                    dashboard_port=args.dashboard_port,
                    include_dashboard=not args.no_dashboard,
                    verbose_logging=True
                )
            else:
                unit = LaunchPad.create(
                    args.unit_type, 
                    args.unit_name, 
                    host=args.host, 
                    port=args.port, 
                    verbose_logging=True
                )
            # Run unit directly (blocking mode)
            unit.start()
            unit.join()
        except KeyboardInterrupt:
            println()
            hint('\nInterrupted. Shutting down gracefully...', use_prefix=False)
        finally:
            println()