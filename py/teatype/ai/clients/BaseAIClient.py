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
from teatype.comms.ipc.redis import RedisDispatch, dispatch_handler
from teatype.modulo import ServiceUnit

class BaseAIClient(ServiceUnit):
    model_designation:str
    
    def __init__(self, name:str, verbose_logging:Optional[bool]=None):
        super().__init__(name=name, verbose_logging=verbose_logging)
        
        self.model_designation = None
    
    ##############
    # Public API #
    ##############
        
    def dispatch_to_engine(self, command:str, payload:dict=None) -> None:
        self.dispatch(command=command,
                      receiver=self.model_designation,
                      is_async=True,
                      payload=payload)
        
    def load_model(self, model_path:str):
        self.dispatch_to_engine(command='load_model',
                                payload={'model_path': model_path})
        
    def register_with_engine(self) -> None:
        self.dispatch_to_engine(command='register_client',
                                payload={'client_designation': self.designation})
        
    def unregister_from_engine(self) -> None:
        self.dispatch_to_engine(command='unregister_client',
                                payload={'client_designation': self.designation})
        
    #########
    # Hooks #
    #########
        
    def on_redis_shutdown_before(self) -> None:
        self.unregister_from_engine()