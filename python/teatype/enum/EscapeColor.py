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

# Standard library imports
from enum import Enum
from typing import Literal

class EscapeColor(Enum):
    Colors = Literal['black',
                     'blue',
                     'cyan',
                     'gray',
                     'green',
                     'magenta',
                     'red',
                     'white',
                     'yellow',
                     'light_black',
                     'light_blue',
                     'light_cyan',
                     'light_green',
                     'light_magenta',
                     'light_red',
                     'light_white',
                     'light_yellow']
    
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
    
    ##############
    # Properties #
    ##############
    
    @staticmethod
    def COLORS(exclude_black:bool=False, exclude_gray:bool=False) -> list[str]:
        """
        Returns a list of all color codes from the EscapeColor enum.

        This method is useful for iterating over all colors in terminal output.
        """
        colors = [color for color in EscapeColor if not color.name.startswith('LIGHT_') and color.name != 'RESET']
        if exclude_black:
            colors = [color for color in colors if color.name != 'BLACK']
        if exclude_gray:
            colors = [color for color in colors if color.name != 'GRAY']
        colors.sort(key=lambda c: c.name)  # Sort colors by name for consistent ordering
        return colors
    
    @staticmethod
    def LIGHT_COLORS(exclude_black:bool=False) -> list[str]:
        """
        Returns a list of light color codes from the EscapeColor enum.

        This method is useful for iterating over light colors in terminal output.
        """
        light_colors = [color for color in EscapeColor if 'LIGHT_' in color.name and color.name != 'RESET']
        if exclude_black:
            light_colors = [color for color in light_colors if color.name != 'LIGHT_BLACK']
        light_colors.sort(key=lambda c: c.name)  # Sort light colors by name for consistent ordering
        return light_colors
    
    def N(exclude_black:bool=False, exclude_gray:bool=False) -> int:
        """
        Returns the number of colors defined in the EscapeColor enum.

        This property can be used to determine how many colors are available for use.
        """
        return len(EscapeColor.COLORS(exclude_black, exclude_gray))
    
    @staticmethod
    def N_LIGHT(exclude_black:bool=False) -> int:
        """
        Returns the number of light colors defined in the EscapeColor enum.

        This property can be used to determine how many light colors are available for use.
        """
        return len(EscapeColor.LIGHT_COLORS(exclude_black))
    
    @staticmethod
    def lighten(color:'EscapeColor.Colors') -> str:
        """
        Returns the light version of a given color.

        Args:
            color (Colors): The color to lighten.

        Returns:
            str: The light version of the specified color.
        """
        if color.name.upper() not in [c.name for c in EscapeColor.COLORS()]:
            raise ValueError(f'Invalid color: {color}. Must be one of {list(EscapeColor.COLORS())}.')
        light_color_name = f'LIGHT_{color.name.upper()}'
        if light_color_name not in EscapeColor.__members__:
            raise ValueError(f'No light version available for color: {color}.')
        return EscapeColor[light_color_name].value