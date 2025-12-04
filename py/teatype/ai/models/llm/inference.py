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
import itertools
import os
import sys
import threading
import time
from typing import Generator, Optional
# Third-party imports
from llama_cpp import Llama
from teatype.ai.models.llm import load_model, PromptBuilder
from teatype.enum import EscapeColor
from teatype.io import env, file, path
from teatype.logging import *
from teatype.toolkit import colorwrap

APPLY_WHITESPACE_PATCH = True

class Inferencer():
    enable_kv_cache:bool
    max_tokens:int
    model:Optional[Llama]
    model_directory:str
    model_extension:str
    model_loaded:bool
    model_name:str
    model_path:str
    temperature:float
    top_p:float
    unlock_full_potential:bool
    
    def __init__(self,
                 model_path:str,
                 max_tokens:int=2048, # The maximum number of tokens to generate in the output - affects length of responses
                 context_size:int=4096, # The context window size of the model - Affects how much text the model can "see" at once
                 temperature:float=0.7, # Affects randomness. Lowering results in less random completions
                 cpu_cores:int=os.cpu_count(),
                 gpu_layers:int=-1,
                 auto_init:bool=True,
                 enable_kv_cache:bool=True,
                 surpress_output:bool=True,
                 top_p:float=0.9, # nucleus sampling - Affects diversity. Lower values makes output more focused
                 unlock_full_potential:bool=False,
                 verbose:bool=False):
        """
        Base class for LLM inferencers.
        """
        env.set('LLAMA_SET_ROWS', '1')

        self.reload(model_path=model_path,
                    max_tokens=max_tokens,
                    context_size=context_size,
                    temperature=temperature,
                    cpu_cores=cpu_cores,
                    gpu_layers=gpu_layers,
                    auto_init=auto_init,
                    enable_kv_cache=enable_kv_cache,
                    surpress_output=surpress_output,
                    top_p=top_p,
                    unlock_full_potential=unlock_full_potential,
                    verbose=verbose)
    
    def __call__(self,
                 user_prompt:str,
                 artificial_delay:float=0.0,
                 colorized_output:EscapeColor.Colors=None,
                 decorator:str=None,
                 show_thinking:bool=True,
                 stream_response:bool=True,
                 use_prompt_builder:bool=True,
                 yield_token:bool=False) -> str|Generator[str, None, None]:
        """
        Generate text from LLaMA model with optional streaming.
        Shows a spinner until the first token or response is available.
        """
        def _spinner(stop_event):
            for symbol in itertools.cycle('|/-\\'):
                if stop_event.is_set():
                    break
                sys.stdout.write('\rThinking ' + symbol)
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write('\r' + ' ' * 20 + '\r') # clear line
            
        response = ''
        if use_prompt_builder:
            input = PromptBuilder(user_prompt, unlock_full_potential=self.unlock_full_potential)
        else:
            input = user_prompt

        first_token = True
        if show_thinking:
            # Spinner setup
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=_spinner, args=(stop_event,))
            spinner_thread.start()
        
        if artificial_delay > 0:
            time.sleep(artificial_delay)

        if not self.enable_kv_cache:
            self.model.reset()
        if decorator:
            print(decorator + ':', end=' ', flush=True)
        if stream_response:
            for output in self.model(
                input,
                max_tokens=self.max_tokens,
                stop=['User:', '\nUser:', '\n\nUser:'], # Stop generation when user prompt is detected again
                stream=True,
                temperature=self.temperature,
                top_p=self.top_p
            ):
                token = output['choices'][0]['text']
                    
                if first_token: 
                    if show_thinking:
                        stop_event.set() # stop spinner when first token arrives
                        spinner_thread.join()
                        
                    first_token = False
                    if APPLY_WHITESPACE_PATCH:
                        token = token.lstrip() # Strip leading whitespace only once at the start

                if yield_token:
                    yield token
                else:
                    if colorized_output:
                        print(colorwrap(token, colorized_output), end='', flush=True)
                    else:
                        print(token, end='', flush=True)
                    response += token
            println()
        else:
            raw_output = self.model(
                input,
                max_tokens=self.max_tokens,
                stop=['User:', '\nUser:', '\n\nUser:'], # Stop generation when user prompt is detected again
                stream=False,
                temperature=self.temperature,
                top_p=self.top_p
            )
            if show_thinking:
                stop_event.set()
                spinner_thread.join()
            response = raw_output['choices'][0]['text']

        # Strip leading newlines/whitespace only once at the start
        return response.lstrip()
    
    def reload(self,
               model_path:str,
               max_tokens:int=2048,
               context_size:int=4096,
               temperature:float=0.7,
               cpu_cores:int=os.cpu_count(),
               gpu_layers:int=-1,
               auto_init:bool=True,
               enable_kv_cache:bool=True,
               surpress_output:bool=True,
               top_p:float=0.9,
               unlock_full_potential:bool=False,
               verbose:bool=False):
        self.enable_kv_cache = enable_kv_cache
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.unlock_full_potential = unlock_full_potential
        
        self.model_directory = self.model_path.rsplit('/', 1)[0]
        self.model_extension = self.model_path.rsplit('.', 1)[-1]
        self.model_loaded = False
        self.model_name = self.model_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        
        if auto_init:
            self.initialize_model(context_size=context_size,
                                  cpu_cores=cpu_cores,
                                  gpu_layers=gpu_layers,
                                  surpress_output=surpress_output,
                                  verbose=verbose)
            
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
                raise ValueError(f'Model {self.model_name} not found in {self.model_path}. Please place the model file there or specify a different `model_path`.')

            self.model = load_model(model_path=matching_model.path,
                                    context_size=context_size,
                                    cpu_cores=cpu_cores,
                                    gpu_layers=gpu_layers,
                                    surpress_output=surpress_output,
                                    verbose=verbose)
            self.model_loaded = True
            self.on_init()
    
    #########
    # Hooks #
    #########
    
    def on_init(self):
        pass
    
