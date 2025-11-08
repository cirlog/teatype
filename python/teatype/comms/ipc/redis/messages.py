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

# Standard library imports
import json
from abc import ABC
# Third-party imports
from teatype.logging import *

class _BaseRedisMessage(ABC):
    channel:str
    source:str
    type:str

    def __init__(self, channel:str, source:str) -> None:
        self.channel = channel
        self.source = source

        # Sets the message type based on the subclass name
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
        init_data = {key: value for key, value in data.items()}
        return cls(**init_data)
        
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
    def __init__(self, channel:str, source:str, message:str, value:any=None) -> None:
        super().__init__(channel, source)
        
        self.message = message
        self.value = value

class RedisDispatch(_BaseRedisMessage):
    def __init__(self, channel:str, source:str, command:str, receiver:str, payload:any=None) -> None:
        super().__init__(channel, source)
        
        self.command = command
        self.receiver = receiver
        self.payload = payload