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
from enum import Enum
from typing import Callable, Dict, List, Optional, Union
# Third-party imports
from teatype.logging import *
# Local imports
from teatype.comms.ipc.redis.base_interface import RedisBaseInterface
from teatype.comms.ipc.redis.connection_pool import RedisConnectionPool
from teatype.comms.ipc.redis.message_processor import RedisMessageProcessor
from teatype.comms.ipc.redis.messages import RedisResponse

# TODO: Figure out how to make request-response patterns work with Redis pub/sub
class RedisServiceManager(RedisBaseInterface):
    """
    Comprehensive Redis service manager with connection pooling and message handling.
    """
    _client_name:Optional[str]
    _pending_responses:Dict[str,threading.Event]
    _response_data:Dict[str,any]
    _response_lock:threading.RLock
    message_processor:RedisMessageProcessor
    pool:RedisConnectionPool
    
    def __init__(self,
                 client_name:Optional[str]=None,
                 channels:Optional[List[Union[str,Enum]]]=None,
                 max_buffer_size:int=100,
                 on_shutdown:Optional[Callable]=None,
                 owner:Optional[object]=None,
                 preprocess_function:Optional[Callable]=None,
                 verbose_logging:Optional[bool]=False) -> None:
        super().__init__(max_buffer_size=max_buffer_size,
                         verbose_logging=verbose_logging)
        
        self._client_name = client_name
        self._pending_responses = dict()
        self._response_data = dict()
        self._response_lock = threading.RLock()
        
        # Initialize components
        self.pool = RedisConnectionPool(client_name=client_name,
                                        verbose_logging=verbose_logging)
        # Establish connection
        if not self.pool.establish_connection():
            raise err('Failed to establish Redis connection. Is Redis server running?',
                      raise_exception=ConnectionError)
        # Subscribe to channels
        if not self.pool.subscribe_channels(channels or []):
            raise err('Failed to subscribe to Redis channels',
                      raise_exception=RuntimeError)
        
        # Initialize store and processor
        self.message_processor = RedisMessageProcessor(pubsub=self.pool.pubsub,
                                                       on_shutdown=on_shutdown,
                                                       owner=owner,
                                                       preprocess_function=preprocess_function,
                                                       response_callback=self._handle_response,
                                                       send_response_callback=self._send_auto_response,
                                                       verbose_logging=verbose_logging)
        # Start message processing
        self.message_processor.start()
        
        if self.verbose_logging:
            success('Redis service manager initialized.')
    
    #############
    # Internals #
    #############
    
    def _handle_response(self, response:RedisResponse) -> None:
        """
        Internal callback to handle incoming response messages.
        Called by the message processor when a response is received.
        """
        response_to = response.response_to
        with self._response_lock:
            if response_to in self._pending_responses:
                self._response_data[response_to] = response
                self._pending_responses[response_to].set()
    
    def _send_auto_response(self,
                            original_message:object,
                            response_message:str='Message processed successfully',
                            payload:any=None) -> None:
        """
        Internal callback used by message processor to send automatic responses.
        """
        response = RedisResponse(
            channel=original_message.channel,
            source=self._client_name or 'unknown',
            response_to=original_message.id,
            response_message=response_message,
            payload=payload
        )
        self.pool.send_message(response)
        
    ##############
    # Public API #
    ##############
        
    def send_message(self,
                     message:object,
                     channel:Optional[str]=None,
                     await_response:bool=False,
                     response_timeout:float=10.0) -> RedisResponse|None:
        """
        Send a message to a Redis channel.
        
        Args:
            message: The message object to send (must have .channel and .dump() methods)
            channel: Optional channel override for simple string messages
            await_response: If True, block and wait for a response
            response_timeout: Timeout in seconds when awaiting response
            
        Returns:
            RedisResponse if await_response=True and response received, None otherwise
        """
        # Set response_requested flag on the message if awaiting response
        if await_response and hasattr(message, 'response_requested'):
            message.response_requested = True
        
        message_id = message.id
        
        if await_response:
            # Create event for this message
            response_event = threading.Event()
            with self._response_lock:
                self._pending_responses[message_id] = response_event
        
        # Send the message
        self.pool.send_message(message, channel)
        
        if await_response:
            # Wait for response
            received = response_event.wait(timeout=response_timeout)
            
            with self._response_lock:
                # Cleanup
                self._pending_responses.pop(message_id, None)
                response = self._response_data.pop(message_id, None)
            
            if not received or response is None:
                if self.verbose_logging:
                    err(f'Timeout waiting for response to message with ID: {message_id}')
                return None
            
            return response
        
        return None
    
    def send_response(self,
                      original_message:object,
                      response_message:str='Message processed successfully',
                      payload:any=None,
                      channel:Optional[str]=None) -> bool:
        """
        Manually send a response to a received message.
        
        Args:
            original_message: The original message being responded to (must have .id and .channel)
            response_message: The response message text
            payload: Optional payload data to include in the response
            channel: Optional channel override (defaults to original message's channel)
            
        Returns:
            bool: True if response was sent successfully
        """
        response = RedisResponse(
            channel=channel or original_message.channel,
            source=self._client_name or 'unknown',
            response_to=original_message.id,
            response_message=response_message,
            payload=payload
        )
        return self.pool.send_message(response)
    
    def terminate(self) -> None:
        """
        Cleanup all resources and close connections.
        """
        try:
            if self.message_processor and self.message_processor._is_active:
                self.message_processor.shutdown()
                # self.message_processor.join(timeout=5)
            
            self.pool.safely_terminate_connection()
            
            # Cleanup references
            self.message_processor = None
            
            log("Redis service terminated cleanly")
            
        except Exception as exc:
            err(f"Error during termination: {exc}")