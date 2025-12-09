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

# System import
import sys
from typing import List, Optional

# Third-party imports
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import WordCompleter
from teatype.enum import EscapeColor
from teatype.logging import *

# TODO: Implement "freesolo" that allows to type in whatever you want or force to select from options only
def prompt(prompt_text:str,
           options:List[str]=None,
           *,
           colorize:bool=True,
           default:Optional[str]=None,
           exit_on_error:bool=False,
           print_padding:bool=True,
           return_bool:bool=True) -> any:
    """
    Displays a prompt to the user with the given text and a list of available options.
    Supports arrow-key navigation for option selection via prompt_toolkit.

    Args:
        prompt_text (str): The message to display to the user.
        options (List[str]): A list of valid options that the user can choose from.
        return_bool (bool): Whether to return a boolean value based on the user's selection.
        colorize (bool): Whether to colorize the prompt text. Default is True.
        exit_on_error (bool): Whether to exit on invalid input.

    Returns:
        any: The user's selected option.
    """
    while True:
        try:
            if options is None and return_bool:
                options = ['Y', 'n']
                
            if return_bool:
                if options:
                    if len(options) > 2:
                        err('Cannot return a boolean value for more than two options.', exit=True)

            # Apply color to the prompt
            display_text = f'{EscapeColor.LIGHT_GREEN}{prompt_text}{EscapeColor.RESET}' if colorize else prompt_text
            
            if default is not None:
                default_text = f' [Default: {default}]'
                if colorize:
                    default_text = f'{EscapeColor.RESET}{default_text}'
                display_text += default_text

            # Build options string for display
            if options:
                options_string = '(' + '/'.join(options) + '): '
                if colorize:
                    options_string = f'{EscapeColor.GRAY}{options_string}{EscapeColor.RESET}'
                display_text += ' ' + options_string

            # Log the prompt
            log(display_text, pad_before=1 if print_padding else 0)

            # Use prompt_toolkit with arrow-key selection
            if options:
                completer = WordCompleter(options, ignore_case=True)
                prompt_answer = pt_prompt('> ', completer=completer)
            else:
                prompt_answer = pt_prompt('> ')

            # Validate input if options are provided
            if options:
                if prompt_answer not in options:
                    error_message = 'Invalid input. Available options are: ' + ', '.join(options)
                    err(error_message,
                        pad_after=1 if print_padding else 0,
                        exit=exit_on_error,
                        raise_exception=not exit_on_error,
                        use_prefix=False,
                        verbose=False)
            
            if prompt_answer == '' and default is not None:
                prompt_answer = default
                log(f'Using default value: {default}', pad_after=1 if print_padding else 0)
                    
            # Return boolean if requested
            return prompt_answer == options[0] if return_bool and options else prompt_answer
        except KeyboardInterrupt:
            warn('User interrupted the input prompt.', pad_before=2, pad_after=1, use_prefix=False)
            # TODO: Raise exception instead?
            sys.exit(1)
        except SystemExit as se:
            sys.exit(se.code)
        except Exception:
            err(f'An error occurred while prompting the user for input', pad_after=1, exit=True, traceback=True)
