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
from teatype.logging import err, success

class ConversationalAI(LLMInferencer):
    def initialize(self,
                   model_path:str,
                   context_size:int=2048,
                   cpu_cores:int=os.cpu_count(),
                   gpu_layers:int=-1,
                   chat_format:Optional[str]=None,
                   surpress_output:bool=True):
        """
        Initializes the llama-cpp model with raw prompt-based inference.
        """
        self.llm = Llama(
            model_path=model_path,
            n_ctx=context_size,
            n_threads=cpu_cores,
            n_gpu_layers=gpu_layers,
            verbose=not surpress_output
        )
        self.initialized = True

    def reset_chat(self):
        """Clears conversation history and alerts."""
        self.chat_history.clear()
        self.game_state_alerts.clear()

    def add_game_state_alert(self, alert: str):
        """Adds a game event/system message."""
        self.game_state_alerts.append(f"[GAME_EVENT]: {alert}")

    def build_prompt(self, player_action:Optional[str], player_prompt:str) -> str:
        """
        Assembles the full prompt string including system, game, chat, and player info.
        Accepts player_action as optional (empty string allowed).
        """
        prompt = self.system_prompt + "\n\n"

        for alert in self.game_state_alerts:
            prompt += f"{alert}\n"

        for entry in self.chat_history:
            prompt += f"Player: {entry['player']}\n"
            prompt += f"NPC: {entry['npc']}\n"

        # Only add player_action if it is not None or empty
        if player_action and player_action.strip():
            prompt += f"Player action: {player_action.strip()}\n"

        prompt += f"Player says: {player_prompt}\n"
        prompt += "NPC:"

        return prompt

    def predict(self, player_action: Optional[str], player_prompt: str, stream: bool = False) -> Dict[str, Optional[str]]:
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
        
        import pprint
        pprint.pprint(output)
        
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

        # Stream the npc text nicely
        self._simulate_stream(npc_text)

    def _parse_structured_output(self, output: str) -> Dict[str, Optional[str]]:
        """
        Extracts the structured reply block from the model output.
        """
        import re
        parsed = {}

        sections = {
            'npc': r'### NPC:\n(.*?)(?=###|$)',
            'mood': r'### Mood:\n(.*?)(?=###|$)',
            'friendship': r'### Friendship:\n(.*?)(?=###|$)',
            'action': r'### Action:\n(.*?)(?=###|$)',
        }

        for key, pattern in sections.items():
            match = re.search(pattern, output, re.DOTALL)
            if match:
                parsed[key] = match.group(1).strip()
            else:
                parsed[key] = None

        return parsed

    def _simulate_stream(self, text: str, delay: float = 0.05):
        """
        Simulate streaming output character-by-character after parsing is done,
        like a typical LLM streaming response.

        Args:
            text (str): The full NPC response text to stream.
            delay (float): Delay in seconds between characters.
        """
        import sys
        import time

        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print() # newline after finishing simulated stream