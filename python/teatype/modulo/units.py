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

# From system imports
import threading
import time
from queue import LifoQueue
from typing import List

# From package imports
from teatype.enum import EscapeColor
from teatype.logging import *
from teatype.comms.ipc.redis import *
from teatype.toolkit import generate_id

class _CoreUnit(threading.Thread):
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
    id:str
    loop_idle_time:float
    loop_iter:int
    
    def __init__(self, name:str, type:str, verbose_logging:bool=True) -> None:
        """
        Initialize the service unit with configuration and communication infrastructure.
        
        Args:
            config_paths: Optional list of directories to search for configuration files
            config_file: Optional explicit path to configuration file
        """
        super().__init__()
        
        self.name = name
        self.type = type
        self._verbose_logging = verbose_logging
        
        self.id = generate_id(truncate=16)
        self.pod = 0 # Enumeration for units with the same name
        self.designation = f'unit:{self.type}:{self.name}:{self.pod}:{self.id}'
        self.loop_idle_time = 1.0
        self.loop_iter = 0
        
        self._command_buffer = LifoQueue(10)
        self._history_stack = LifoQueue()
        self._status = None
        self._shutdown_in_progress = False
        
        log(f'Initialized unit:')
        log(f'  {EscapeColor.CYAN}Name:        {EscapeColor.MAGENTA}{self.name}')
        log(f'  Type:        {self.type}')
        log(f'  ID:          {self.id}')
        log(f'  Pod:         {self.pod}')
        log(f'  Designation: {self.designation}')
        
    def __new__(cls, *args, **kwargs):
        if not cls._ALLOW_DIRECT_INSTANTIATION:
            raise TypeError(
                'Direct instantiation of _CoreUnit baseclasses is not allowed. '
                'Use Subclass.create() or better yet, Launchpads to instantiate appropriate worker units.'
            )
        return super().__new__(cls)
    
    #################
    # Class methods #
    #################
    
    @classmethod
    def create(cls, **kwargs) -> '_CoreUnit':
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
    
class BackendUnit(_CoreUnit):
    def __init__(self, name:str) -> None:
        """
        Initialize the backend unit.
        
        Args:
            name: Name of the backend unit
        """
        super().__init__(name=name, type='backend')
    
class ServiceUnit(_CoreUnit):
    """
    Advanced service orchestration unit providing core system management capabilities.
    
    This class implements a robust framework for inter-process communication via Redis,
    shared memory management, state tracking, and unit lifecycle handling.
    """
    
    def __init__(self, name:str) -> None:
        """
        Initialize the service unit with configuration and communication infrastructure.
        
        Args:
            name: Name of the service unit
        """
        super().__init__(name=name, type='service')
        
        self._setup_redis_infrastructure()
        self._register()
        
    #############
    # Internals #
    #############
    
    def _setup_redis_infrastructure(self) -> None:
        """
        Initialize Redis connection and message routing.
        """
        try:
            self.redis_service = RedisServiceManager(preprocess_function=self._default_message_preprocessor,
                                                     verbose_logging=self._verbose_logging)
        except Exception:
            err('Redis infrastructure setup failed.',
                traceback=True)
            
    def _default_message_preprocessor(self, message:any) -> any:
        """
        Default message preprocessor to filter irrelevant messages.
        
        Args:
            msg: Incoming Redis message
            
        Returns:
            Processed message or None if irrelevant
        """
        message = self._filter_irrelevant_messages(message)
        if message == None:
            return None
        message = self._react_to_kill_command(message)
            
    def _filter_irrelevant_messages(self, message:any) -> any:
        """
        Filter out messages not intended for this unit.
        
        Args:
            msg: Incoming Redis message
            
        Returns:
            Message if relevant, None otherwise
        """
        try:
            sender = message.get('sender')
            receiver = message.get('receiver')
            
            if sender == self.designation:
                return None
                
            if receiver and receiver != 'all' and receiver != self.designation:
                return None
                
            return message
        except Exception:
            err(f'Message filtering error', traceback=True)
            return None
        
    def _react_to_kill_command(self, message:any) -> any:
        """
        React to 'kill' command messages by initiating shutdown.
        
        Args:
            msg: Incoming Redis message
            
        Returns:
            Message if not a kill command, None otherwise
        """
        try:
            command = message.get('command', None)
            if command != None and command == 'kill':
                hint(f'Received "kill" command. Initiating shutdown ...')
                self.shutdown()
                return None
            return message
        except Exception:
            err(f'Kill command processing error', traceback=True)
            return message
        
    def _register(self) -> None:
        """
        Register the service unit in the unit registry.
        """
        try:
            pass
        except Exception:
            err(f'Unit registration error', traceback=True)
        
    def _terminate_redis_connection(self) -> None:
        """
        Close Redis connection and cleanup unit registry.
        """
        try:
            # self._unregister()
            self.redis_service.terminate()
        except Exception:
            err(f'Redis termination error', traceback=True)
        
    ##############
    # Properties #
    ##############
    
    @property
    def is_connected(self) -> bool:
        """
        Check if the service unit is connected to Redis.
        
        Returns:
            Connection status
        """
        return self.redis_service.pool.is_connected
    
    @property
    def is_subscribed(self) -> bool:
        """
        Check if the service unit is subscribed to Redis channels.
        
        Returns:
            Subscription status
        """
        return self.redis_service.pool.is_subscribed
    
    ##############
    # Public API #
    ##############
    
    def broadcast(self,
                  message:str,
                  value:any=None,
                  **kwargs) -> None:
        pass
        
    def dispatch(self, 
                 command:str,
                 receiver:str,
                 payload:any=None,
                 **kwargs) -> None:
        pass
        
    def updateStatus(self, new_status:str, broadcast:bool=True) -> None:
        """
        Update the service unit's status.
        
        Args:
            new_status: New status string
        """
        self._status = new_status
        self._history_stack.put(new_status)
        
        if broadcast:
            self.broadcast(message='status-update', value=new_status)
        
    def shutdown(self, force:bool=False) -> None:
        """
        Gracefully terminate the service unit and cleanup resources.
        
        Args:
            force: If True, bypass shutdown-in-progress check
        """
        if not force and self._shutdown_in_progress:
            print('Shutdown already in progress')
            return
        
        self._shutdown_in_progress = True
            
        self.on_redis_shutdown_before()
            
        try:
            hint('Commencing shutdown procedure ...')
            self._terminate_redis_connection()
        except Exception:
            err(f'Shutdown failed', traceback=True,
                raise_exc=True)
            
        self.on_redis_shutdown_after()
    
class WorkhorseUnit(_CoreUnit):
    """
    Lightweight one-shot worker unit for specialized tasks within the Teatype Modulo framework.
    """
    def __init__(self, name:str) -> None:
        """
        Initialize the workhorse unit.
        
        Args:
            name: Name of the workhorse unit
        """
        super().__init__(name=name, type='workhorse')