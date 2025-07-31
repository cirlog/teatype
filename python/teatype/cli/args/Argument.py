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
    
class Argument:
    """
    Represents a command-line argument.

    Attributes:
        name (str): The name of the argument.
        help (str): A brief description of the argument.
        help_extension (List[str], optional): Additional help information for the argument.
        required (bool): Indicates whether the argument is required.
        value (Any): The value of the argument, initially set to None.
    """
    def __init__(self,
                name:str,
                help:str|List[str],
                position:int,
                required:bool):
        self.name = name
        self.help = help
        self.position = position
        self.required = required
        
        self.value = None  # Initialize the value of the argument to None