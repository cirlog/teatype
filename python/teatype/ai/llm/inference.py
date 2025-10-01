# Copyright © 2025-2026 @arsonite.
#
# This software and all its associated assets, code, designs, dialogue systems, characters, and in-game logic
# are proprietary and owned exclusively by @arsonite. Permission is granted to the user to install and play
# the game for personal use. Redistribution, resale, modification, reverse-engineering, or reuse of any part
# of the game is strictly prohibited without written permission.
#
# Third-party open-source components are used under their respective licenses.
# See /third-party-licenses.md for details.
#
# THE GAME IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
# NON-INFRINGEMENT, OR TITLE. @arsonite DOES NOT WARRANT THAT THE GAME WILL MEET YOUR
# REQUIREMENTS OR THAT OPERATION OF THE GAME WILL BE UNINTERRUPTED OR ERROR-FREE.
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# System imports
import os

# From system imports
from abc import ABC
from collections import deque
from typing import List, Dict, Optional

# From package imports
from llama_cpp import Llama
from teatype.ai.llm import load_model
from teatype.io import env, file, path
from teatype.logging import *

ROOT_PATH = env.get('TEATYPE_WORKSPACE_PATH')
MODELS_PATH = path.join(ROOT_PATH, 'cli', 'dist', 'llm-models')

class Inferencer():
    max_tokens:int
    model:Optional[Llama]
    temperature:float
    top_p:float
    
    def __init__(self,
                 model:str,
                 model_directory:str=None,
                 max_tokens:int=2048,
                 context_size:int=4096,
                 temperature:float=0.7,
                 cpu_cores:int=os.cpu_count(),
                 gpu_layers:int=-1,
                 auto_init:bool=True,
                 surpress_output:bool=True,
                 top_p:float=0.9,
                 verbose:bool=False):
        """
        Base class for LLM inferencers.
        """
        env.set('LLAMA_SET_ROWS', '1')

        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        
        self.model_name = model
        self.model_directory = model_directory if model_directory else MODELS_PATH
        
        if auto_init:
            self.initialize_model(context_size=context_size,
                                  cpu_cores=cpu_cores,
                                  gpu_layers=gpu_layers,
                                  surpress_output=surpress_output,
                                  verbose=verbose)
    
    def __call__(self, user_prompt:str, stream_response:bool=True) -> str:
        """
        Generate text from LLaMA model.
        
        Args:
            user_prompt (str): The input prompt.
            stream_response (bool): Whether to stream output tokens live.

        Returns:
            str: Final full response.
        """
        response = ''
        if stream_response:
            # Stream tokens as they are generated
            for output in self.model(user_prompt,
                                     max_tokens=self.max_tokens,
                                     temperature=self.temperature,
                                     top_p=self.top_p,
                                     stream=True):
                token = output['choices'][0]['text']
                print(token, end='', flush=True) # live output
                response += token
            print()  # newline after streaming
        else:
            # Normal non-streaming inference
            raw_output = self.model(user_prompt,
                                     max_tokens=self.max_tokens,
                                     temperature=self.temperature,
                                     top_p=self.top_p,
                                     stream=False)
            response = raw_output['choices'][0]['text']
        return response
            
    def initialize_model(self,
                         context_size:int=4096,
                         cpu_cores:int=os.cpu_count(),
                         gpu_layers:int=-1,
                         surpress_output:bool=True,
                         verbose:bool=False,) -> Llama|None:
            """
            Initializes the llama-cpp model with raw prompt-based inference.
            """
            # TODO: Download model if not present from huggingface
            found_model_files = file.list(self.model_directory)
            matching_model = [f for f in found_model_files if self.model_name in f.name][0]
            if not matching_model:
                raise ValueError(f'Model {self.model_name} not found in {MODELS_PATH}. Please place the model file there or specify a different `model_directory`.')

            self.model = load_model(model_path=matching_model.path,
                                    context_size=context_size,
                                    cpu_cores=cpu_cores,
                                    gpu_layers=gpu_layers,
                                    surpress_output=surpress_output,
                                    verbose=verbose)
            self.on_init()
    
    #########
    # Hooks #
    #########
    
    def on_init(self):
        pass