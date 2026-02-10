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
import inspect
import json
from abc import ABC
# Third-party imports
from teatype.logging import *
from teatype.toolkit import generate_id

class _BaseRedisMessage(ABC):
    channel:str
    id:str
    response_requested:bool
    source:str
    type:str

    def __init__(self, channel:str, source:str, response_requested:bool=False) -> None:
        self.channel = channel
        self.source = source
        self.response_requested = response_requested

        # Sets the message type based on the subclass name
        self.id = generate_id(truncate=16)
        self.type = self.__class__.__name__.replace('Redis','').lower()
        
    #################
    # Class methods #
    #################
    
    @classmethod
    def from_dict(cls, data: dict) -> '_BaseRedisMessage':
        """
        Deserialize a dictionary to a RedisMessage instance.

        :param data: Dictionary representing the message data.
        :return: An instance of RedisMessage with the loaded data.
        """
        # Get valid parameter names for the constructor
        sig = inspect.signature(cls.__init__)
        valid_params = set(sig.parameters.keys()) - {'self'}
        
        # Separate constructor args from post-init attributes
        init_data = {key: value for key, value in data.items() if key in valid_params}
        extra_data = {key: value for key, value in data.items() if key not in valid_params}
        
        # Create instance with valid constructor args
        instance = cls(**init_data)
        
        # Set extra attributes (like 'id', 'type') that are generated in __init__
        # but should be preserved from serialized data
        if 'id' in extra_data:
            instance.id = extra_data['id']
        if 'type' in extra_data:
            instance.type = extra_data['type']
        # Preserve response_requested if it exists in data but wasn't a constructor param
        if 'response_requested' in extra_data:
            instance.response_requested = extra_data['response_requested']
            
        return instance
        
    ##############
    # Public API #
    ##############
        
    def dump(self) -> str:
        """
        Serialize the message data to a JSON-formatted string.
        """
        return json.dumps(self.to_dict())
        
    def to_dict(self) -> dict:
        """
        Serialize the message data to a dictionary.
        """
        return {key: value for key, value in self.__dict__.items()}

class RedisBroadcast(_BaseRedisMessage):
    message:str
    value:any
    
    def __init__(self,
                 channel:str,
                 source:str,
                 message:str,
                 value:any=None,
                 response_requested:bool=False) -> None:
        super().__init__(channel, source, response_requested)
        
        self.message = message
        self.value = value

class RedisDispatch(_BaseRedisMessage):
    command:str
    receiver:str
    payload:any
    
    def __init__(self,
                 channel:str,
                 source:str,
                 command:str,
                 receiver:str,
                 payload:any=None,
                 response_requested:bool=False) -> None:
        super().__init__(channel, source, response_requested)
        
        self.command = command
        self.receiver = receiver
        self.payload = payload
        
class RedisResponse(_BaseRedisMessage):
    response_message:str
    response_to:str  # ID of the original message being responded to
    payload:any
    
    def __init__(self,
                 channel:str,
                 source:str,
                 response_to:str,
                 response_message:str='Message processed successfully',
                 payload:any=None) -> None:
        super().__init__(channel, source, response_requested=False)
        
        self.response_message = response_message
        self.response_to = response_to
        self.payload = payload