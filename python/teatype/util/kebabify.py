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
    parsed_name = re.sub(r'(?<!^)(?=[A-Z])', seperator, raw_name).lower()
    if remove:
        parsed_name = parsed_name.replace(remove, '')
    # TODO: Implement support for multiple replace
    if replace:
        parsed_name = parsed_name.replace(replace[0], replace[1])
    if plural:
        parsed_name = parsed_name + 's' if not parsed_name.endswith('s') else parsed_name + 'es'
    return parsed_name