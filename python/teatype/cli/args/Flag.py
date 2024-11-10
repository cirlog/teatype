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

# From system imports
from typing import List

# TODO: Implement as package class
class Flag:
    """
    Represents a command-line flag.

    Attributes:
        short (str): The short form of the flag (e.g., '-h').
        long (str): The long form of the flag (e.g., '--help').
        help (str): A brief description of the flag.
        help_extension (List[str], optional): Additional help information for the flag.
        value_name (str, optional): The name of the value associated with the flag.
        required (bool): Indicates whether the flag is required.
        value (Any): The value of the flag, initially set to None.
    """
    def __init__(self,
                short: str,
                long: str,
                help: str|List[str],
                required:bool,
                options:List[str]=None):
        self.short = f'-{short}'
        self.long = f'--{long}'
        self.help = help
        self.required = required
        
        self.options = options
        
        self.value = None # Initialize the value of the flag to None