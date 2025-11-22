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

# Standard-library imports
from typing import Optional
# Third-party imports
from teatype.comms.ipc.redis import RedisChannel, RedisDispatch, RedisServiceManager, dispatch_handler
from teatype.logging import *
from teatype.modulo.units.core import CoreUnit

class ServiceUnit(CoreUnit):
    """
    Advanced service orchestration unit providing core system management capabilities.
    
    This class implements a robust framework for inter-process communication via Redis,
    shared memory management, state tracking, and unit lifecycle handling.
    """
    def __init__(self, name:str, verbose_logging:Optional[bool]=False) -> None:
        """
        Initialize the service unit with configuration and communication infrastructure.
        
        Args:
            name: Name of the service unit
        """
        super().__init__(name=name, verbose_logging=verbose_logging)
        
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
            self.redis_service = RedisServiceManager(client_name=self.designation,
                                                     owner=self,
                                                     preprocess_function=self._filter_irrelevant_messages,
                                                     verbose_logging=self._verbose_logging)
        except Exception:
            err('Redis infrastructure setup failed.',
                traceback=True)
            
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
            
            if sender == self.id or sender == self.designation:
                return None
                
            if receiver and receiver != 'all' and receiver != self.id and receiver != self.designation:
                return None
                
            return message
        except Exception:
            err(f'Message filtering error', traceback=True)
            return None
        
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

    ##################
    # Redis handlers #
    ##################
    
    @dispatch_handler
    def kill(self, dispatch:RedisDispatch) -> None:
        hint(f'Received "kill" command. Initiating shutdown ...')
        self.shutdown()
    
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
                 is_async:bool=True,
                 payload:any=None,
                 receiver_target:str=None,
                 **kwargs) -> None:
        """
        Dispatch command to a Modulo unit.
        
        Args:
            id (str): ID of the Modulo unit.
            command (str): Command to dispatch.
            is_async (bool): Whether to dispatch asynchronously.
            payload (any): Additional payload data.
        """
        dispatch = RedisDispatch(RedisChannel.COMMANDS.value,
                                 'modulo.operations.dispatch',
                                 command,
                                 receiver,
                                 payload)
        if is_async:
            self.redis_service.send_message(dispatch)
        
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