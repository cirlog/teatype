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
import atexit
import json
import threading
from abc import ABC
from collections import OrderedDict
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Package imports
import redis
from teatype.logging import *

# Local imports
from teatype.comms.ipc.redis.base_interface import RedisBaseInterface
from teatype.comms.ipc.redis.connection_pool import RedisConnectionPool
from teatype.comms.ipc.redis.message_processor import RedisMessageProcessor

class RedisServiceManager(RedisBaseInterface):
    """
    Comprehensive Redis service manager with connection pooling and message handling.
    """
    message_processor:RedisMessageProcessor
    pool:RedisConnectionPool
    
    def __init__(self,
                 channels:Optional[List[Union[str,Enum]]]=None,
                 on_shutdown:Optional[Callable]=None,
                 preprocess_function:Optional[Callable]=None,
                 verbose_logging:bool=True) -> None:
        super().__init__(verbose_logging=verbose_logging)
        
        # Initialize components
        self.pool = RedisConnectionPool(verbose_logging=verbose_logging)
        
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
                                                       preprocess_function=preprocess_function,
                                                       verbose_logging=verbose_logging)
        
        # Start message processing
        self.message_processor.start()
        
        success('Redis service manager initialized.')
    
    def terminate(self) -> None:
        """
        Cleanup all resources and close connections.
        """
        try:
            if self.message_processor and self.message_processor._is_active:
                self.message_processor.shutdown()
                self.message_processor.join(timeout=5)
            
            self.pool.terminate_connection()
            
            # Cleanup references
            self.message_processor = None
            
            log("Redis service terminated cleanly")
            
        except Exception as exc:
            err(f"Error during termination: {exc}")