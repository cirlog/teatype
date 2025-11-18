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
    """
    You're looking at a standard “lazy-import” pattern for a package and in short accomplishes:
        - reduced startup time (by deferring imports until first use)
        - cut down memory usage (never import unused bits)
        - and most importantly: avoid import-time side-effects or circular dependenciews
    """
    import llama_cpp
    
    __GPU_SUPPORT__ = True
    
    __all__ = ['AnalyticalAI',
               'ConversationalAI',
               'Inferencer',
               'load_model',
               'PromptBuilder']
    
    # from .models.analytical import AnalyticalAI
    # from .models.conversational import ConversationalAI
    # from .loader import load_model
    # from .inference import Inferencer
    # from .prompt_builder import PromptBuilder

    def __getattr__(name):
        if name == 'AnalyticalAI':
            from .models.analytical import AnalyticalAI
            return AnalyticalAI
        if name == 'ConversationalAI':
            from .models.conversational import ConversationalAI
            return ConversationalAI
        if name == 'load_model':
            from .loader import load_model
            return load_model
        if name == 'Inferencer':
            from .inference import Inferencer
            return Inferencer
        if name == 'PromptBuilder':
            from .prompt_builder import PromptBuilder
            return PromptBuilder
        raise AttributeError(f'module "llm" has no attribute "{name}"')
except:
    __GPU_SUPPORT__ = False