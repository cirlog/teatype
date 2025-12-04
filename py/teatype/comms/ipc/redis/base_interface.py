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
from abc import ABC
from typing import Dict

class RedisBaseInterface(ABC):
    DEFAULT_HOST='127.0.0.1'
    DEFAULT_PORT=6379
    
    max_buffer_size:int
    message_buffer:Dict[str,any]
    verbose_logging:bool
    
    def __init__(self, max_buffer_size:int, verbose_logging:bool):
        self.max_buffer_size = max_buffer_size
        self.message_buffer = dict()
        self.verbose_logging = verbose_logging
        
    def push_message_to_buffer(self, message_id:str, message:any) -> None:
        """
        Pushes a message to the internal buffer, maintaining the max buffer size.
        """
        self.message_buffer[message_id] = message
        if len(self.message_buffer) > self.max_buffer_size:
            # Remove the oldest message
            oldest_key = next(iter(self.message_buffer))
            del self.message_buffer[oldest_key]
            
    def pop_message_from_buffer(self, message_id:str) -> any:
        """
        Pops a message from the internal buffer by its ID.
        """
        return self.message_buffer.pop(message_id, None)