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

def prompt(text:str,
           choices:List[str]=None,
           *,
           colorize:bool=True,
           default:Optional[str]=None,
           exit_on_error:bool=False,
           freesolo:bool=False,
           print_padding:bool=True,
           return_input:bool=False,
           use_index:bool=False) -> any:
    """
    Displays a prompt to the user with the given text and a list of available choices.
    Supports arrow-key navigation for option selection via prompt_toolkit.

    Args:
        text (str): The message to display to the user.
        choices (List[str]): A list of valid choices that the user can choose from.
        colorize (bool): Whether to colorize the prompt text. Default is True.
        default (Optional[str]): Default value to use if user presses Enter without input.
        exit_on_error (bool): Whether to exit on invalid input.
        freesolo (bool): If True, allows the user to type any value even if it's not in the choices list.
                         choices will still be shown as suggestions with autocomplete. Default is False.
        print_padding (bool): Whether to add padding around the prompt. Default is True.
        return_input (bool): Whether to return a boolean value based on the user's selection.
        use_index (bool): If True, displays choices as a numbered list and allows the user to type
                          the number (1-indexed) of the choice. Returns the 0-indexed value.
                          Default is False.

    Returns:
        any: The user's selected option, the 0-indexed selection if use_index is enabled,
             or any string if freesolo is enabled.
    """
    while True:
        try:
            if choices is None and not return_input:
                choices = ['Y', 'n']
                
            if not return_input:
                if choices:
                    if len(choices) > 2:
                        err('Cannot return a boolean value for more than two choices.', exit=True)

            # Apply color to the prompt
            display_text = f'{EscapeColor.LIGHT_GREEN}{text}{EscapeColor.RESET}' if colorize else text
            
            if default is not None:
                default_text = f' [Default: {default}]'
                if colorize:
                    default_text = f'{EscapeColor.RESET}{default_text}'
                display_text += default_text

            # Build choices string for display (only when not using use_index)
            if choices and not use_index:
                choices_string = '(' + '/'.join(choices) + '): '
                if colorize:
                    choices_string = f'{EscapeColor.GRAY}{choices_string}{EscapeColor.RESET}'
                display_text += ' ' + choices_string

            # Log the prompt
            log(display_text, pad_before=1 if print_padding else 0)
            # Display numbered list when use_index is enabled
            if choices and use_index:
                for i, choice in enumerate(choices):
                    whisper(f'  [{i + 1}] {choice}')

            # Use prompt_toolkit with arrow-key selection
            if choices:
                # Include numeric choices in completer if use_index is enabled
                completer_choices = list(choices)
                if use_index:
                    completer_choices.extend(str(i+1) for i in range(len(choices)))
                completer = WordCompleter(completer_choices, ignore_case=True)
                prompt_answer = pt_prompt('> ', completer=completer)
            else:
                prompt_answer = pt_prompt('> ')

            # Handle numeric input if use_index is enabled
            if choices and use_index and prompt_answer.isdigit():
                numeric_index = int(prompt_answer) - 1  # Convert to 0-indexed
                if 0 <= numeric_index < len(choices):
                    # Return the 0-indexed value
                    return numeric_index
                elif not freesolo:
                    error_message = f'Invalid number. Please enter a number between 1 and {len(choices)}.'
                    err(error_message,
                        pad_after=1 if print_padding and exit_on_error else 0,
                        exit=exit_on_error,
                        raise_exception=False,
                        use_prefix=False,
                        verbose=False)
                    continue
            
            # If use_index is enabled but user typed the choice name, find its index
            if choices and use_index and prompt_answer in choices:
                return choices.index(prompt_answer)

            # Validate input if choices are provided and freesolo is disabled
            if choices and not freesolo:
                if prompt_answer not in choices:
                    error_message = 'Invalid input. Available choices are: ' + ', '.join(choices)
                    if use_index:
                        error_message += f' (or enter 1-{len(choices)})'
                    err(error_message,
                        pad_after=1 if print_padding and exit_on_error else 0,
                        exit=exit_on_error,
                        raise_exception=False,
                        use_prefix=False,
                        verbose=False)
                    continue
            
            if prompt_answer == '' and default is not None:
                prompt_answer = default
                log(f'Using default value: {default}', pad_after=1 if print_padding else 0)
                # If use_index and default is a valid choice, return its index
                if use_index and prompt_answer in choices:
                    return choices.index(prompt_answer)
                    
            # Return boolean if requested
            return prompt_answer == choices[0] if not return_input and choices else prompt_answer
        except KeyboardInterrupt:
            warn('User interrupted the input prompt.', pad_before=2, pad_after=1, use_prefix=False)
            # TODO: Raise exception instead?
            sys.exit(1)
        except SystemExit as se:
            sys.exit(se.code)
        except Exception:
            err(f'An error occurred while prompting the user for input', pad_after=1, exit=True, traceback=True)
