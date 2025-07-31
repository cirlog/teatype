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
from enum import Enum

class EscapeColor(Enum):
    BLACK = '\033[30m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    GRAY = '\033[90m'
    GREEN = '\033[32m'
    MAGENTA = '\033[35m'
    RED = '\033[31m'
    RESET = '\033[0m'
    WHITE = '\033[37m'
    YELLOW = '\033[33m'
    LIGHT_BLACK = '\033[90m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_MAGENTA = '\033[95m'
    LIGHT_RED = '\033[91m'
    LIGHT_WHITE = '\033[97m'
    LIGHT_YELLOW = '\033[93m'
    
    def __str__(self):
        """
        Returns the ANSI escape code associated with the enumeration member.

        This method overrides the default string representation of the Enum member,
        enabling it to be used directly in string formatting for colored terminal output.
        This way enums mimick how they are implemented in other languages like C++.
        
        Unfortunately (for good reasons), Python does not support operator overloading and inheritance of enums,
        so this function has to be implemented in every enum class that requires it.
        """
        return self.value # Retrieve and return the ANSI escape code string for the specific value