if __name__ == '__main__':
        from teatype.io import prompt
        
        verbose = True
        
        parent_directory = path.caller_parent(reverse_depth=2)
        cli_directory = path.join(parent_directory, 'cli')
        cli_dist_directory = path.join(cli_directory, 'dist')
        model_directory = path.join(cli_dist_directory, 'llm-models')
        conversational_model_directory = path.join(model_directory, 'conversational')
        if not path.exists(conversational_model_directory):
            warn(f'Conversational model directory not found at {conversational_model_directory}. Creating it. Please re-run this script after placing your model there.',
                 use_prefix=False)
            path.create(conversational_model_directory)
            println()
            exit(1)

        stream = True
        
        default_model_file_path = path.join(conversational_model_directory, 'default-model.txt')
        if not file.exists(default_model_file_path):
            file.write(default_model_file_path, '')
        
        default_model = file.read(default_model_file_path).strip()
        if default_model == '' or default_model is None:
            hint('No default model set. Select one of these available local models:',
                 use_prefix=False)
            available_local_models = [f.name.split('.gguf')[0] for f in file.list(conversational_model_directory, only_include='.gguf')]
            prompt_options = {str(i+1): model_name for i, model_name in enumerate(available_local_models)}
            for available_model_index, available_model_name in prompt_options.items():
                model_file_path = path.join(conversational_model_directory, f'{available_model_name}.gguf')
                file_size = file.size(model_file_path, human_readable=True)
                log(f'  [{available_model_index}] {available_model_name} ({file_size})')
            selection = prompt('Please enter the number corresponding to your choice:',
                               options=prompt_options,
                               return_bool=False)
            default_model = available_local_models[int(selection)-1]
            file.write(default_model_file_path, default_model)
        
        default_model = file.read(path.join(conversational_model_directory, 'default-model.txt'))
        
        user_prompt = prompt('Enter your prompt:', return_bool=False)
        
        from teatype.ai.models.llm import Inferencer
        llm = Inferencer(model=default_model,
                         model_directory=conversational_model_directory)
        response = llm(user_prompt=user_prompt,
                       stream_response=stream)
        println()