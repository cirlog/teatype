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
from teatype.ai.clients.BaseAIClient import BaseAIClient
from teatype.modulo.operations import Operations
from teatype.logging import *

class LLMClient(BaseAIClient):
    def __init__(self, auto_fire:bool=False, verbose_logging:Optional[bool]=False):
        super().__init__(name='l-l-m-client', verbose_logging=verbose_logging)
        
        # Discover LLM Engine unit and store its designation
        operations = Operations(verbose_logging=False if verbose_logging == None else verbose_logging)
        units = operations.list(filters=[('type', 'l-l-m-engine')])
        del operations
        if len(units) == 0:
            if auto_fire:
                import time
                from teatype.ai.engines import LLMEngine
                from teatype.modulo.launchpad import LaunchPad
                LaunchPad.fire(LLMEngine)
                time.sleep(2.0)
            else:
                raise RuntimeError('No LLM Engine unit found. Please start the LLM Engine first.')
        self.model_designation = units[0].get('designation')
        
    def dispatch(self, command:str, payload:dict=None) -> None:
        super().dispatch(command=command,
                         receiver=self.model_designation,
                         is_async=True,
                         payload=payload)
        
    def load_model(self, model_path:str):
        self.dispatch(command='load_model',
                      payload={'model_path': model_path})
        
    def chat(self, message:str):
        self.dispatch(command='prompt',
                      payload={'user_prompt': message})