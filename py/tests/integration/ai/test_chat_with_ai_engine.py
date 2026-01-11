#!/usr/bin/env python3.13

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

# Third-party imports
from teatype import colorwrap
from teatype.ai.models.llm import ConversationalAI
from teatype.cli import BaseTUI
from teatype.io import fetch, path, prompt
from teatype.logging import *

def test_chat_with_ai_engine():
    println()

    parent_directory = path.caller_parent(reverse_depth=2)
    cli_dist_directory = path.join(parent_directory, 'dist')
    model_directory = path.join(cli_dist_directory, 'llm-models')
    conversational_model_directory = path.join(model_directory, 'conversational')
    if not path.exists(conversational_model_directory):
        warn(f'Conversational model directory not found at {conversational_model_directory}. Creating it. Please re-run this script after placing your model there.',
                use_prefix=False)
        path.create(conversational_model_directory)
        println()
        return

    stream = True
    llm = ConversationalAI(model='google/gemma-2b',
                           model_directory=conversational_model_directory,
                           temperature=0.9,
                           top_p=0.9,
                           verbose=True)
    println()
    log(colorwrap('[LLM]:', 'cyan'))
    response = llm.chat('Instruction: Greet the user.', stream_response=stream)
    try:
        while True:
            user_input = prompt('[You]:', return_bool=False)
            if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                println()
                break
            println()
            log(colorwrap('[LLM]:', 'cyan'))
            response = llm.chat(user_input, stream_response=stream)
            if not stream:
                print(response)
    except KeyboardInterrupt:
        println()