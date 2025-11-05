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
from teatype.comms.ipc.redis.channels import RedisChannel

class RedisConnectionPool(RedisBaseInterface):
    """
    Manages Redis connections with pooling and health checks.
    """
    _active_subscriptions:set
    _connection:redis.Redis
    _connection_lock:threading.RLock
    _is_connected:bool
    
    DEFAULT_DECODE_RESPONSES=True
    
    pubsub:redis.client.PubSub
    
    def __init__(self, verbose_logging:bool=True):
        super().__init__(verbose_logging)
        
        self._active_subscriptions = set()
        self._connection = None
        self._connection_lock = threading.RLock()
        self._is_connected = False
        
        self.pubsub = None
        
    #############
    # Internals #
    #############
    
    def _verify_connection(self) -> bool:
        """
        Verify connection health via ping.
        """
        try:
            return self._connection.ping() if self._connection else False
        except (redis.ConnectionError, redis.TimeoutError):
            return False
        
    def _unsubscribe_all(self) -> bool:
        """
        Unsubscribe from all active channels.
        """
        if not self._active_subscriptions:
            return True
        try:
            self.pubsub.unsubscribe(*self._active_subscriptions)
            self._active_subscriptions.clear()
            return True
        except Exception as exc:
            err(f'Unsubscribe error: {exc}')
            return False
    
    def _validate_state(self) -> bool:
        """
        Validate connection state before operations.
        """
        if not self._connection:
            err('Connection not initialized')
            return False
        if not self._is_connected:
            err('Not connected to Redis server')
            return False
        return True
    
    @staticmethod
    def _normalize_channels(channels:List[Union[str,Enum]]) -> List[str]:
        """
        Convert channel enums to string values.
        """
        return [channel.value if isinstance(channel, Enum) else channel for channel in channels]
    
    ##############
    # Public API #
    ##############
        
    def establish_connection(self,
                             host:str=RedisBaseInterface.DEFAULT_HOST,
                             port:int=RedisBaseInterface.DEFAULT_PORT,
                             decode_responses:bool=DEFAULT_DECODE_RESPONSES,
                             verbose:bool=True) -> bool:
        """
        Establish connection with comprehensive error handling.
        
        Args:
            host (str): Redis server host.
            port (int): Redis server port.
            decode_responses (bool): Whether to decode responses.
            verbose (bool): Enable verbose logging.
            
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        with self._connection_lock:
            try:
                self._connection = redis.Redis(
                    host=host,
                    port=port,
                    decode_responses=decode_responses,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30
                )
                
                # Verify connection with ping
                if not self._verify_connection():
                    raise redis.ConnectionError('Ping verification failed')
                
                self.pubsub = self._connection.pubsub(ignore_subscribe_messages=True)
                self._is_connected = True
                
                if verbose:
                    log(f'Redis connection established: {host}:{port}')
                
                return True
            except redis.RedisError as exc:
                self._is_connected = False
                if verbose:
                    err(f'Redis connection failed: {exc}')
                return False
            except Exception as exc:
                self._is_connected = False
                if verbose:
                    err(f'Unexpected connection error: {exc}')
                return False
    
    def safely_terminate_connection(self) -> bool:
        """
        Safely close connection and cleanup resources.
        """
        with self._connection_lock:
            if not self._connection:
                return True
            
            try:
                if self.pubsub:
                    self._unsubscribe_all()
                    self.pubsub.close()
                    
                self._connection.close()
                self._is_connected = False
                success('Redis connection terminated gracefully.')
                return True
            except Exception as exc:
                err(f'Error during connection termination: {exc}')
                self._is_connected = False
                return False
    
    def subscribe_channels(self, channels:List[Union[str, Enum]]) -> bool:
        """
        Subscribe to multiple channels with validation.
        
        Args:
            channels (List[Union[str, Enum]]): Channels to subscribe to.
            verbose (bool): Enable verbose logging.
            
        Returns:
            bool: True if subscription is successful, False otherwise.
        """
        if not self._validate_state():
            return False
        
        try:
            channel_names = self._normalize_channels(channels or list(RedisChannel))
            self.pubsub.subscribe(*channel_names)
            self._active_subscriptions.update(channel_names)
            
            if self.verbose_logging:
                log(f"Subscribed to channels: {channel_names}")
            return True
            
        except redis.RedisError as exc:
            err(f"Channel subscription failed: {exc}")
            return False
    
    def send_message(self, message:object, channel:Optional[str]=None) -> bool:
        """
        Publish message to Redis channel.
        """
        if not self._validate_state():
            return False
        
        try:
            if isinstance(message, str):
                if not channel:
                    err("Channel required for simple string messages")
                    return False
                self._connection.publish(channel, message)
            else:
                self._connection.publish(message.channel, message.dump())
            return True
            
        except redis.RedisError as exc:
            err(f"Message publish failed: {exc}")
            return False
    
    @property
    def is_alive(self) -> bool:
        """
        Check if connection is active and healthy.
        """
        return self._is_connected and self._verify_connection()