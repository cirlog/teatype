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

# Standard library imports
import os
import sys
from contextlib import contextmanager
# Third-party imports
from llama_cpp import Llama
from teatype.logging import *

def load_model(model_path:str,
               context_size:int=4096,
               cpu_cores:int=os.cpu_count(),
               gpu_layers:int=-1,
               surpress_output:bool=True,
               verbose:bool=False) -> Llama|None:
    """
    Loads a model from the specified path.
    
    Args:
        model_path (str): The (absolute) path to the model file.
        cpu_cores (int): Number of CPU cores to use for processing.
        context_size (int): The context size for the model.
        gpu_layers (int): Number of GPU layers to use, set to 0 for CPU-only or –-1 for GPU depending on VRAM.
    
    Returns:
        Any: The loaded model object.
    """
    @contextmanager
    def suppress_stdout_stderr():
        with open(os.devnull, 'w') as devnull:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            try:
                sys.stdout = devnull
                sys.stderr = devnull
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
    if verbose:
        warn(f'> Loading model with parameters:',
             use_prefix=False)
        warn(f'     - Path: {model_path}',
             use_prefix=False)
        warn(f'     - Context Size: {context_size}',
             use_prefix=False)
        warn(f'     - CPU Cores: {cpu_cores}',
             use_prefix=False)
        warn(f'     - GPU Layers: {gpu_layers}',
             use_prefix=False)
    if surpress_output:
        with suppress_stdout_stderr():
            model = Llama(
                model_path=model_path,
                n_ctx=context_size,
                n_threads=cpu_cores,
                n_gpu_layers=gpu_layers,
                use_mlock=True,
                use_mmap=True,
                verbose=False
            )
    else:
        model = Llama(
            model_path=model_path,
            n_ctx=context_size,
            n_threads=cpu_cores,
            n_gpu_layers=gpu_layers,
            use_mlock=True,
            use_mmap=True,
            verbose=True
        )
    if not model:
        if verbose:
            err(f'Failed to load model. Please check the path and parameters.')
        return None
    if verbose:
        success(f'> Model loaded successfully!')
    return model