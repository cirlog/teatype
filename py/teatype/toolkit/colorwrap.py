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

# Third-party imports
from teatype.enum import EscapeColor

def colorwrap(string:str, color:EscapeColor.Colors) -> str:
    """
    Wraps a string with the specified color escape code.

    Args:
        string (str): The string to be wrapped.
        color (Colors=Literal['black', 'blue', 'cyan', 'gray', 'green', 'magenta', 'red', 'white', 'yellow', 'light_black', 'light_blue', 'light_cyan', 'light_green', 'light_magenta', 'light_red', 'light_white', 'light_yellow']): The color to wrap the string with. 

    Returns:
        str: The wrapped string with ANSI escape codes for coloring.
    """
    if color.upper() not in [c.name for c in EscapeColor.COLORS()]:
        raise ValueError(f'Invalid color: {color}. Must be one of {list(EscapeColor)}.')
    escape_color = EscapeColor[color.upper()]
    return f'{escape_color}{string}{EscapeColor.RESET}' # Wrap the string with the specified color and reset code