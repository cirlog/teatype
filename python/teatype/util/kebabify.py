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

# System imports
import re

# From system imports
from typing import Union

def kebabify(raw_name:str,
             plural:bool=False,
             remove:str=None,
             replace:Union[str,str]=None,
             seperator:str='-') -> str:
    """
    Convert a CamelCase or PascalCase identifier into kebab-case.

    raw_name:    The original string in CamelCase or PascalCase.
    plural:      If True, append a plural suffix ('s' or 'es') to the result.
    remove:      A substring to strip out of the kebabified name after conversion.
    replace:     A two-element sequence (old, new) specifying a single replacement.
    seperator:   The character to insert before uppercase letters (defaults to '-').
    
    Returns the resulting kebab-case string, optionally modified by remove, replace, and plural rules.
    """
    # Insert separator before each uppercase letter (except at the start), then lowercase entire string
    parsed_name = re.sub(r'(?<!^)(?=[A-Z])', seperator, raw_name).lower()
    if remove:
        # Remove all occurrences of the specified substring
        parsed_name = parsed_name.replace(remove, '')
    # TODO: Implement support for multiple replacement operations
    if replace:
        # Perform a single replace operation: replace[0] → replace[1]
        parsed_name = parsed_name.replace(replace[0], replace[1])
    if plural:
        # Append 's' if it doesn't already end with 's', otherwise append 'es'
        parsed_name = parsed_name + 's' if not parsed_name.endswith('s') else parsed_name + 'es'
    return parsed_name # Return the final kebabified (and possibly modified) string

def unkebabify(kebab_name: str) -> str:
    """
    Convert a kebab-case string back into PascalCase.

    kebab_name: The input string in kebab-case (words separated by '-').
    
    Returns the string in PascalCase, capitalizing each segment and concatenating.
    """
    # Split the kebab-case input into parts on hyphens
    parts = kebab_name.split('-')
    # Capitalize each non-empty segment and join them without separators
    return ''.join(part.capitalize() for part in parts if part)