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
from teatype.ai import LLMInferencer
from teatype.io import env, path
from teatype.logging import *

class ConversationalAI(LLMInferencer):
    chat_history:deque
    messages:List[Dict[str, str]]
    
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
                 top_p:float=0.9):
        super().__init__(model=model,
                         model_directory=model_directory,
                         max_tokens=max_tokens,
                         context_size=context_size,
                         temperature=temperature,
                         cpu_cores=cpu_cores,
                         gpu_layers=gpu_layers,
                         auto_init=auto_init,
                         surpress_output=surpress_output,
                         top_p=top_p)

        self.chat_history = deque() # Store past interactions
        self.messages = []

    def reset_chat(self):
        """
        Clears conversation history and alerts.
        """
        self.chat_history.clear()

    def prompt(self, player_action: Optional[str], player_prompt: str, stream: bool = False) -> Dict[str, Optional[str]]:
        """
        Performs a streamed prompt-based inference and extracts structured NPC response.

        Returns:
            dict: Parsed NPC response structure with keys 'npc', 'mood', 'friendship', 'action'.
        """
        if not self.initialized:
            err('Inferencer not initialized. Call initialize().')
            return {}

        prompt = self.build_prompt(player_action, player_prompt)

        # Streaming or non-streaming loop from llama-cpp
        output =  self.llm(prompt=prompt,
                           max_tokens=self.max_tokens,
                           temperature=self.temperature,
                           top_p=self.top_p,
                           stop=["Player says:", "Player:", "### NPC:"])
        
        # Edge case for mistral models
        raw_text = output['choices'][0]['text']
        npc_dialogue, npc_analysis = raw_text.strip().split("### Mood:")
        reconstructed_output = f"### NPC:\n{npc_dialogue.strip()}\n### Mood:{npc_analysis.strip()}"
        # print(reconstructed_output)

        # Cap history size by rough token count (words count as proxy)
        while sum(len(turn['player'].split()) + len(turn['npc'].split()) for turn in self.chat_history) > self.max_tokens:
            self.chat_history.popleft()

        # Parse structured output block from the raw output
        parsed_response = self._parse_structured_output(reconstructed_output)

        npc_text = parsed_response.get('npc') or ''
        if not npc_text:
            err("Warning: NPC response missing or empty.")

        # Save only parsed npc text in history if you want
        self.chat_history.append({
            'player': player_prompt,
            'npc': npc_text
        })