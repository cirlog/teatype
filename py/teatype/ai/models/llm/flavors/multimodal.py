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
import os
from abc import ABC
from collections import deque
from typing import List, Dict, Optional
# Third-party imports
from llama_cpp import Llama
from teatype.ai.models.llm import Inferencer, PromptBuilder
from teatype.enum import EscapeColor
from teatype.io import env, path
from teatype.logging import *

class MultimodalInferencer(Inferencer):
    """
    Extension of Inferencer that supports multimodal models
    (e.g. LLaVA, Fuyu, Qwen-VL) which accept image input alongside text.
    """
    def __init__(self,
                 model:str,
                 mmproj:str=None,  # path to mmproj file for multimodal models
                 model_directory:str=None,
                 max_tokens:int=2048,
                 context_size:int=4096,
                 temperature:float=0.7,
                 cpu_cores:int=os.cpu_count(),
                 gpu_layers:int=-1,
                 auto_init:bool=True,
                 surpress_output:bool=True,
                 top_p:float=0.9,
                 unlock_full_potential:bool=False,
                 verbose:bool=False):
        self.mmproj = mmproj
        super().__init__(model=model,
                         model_directory=model_directory,
                         max_tokens=max_tokens,
                         context_size=context_size,
                         temperature=temperature,
                         cpu_cores=cpu_cores,
                         gpu_layers=gpu_layers,
                         auto_init=auto_init,
                         surpress_output=surpress_output,
                         top_p=top_p,
                         unlock_full_potential=unlock_full_potential,
                         verbose=verbose)

    def initialize_model(self,
                         context_size:int=4096,
                         cpu_cores:int=os.cpu_count(),
                         gpu_layers:int=-1,
                         surpress_output:bool=True,
                         verbose:bool=False) -> Llama|None:
        """
        Initializes a multimodal llama-cpp model with optional mmproj file.
        """
        found_model_files = file.list(self.model_directory)
        matching_model = [f for f in found_model_files if self.model_name in f.name][0]
        if not matching_model:
            raise ValueError(
                f'Model {self.model_name} not found in {MODELS_PATH}. '
                f'Please place the model file there or specify a different `model_directory`.'
            )

        # Here we explicitly pass mmproj_path if provided
        self.model = Llama(
            model_path=matching_model.path,
            mmproj_path=self.mmproj,
            n_ctx=context_size,
            n_threads=cpu_cores,
            n_gpu_layers=gpu_layers,
            verbose=verbose
        )
        self.on_init()
        
    def __call__(self,
                 user_prompt: str,
                 images: Optional[List[str]] = None,
                 artificial_delay: float = 0.0,
                 colorized_output: EscapeColor.Colors = None,
                 decorator: str = None,
                 show_thinking: bool = True,
                 stream_response: bool = True,
                 use_prompt_builder: bool = True) -> str:
        """
        Erweitert __call__ um die Fähigkeit, Bilder zu übergeben.
        `images` ist eine Liste von Dateipfaden zu Bildern.
        """
        def _spinner(stop_event):
            for symbol in itertools.cycle('|/-\\'):
                if stop_event.is_set():
                    break
                sys.stdout.write('\rThinking ' + symbol)
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write('\r' + ' ' * 20 + '\r')  # clear line

        response = ''
        if use_prompt_builder:
            input = PromptBuilder(user_prompt,
                                  unlock_full_potential=self.unlock_full_potential)
        else:
            input = user_prompt

        if show_thinking:
            first_token = True
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=_spinner, args=(stop_event,))
            spinner_thread.start()

        if artificial_delay > 0:
            time.sleep(artificial_delay)

        if decorator:
            print(decorator + ':', end=' ', flush=True)

        # ---- WICHTIGER PART: llama-cpp unterstützt jetzt `images=[...]` ----
        call_kwargs = dict(
            prompt=input,
            max_tokens=self.max_tokens,
            stop=['User:', '\nUser:', '\n\nUser:'],
            temperature=self.temperature,
            top_p=self.top_p
        )
        if images:
            call_kwargs["images"] = images  # Liste von Pfaden übergeben

        if stream_response:
            for output in self.model(stream=True, **call_kwargs):
                token = output['choices'][0]['text']

                if show_thinking:
                    if first_token:
                        stop_event.set()
                        spinner_thread.join()
                        first_token = False
                        if APPLY_WHITESPACE_PATCH:
                            token = token.lstrip()

                if colorized_output:
                    print(colorwrap(token, colorized_output), end='', flush=True)
                else:
                    print(token, end='', flush=True)
                response += token
            println()
        else:
            raw_output = self.model(stream=False, **call_kwargs)
            if show_thinking:
                stop_event.set()
                spinner_thread.join()
            response = raw_output['choices'][0]['text']

        return response.lstrip()
