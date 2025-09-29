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

try:
    import llama_cpp
    
    __all__ = ['Inferencer', 'PromptBuilder']

    def __getattr__(name):
        if name == "Inferencer":
            from .inference import Inferencer
            return Inferencer
        if name == "PromptBuilder":
            from .prompt_builder import PromptBuilder
            return PromptBuilder
        raise AttributeError(f"module 'llm' has no attribute '{name}'")

    from .loader import load_model
    from .inference import Inferencer
    
    __GPU_SUPPORT__ = True
except:
    __GPU_SUPPORT__ = False