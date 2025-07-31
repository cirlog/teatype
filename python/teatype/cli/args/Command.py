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

class Command:
    """
    Represents a command-line command.

    Attributes:
        name (str): The name of the command.
        shorthand (str): The shorthand of the command.
        help (str): A brief description of the command.
        required (bool): Whether the command is required or not.
    """
    def __init__(self,
                name:str,
                shorthand:str,
                help:str|List[str],
                required:bool=True):
        self.name = name
        self.shorthand = shorthand
        self.help = help
        self.required = required
        
        self.value = None