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
# TODO: Ommit commands in favor of flags with values (e.g. --name "John Doe" or maybe even "=" assignement e.g. --name="John Doe")
class Command:
    """
    Represents a command-line command.

    Attributes:
        name (str): The name of the command.
        help (str): A brief description of the command.
        help_extension (List[str], optional): Additional help information for the command.
        value (Any): The value of the command, initially set to None.
    """
    def __init__(self,
                name:str,
                shorthand:str,
                help:str|List[str]):
        self.name = name
        self.shorthand = shorthand
        self.help = help
        
        self.value = None