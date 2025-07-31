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

# System import
import sys

# From system imports
from typing import List

# From package imports
from teatype.enum import EscapeColor
from teatype.logging import err, log, warn

def prompt(prompt_text:str, options:List[any]=None, return_bool:bool=True, colorize:bool=True) -> any:
    """
    Displays a prompt to the user with the given text and a list of available options.

    Args:
        prompt_text (str): The message to display to the user.
        options (List[any]): A list of valid options that the user can choose from.
        return_bool (bool): Whether to return a boolean value based on the user's selection. Default is True.
        colorize (bool): Whether to colorize the prompt text. Default is True.

    Returns:
        any: The user's selected option.
    """
    try:
        if return_bool:
            if options:
                # Determine if the return type should be a boolean based on the user's preference
                if len(options) > 2:
                    # Raise an error if more than two options are provided, as a boolean return is only valid for binary choices
                    err('Cannot return a boolean value for more than two options.', exit=True)
            else:
                err('Cannot return a boolean value without options. If you don\'t want to use options, set "return_bool=False"', exit=True)
        
        # Log the prompt text for debugging or record-keeping purposes
        if colorize:
            prompt_text = f'{EscapeColor.LIGHT_GREEN}{prompt_text}{EscapeColor.RESET}'
        log(prompt_text, pad_before=1)
        
        if options:
            # Initialize the string that will display the options
            options_string = '('
            
            # Iterate over each option to build the options string
            for i, option in enumerate(options):
                options_string += f'{option}'
                # If it's the last option, append a '/' to indicate the end
                if i < len(options) - 1:
                    options_string += '/'
            
            # Close the options string with a colon and space for user input
            options_string += '): '
            
            # Prompt the user for input using the constructed options string
            if colorize:
                options_string = f'{EscapeColor.GRAY}{options_string}{EscapeColor.RESET}'
            prompt_answer = input(options_string)
            
            # Validate the user's input against the available options
            if prompt_answer not in options:
                # Log an error message and exit if the input is invalid
                err('Invalid input. Available options are: ' + ', '.join(options),
                    pad_after=1,
                    exit=True,
                    use_prefix=False,
                    verbose=False)
        else:
            prompt_answer = input()
        
        # Return the validated user input
        return prompt_answer == options[0] if return_bool else prompt_answer
    except KeyboardInterrupt:
        warn('User interrupted the input prompt.', pad_before=2, pad_after=1, use_prefix=False, verbose=False)
        sys.exit(1)
    except SystemExit as se:
        sys.exit(se.code)
    except:
        err(f'An error occurred while prompting the user for input', pad_after=1, exit=True, traceback=True)