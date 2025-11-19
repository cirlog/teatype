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
from typing import List, Union

class TokenMap:
    def __init__(self, index:int=0, weight:float=1.0):
        self.index = index
        self.weight = weight

class LLMToken:
    def __init__(self, value:str, map:'TokenMap'=None):
        self.value = value
        self.map = map if map else TokenMap()

class TokenIndex:
    _db:dict
    
    def __init__(self, token_index_path:str, tokens:Union[str, 'LLMToken']):
        self.db = {}

def enrich(llm_token:'LLMToken', epochs:int=1) -> dict:
    """
    Enriches a token by adding additional metadata or context through iterative LLM calls, basically training the model on-the-fly.
    This function can be customized to add specific attributes to the token.

    Args:
        token (str): The token to be enriched.
        epochs (int): Number of iterations to refine the token's metadata.
    Returns:
        dict: A dictionary containing the enriched token data.
    """
    return {
        'index': 0,
        'weight': 1.0,
        'value': llm_token
    }

def tokenize(raw_llm_output:str, llm_tokens:List['LLMToken']) -> dict:
    """
    Tokenizes the output from the LLM.
    It extracts keywords and their weights from the output string and binds them to keywords saved 
    in the softwawre kernel, so that the program understands the context of the output.

    Args:
        llm_output (str): The output string from the LLM.

    Returns:
        dict: A sanitized data structure containing the tokenized output with weighted keywords.
    """
    index=0
    word_length=7
    return {
        'example_keyword': {
            'index': 0,
            'weight': 1.0,
            'value': raw_llm_output[0:7] # Example slicing, adjust as needed
        },
    }
    
token_index = TokenIndex()