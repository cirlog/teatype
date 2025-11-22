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
import time
from enum import Enum
from typing import Callable, Dict, List, Optional, Union
# Third-party imports
from teatype.logging import *
# Local imports
from teatype.comms.ipc.redis.base_interface import RedisBaseInterface
from teatype.comms.ipc.redis.connection_pool import RedisConnectionPool
from teatype.comms.ipc.redis.message_processor import RedisMessageProcessor

# TODO: Figure out how to make request-response patterns work with Redis pub/sub
class RedisServiceManager(RedisBaseInterface):
    """
    Comprehensive Redis service manager with connection pooling and message handling.
    """
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
                                                       verbose_logging=verbose_logging)
        # Start message processing
        self.message_processor.start()
        
        if self.verbose_logging:
            success('Redis service manager initialized.')
        
    def send_message(self,
                     message:object,
                     channel:Optional[str]=None,
                     is_async:bool=True,
                     timeout:float=10.0) -> dict|None:
        self.pool.send_message(message, channel)
        if not is_async:
            message_id = message.id
            # Wait for response
            waited_time = 0.0
            poll_interval = 0.01
            while waited_time < timeout:
                if message_id in self.response_buffer:
                    return self.response_buffer.pop(message_id, None)
                time.sleep(poll_interval)
                waited_time += poll_interval
            err(f'Timeout waiting for response to message with ID: {message_id}')
            return None
    
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