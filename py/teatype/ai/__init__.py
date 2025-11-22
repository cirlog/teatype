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
    # Local imports
    from .engines.BaseAIEngine import BaseAIEngine
    from .engines.LLMEngine import LLMEngine
    from .models.llm.loader import load_model as load_llm_model
    from .models.llm.inference import Inferencer as LLMInferencer
    from .OpenGPT import OpenGPT
    
    __GPU_SUPPORT__ = True
except:
    __GPU_SUPPORT__ = False