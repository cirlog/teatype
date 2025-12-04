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
from typing import Optional
# Third-party imports
from teatype.ai.engines.BaseAIEngine import BaseAIEngine
from teatype.ai.models.llm.inference import Inferencer
from teatype.comms.ipc.redis import dispatch_handler, RedisDispatch

class LLMEngine(BaseAIEngine):
    def __init__(self, verbose_logging:Optional[bool]=False):
        super().__init__(verbose_logging=verbose_logging)
        
    ############
    # Handlers #
    ############
    
    @dispatch_handler
    def load_model(self, dispatch:RedisDispatch) -> None:
        payload = dispatch.payload
        model_path = payload.get('model_path', None)
        if model_path is None:
            err('No model path provided in the payload.', verbose=False)
            return
        
        if self.model is None:
            self.model = Inferencer(enable_kv_cache=False,
                                    model_path=model_path,
                                    verbose=self._verbose_logging)
        
    @dispatch_handler
    def prompt(self, dispatch:RedisDispatch) -> None:
        payload = dispatch.payload
        user_prompt = payload.get('user_prompt', None)
        if user_prompt is None:
            err('No user prompt provided in the payload.', verbose=False)
            return
        
        generator = self.model(show_thinking=False,
                               stream_response=True,
                               user_prompt=user_prompt,
                               yield_token=True)
        
        self.dispatch_to_clients(command='prompt_response',
                                 payload={'message': '/startllm'})
        for token in generator:
            self.dispatch_to_clients(command='prompt_response',
                                     payload={'message': token})
        self.dispatch_to_clients(command='prompt_response',
                                 payload={'message': '/endllm'})

if __name__ == '__main__':
    try:
        # Third-party imports
        from teatype.logging import *
        # Local imports
        from teatype.modulo.launchpad import LaunchPad
        
        unit = LaunchPad.create(LLMEngine, verbose_logging=True)
        # Run unit directly (blocking mode)
        unit.start()
        unit.join()
    except KeyboardInterrupt:
        println()
        hint('\nInterrupted. Shutting down gracefully...', use_prefix=False)
    finally:
        println()