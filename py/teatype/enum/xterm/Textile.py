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

# Standard-library imports
from enum import Enum

# HINT: Wordplay at text-style ;)
class Textile(Enum):
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    RESET = '\033[0m'
    STRIKETHROUGH = '\033[9m'
    UNDERLINE = '\033[4m'
        
    def __str__(self):
        """
        Returns the ANSI escape code associated with the enumeration member.

        This method overrides the default string representation of the Enum member,
        enabling it to be used directly in string formatting for colored terminal output.
        This way enums mimick how they are implemented in other languages like C++.
        
        Unfortunately (for good reasons), Python does not support operator overloading and inheritance of enums,
        so this function has to be implemented in every enum class that requires it.
        """
        return self.value