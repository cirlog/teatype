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
import atexit
import json
import inspect
import threading
from typing import Callable, Dict, List, Optional, Union
# Third-party imports
import redis
from teatype.logging import *
# Local imports
from teatype.comms.ipc.redis.messages import RedisDispatch
from teatype.comms.ipc.redis.base_interface import RedisBaseInterface

class RedisMessageProcessor(RedisBaseInterface, threading.Thread):
    """
    Asynchronous message processor with handler routing.
    """
    _is_active:bool
    _message_handler_lock:threading.RLock
    _message_handlers:Dict[str,List[Dict[str,any]]]
    _preprocess_function:Optional[Callable]
    _pubsub_instance:redis.client.PubSub
    _shutdown_event:threading.Event
    
    def __init__(self,
                 pubsub:redis.client.PubSub,
                 max_buffer_size:int=100,
                 on_shutdown:Optional[Callable]=None,
                 owner:Optional[object]=None,
                 preprocess_function:Optional[Callable]=None,
                 verbose_logging:Optional[bool]=False) -> None:
        threading.Thread.__init__(self, daemon=True)
        super().__init__(max_buffer_size=max_buffer_size,
                         verbose_logging=verbose_logging)
        
        self._pubsub_instance = pubsub
        self._message_handlers = dict()
        
        self._is_active = False
        self._shutdown_event = threading.Event()
        self._message_handler_lock = threading.RLock()
        self._preprocess_function = preprocess_function
        
        if owner:
            try:
                # Scan the owner for methods decorated with @redis_handler and register them.
                # Returns the number of handlers registered.
                registered = 0
                for name in dir(owner):
                    attr = getattr(owner, name, None)
                    if attr is None:
                        continue

                    info = getattr(attr, '_redis_handler_info', None)
                    if not info:
                        continue

                    # attr is a bound method when retrieved via instance
                    message_class = info['message_class']
                    listen_channels = info['listen_channels']
                    ok = self.register_handler(
                        message_class=message_class,
                        callable=attr,
                        listen_channels=listen_channels,
                    )
                    if ok:
                        if self.verbose_logging:
                            log(f'Autowired redis handler "{name}" for message class "{message_class.__name__}"')
                        registered += 1
                if self.verbose_logging:
                    log(f'Autowired {registered} redis handler(s) from owner {owner.__class__.__name__}')
            except Exception:
                pass
        
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
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                err(f'JSON decode error', traceback=True)
                return
            
            # Extract message type
            message_type = message.get('type')
            if not message_type:
                err('Message missing "type" field')
                return
            
            message = self._preprocess_function(message) if self._preprocess_function else message
            if message is None:
                return
            
            # Route to handler
            with self._message_handler_lock:
                handlers = self._message_handlers.get(message_type)
                
                if not handlers:
                    err(f'No handler for message type: {message_type}')
                    return
                    
                if message_type == 'dispatch':
                    command = message.get('command', None)
                    print(command)
                    if command is None:
                        err('Dispatch message missing "command" field')
                        return
                    matching_handlers = [handler for handler in handlers if command == handler['callable'].__name__]
                    if len(matching_handlers) == 0:
                        warn(f'No handler for dispatch command: {command}')
                        return
                    # Execute the matching handler
                    matching_handlers[0]['callable'](message)
                else:
                    channel = message.get('channel', None)
                    # Execute handlers
                    for handler in handlers:
                        # Channel filtering
                        if handler['listen_channels'] is not None:
                            if channel not in handler['listen_channels']:
                                continue
            
                        handler['callable'](message)
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
        if self.verbose_logging:
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

# TODO: Convert a duplicate key that uses '-' instead of '_' so have options
def dispatch_handler(function:callable):
    """
    Marks an instance method as a dispatch handler.
    The processor will discover and register it via .autowire(owner).
    Ensures the decorated function has the signature (self, dispatch:object).
    """
    signature = inspect.signature(function)
    params = list(signature.parameters.values())
    if len(params) != 2 or params[0].name != 'self' or params[1].name != 'dispatch':
        raise TypeError(
            f"@dispatch_handler-decorated function '{function.__qualname__}' must have signature (self, dispatch:object)"
        )
    setattr(function, '_redis_handler_info', {
        'message_class': RedisDispatch,
        'listen_channels': None
    })
    return function

def redis_handler(message_class:type, listen_channels:list[str]|None=None):
    """
    Marks an instance method as a Redis handler.
    The processor will discover and register it via .autowire(owner).
    Ensures the decorated function has the signature (self, message:object).
    """
    def decorator(function:callable):
        signature = inspect.signature(function)
        params = list(signature.parameters.values())
        if len(params) != 2 or params[0].name != 'self' or params[1].name != 'message':
            raise TypeError(
                f"@redis_handler-decorated function '{function.__qualname__}' must have signature (self, message:object)"
            )
        setattr(function, '_redis_handler_info', {
            'message_class': message_class,
            'listen_channels': listen_channels
        })
        return function
    return decorator