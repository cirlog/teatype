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
from typing import List, Optional
# Third-party imports
from teatype.comms.ipc.redis import RedisDispatch, dispatch_handler
from teatype.modulo import ServiceUnit

class BaseAIEngine(ServiceUnit):
    clients:List[str]
    model:object
    
    def __init__(self, verbose_logging:Optional[bool]=False):
        super().__init__(name='ai-engine', verbose_logging=verbose_logging)
        
        self.clients = []
        self.model = None
        
    ############
    # Handlers #
    ############
    
    @dispatch_handler
    def register_client(self, dispatch:RedisDispatch):
        client_designation = dispatch.payload.get('client_designation', None)
        if client_designation not in self.clients:
            self.clients.append(client_designation)
        
    @dispatch_handler
    def unregister_client(self, dispatch:RedisDispatch):
        client_designation = dispatch.payload.get('client_designation', None)
        if client_designation in self.clients:
            self.clients.remove(client_designation)
            
    ##############
    # Public API #
    ##############
    
    def dispatch_to_clients(self, command:str, payload:dict=None) -> None:
        for client in self.clients:
            self.dispatch(command=command,
                          receiver=client,
                          is_async=True,
                          payload=payload)