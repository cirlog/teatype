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

class RedisMessageProcessor(RedisBaseInterface, threading.Thread):
    """
    Asynchronous message processor with handler routing.
    """
    
    def __init__(self,
                 pubsub:redis.client.PubSub,
                 on_shutdown:Optional[Callable]=None,
                 preprocess_function:Optional[Callable]=None,
                 verbose_logging:bool=True) -> None:
        threading.Thread.__init__(self, daemon=True)
        super().__init__(verbose_logging=verbose_logging)
        
        self._pubsub_instance = pubsub
        self._message_handlers = dict()
        
        self._is_active = False
        self._shutdown_event = threading.Event()
        self._message_handler_lock = threading.RLock()
        self._preprocess_function = preprocess_function
        
        if on_shutdown:
            atexit.register(on_shutdown)
    
    def register_handler(self,
                         message_class:type,
                         callable:callable,
                         listen_channels:List[str]|None=None) -> bool:
        """
        Register message handler
        """
        try:
            message_type = message_class.__name__.replace('Redis', '').lower()
            with self._message_handler_lock:
                if message_type not in self._message_handlers:
                    self._message_handlers[message_type] = []
                self._message_handlers[message_type].append({
                    'callable': callable,
                    'listen_channels': listen_channels
                })
                return True
        except Exception:
            err(f'Handler registration error', traceback=True)
            return False
    
    def clear_all_handlers(self) -> None:
        """
        Clear all registered handlers.
        """
        with self._message_handler_lock:
            self._message_handlers.clear()
    
    def receive(self, raw_message:Union[str,bytes,int]) -> None:
        """
        Process and route incoming message.
        """
        if isinstance(raw_message, int):
            return # Skip subscription confirmations
        
        try:
            # Decode if needed
            if isinstance(raw_message, bytes):
                raw_message = raw_message.decode('utf-8')
            
            # Parse JSON
            try:
                message_data = json.loads(raw_message)
            except json.JSONDecodeError:
                err(f'JSON decode error', traceback=True)
                return
            
            # Extract message type
            message_type = message_data.get('type')
            if not message_type:
                err('Message missing "type" field')
                return
            
            message_data = self._preprocess_function(message_data) if self._preprocess_function else message_data
            if message_data is None:
                return
            
            # Route to handler
            with self._message_handler_lock:
                handler_config = self._message_handlers.get(message_type)
                
                if not handler_config:
                    err(f'No handler for message type: {message_type}')
                    return
                
                # Channel filtering
                if handler_config['channels']:
                    channel = message_data.get('channel')
                    if not channel:
                        err('Message missing "channel" field')
                        return
                    
                    if channel not in handler_config['channels']:
                        return # Filtered by channel
                
                # Execute handler
                handler_config['callback'](message_data)
            
        except Exception as exc:
            err(f'Message dispatch error', traceback=True)
    
    def shutdown(self) -> None:
        """
        Signal thread to stop processing.
        """
        self._shutdown_event.set()
    
    def run(self) -> None:
        """
        Main message processing loop.
        """
        self._is_active = True
        log('Message processor started')
        try:
            for message in self._pubsub_instance.listen():
                if self._shutdown_event.is_set():
                    break
                
                data = message.get('data')
                try:
                    self.receive(data)
                except Exception:
                    err(f'Processing error', traceback=True)
        except (ValueError, redis.ConnectionError):
            if self._is_active:
                err(f'Connection error')
        except Exception:
            err(f'Fatal processor error', traceback=True)
        finally:
            warn('Message processor stopped')
            self._is_active = False