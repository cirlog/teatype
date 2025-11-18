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

# Third-party imports
from teatype.comms.ipc.redis import dispatch_handler, RedisDispatch
from teatype.ai.engines.BaseAIEngine import BaseAIEngine

class OpenGPT(BaseAIEngine):
    # The goal of this class is to build a fully featured multi-modal AI assistant with almost the same
    # capabilities as ChatGPT, but running locally on the user's machine.
    # This includes:
    # - Text generation - LLM (chat, code, etc.)
    # - Image generation - StableDiffusion (from text prompts)
    # - Image understanding - CLIP/OCR (captioning, OCR, etc)
    # - Audio understanding (transcription, etc)
    # - File understanding (parsing, summarization, etc)
    # - Memory (short-term and long-term)
    # - Tool use (web search, calculator, etc)
    # - Agent capabilities (reasoning, planning, etc)

    def __init__(self):
        super().__init__()
    
if __name__ == '__main__':
    try:
        # Third-party imports
        from teatype.logging import *
        # Local imports
        from teatype.modulo.launchpad import LaunchPad
        
        unit = LaunchPad.create(OpenGPT)
        # Run unit directly (blocking mode)
        unit.start()
        unit.join()
    except KeyboardInterrupt:
        println()
        hint('\nInterrupted. Shutting down gracefully...', use_prefix=False)
    finally:
        println()