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
import threading
import time
from queue import LifoQueue
from typing import Optional, Union

# Third-party imports
from teatype.comms.ipc.redis import *
from teatype.enum import EscapeColor
from teatype.logging import *
from teatype.toolkit import generate_id, kebabify

def parse_designation(designation:str) -> dict[Union[str,str|int]]:
    """
    Parse a Teatype Modulo unit designation string into its components.

    Args:
        designation: The designation string to parse.

    Returns:
        A dictionary containing the parsed components.
    """
    parts = designation.split(':')
    if len(parts) != 7 or parts[0] != 'teatype':
        err('Invalid designation format and/or not a teatype-module',
            raise_exception=ValueError)

    return {
        'type': parts[3],
        'name': parts[4],
        'pod': int(parts[5]),
        'id': parts[6]
    }
    
def print_designation(designation:str) -> None:
    """
    Print the components of a Teatype Modulo unit designation string.

    Args:
        designation: The designation string to print. 
    """
    info = parse_designation(designation)
    log(f'  {EscapeColor.MAGENTA}Name: {EscapeColor.CYAN}{info["name"]}')
    log(f'  {EscapeColor.MAGENTA}Type: {EscapeColor.CYAN}{info["type"]}')
    log(f'  {EscapeColor.MAGENTA}ID:   {EscapeColor.CYAN}{info["id"]}')
    log(f'  {EscapeColor.MAGENTA}Pod:  {EscapeColor.CYAN}{info["pod"]}')
    log(f'  {EscapeColor.MAGENTA}Designation: {EscapeColor.CYAN}{designation}')

class CoreUnit(threading.Thread):
    """
    Base class for Teatype Modulo units.
    """
    _ALLOW_DIRECT_INSTANTIATION:bool=False
    
    _command_buffer:LifoQueue
    _history_stack:LifoQueue
    _status:str|None
    _shutdown_in_progress:bool
    _verbose_logging:bool
    
    designation:str
    name:str
    id:str
    loop_idle_time:float
    loop_iter:int
    type:str
    
    def __init__(self, name:str, verbose_logging:Optional[bool]=True) -> None:
        """
        Initialize the service unit with configuration and communication infrastructure.
        
        Args:
            config_paths: Optional list of directories to search for configuration files
            config_file: Optional explicit path to configuration file
        """
        super().__init__()
        
        self.name = name
        self.type = kebabify(self.__class__.__name__.replace('Unit', ''))
        self._verbose_logging = verbose_logging
        
        self.id = generate_id(truncate=16)
        self.pod = 0 # Enumeration for units with the same name
        # TODO: Make PID part of designation to allow external process management
        self.designation = f'teatype:modulo:unit:{self.type}:{self.name}:{self.pod}:{self.id}'
        self.loop_idle_time = 1.0
        self.loop_iter = 0
        
        self._command_buffer = LifoQueue(10)
        self._history_stack = LifoQueue()
        self._status = None
        self._shutdown_in_progress = False
        
        if self._verbose_logging:
            log(f'Initialized unit:')
            print_designation(self.designation)
        
    def __new__(cls, *args, **kwargs):
        if not cls._ALLOW_DIRECT_INSTANTIATION:
            raise TypeError('Direct instantiation of CoreUnit baseclasses is not allowed. \nUse Subclass.create() or better yet, Launchpads to instantiate appropriate worker units.')
        return super().__new__(cls)
    
    #################
    # Class methods #
    #################
    
    @classmethod
    def create(cls, **kwargs) -> 'CoreUnit':
        cls._ALLOW_DIRECT_INSTANTIATION = True
        try:
            return cls(**kwargs)
        finally:
            cls._ALLOW_DIRECT_INSTANTIATION = False
    
    ##############
    # Public API #
    ##############
    
    def run(self) -> None:
        self.on_loop_start()
        
        println()
        if self._verbose_logging:
            log('Running main loop')
        while not self._shutdown_in_progress:
            self.on_loop_run()
            time.sleep(self.loop_idle_time)
            self.loop_iter += 1
            
        self.on_loop_end()
            
    #########
    # Hooks #
    #########
    
    def on_loop_start(self) -> None:
        """
        Hook method called on the first run of the unit.
        """
        pass
    
    def on_loop_run(self) -> None:
        """
        Hook method called on each iteration of the unit's main loop.
        """
        pass
    
    def on_loop_end(self) -> None:
        """
        Hook method called on the termination of the unit.
        """
        pass
    
    def on_redis_shutdown_before(self) -> None:
        """
        Hook method called before Redis connection is terminated.
        """
        pass
    
    def on_redis_shutdown_after(self) -> None:
        """
        Hook method called after Redis connection is terminated.
        """
        pass