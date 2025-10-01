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
from teatype.io import env, path
from teatype.logging import *

# Constants
DEFAULT_MODEL = 'Nous-Hermes-2-Mistral-7B-DPO.Q6_K'
MODELS_PATH = '/root/arsonite/nightshade/dist/llm-models'

class Inferencer():
    def __init__(self,
                 max_tokens:int=2048,
                 temperature:float=0.7,
                 top_p:float=0.9,
                 auto_init:bool=True,
                 model_path:str=None,
                 context_size:int=2048,
                 cpu_cores:int=os.cpu_count(),
                 gpu_layers:int=-1,
                 surpress_output:bool=True):
        
        env.set('LLAMA_SET_ROWS', '1')

        if getattr(self, "_instantiated", False):
            return

        self._instantiated = True

        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

        self.messages: List[Dict[str, str]] = []
        self.chat_history = deque()
        self.game_state_alerts = []

        if auto_init:
            model_path = path.join(MODELS_PATH, DEFAULT_MODEL) + '.gguf' if model_path is None else model_path
            self.initialize(
                model_path=model_path,
                context_size=context_size,
                cpu_cores=cpu_cores,
                gpu_layers=gpu_layers,
                surpress_output=surpress_output
            )