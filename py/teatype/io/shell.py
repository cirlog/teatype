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
import shlex
import subprocess
import sys
import termios
import tty
from typing import List, Optional

# Third-party imports
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import WordCompleter
from teatype.enum import EscapeColor
from teatype.logging import *
from teatype.io import env as current_env

def clear(use_ansi:bool=False) -> None:
    """
    Clears the terminal screen using ANSI escape sequences.

    This function prints ANSI escape codes to reset the terminal cursor position and clear the screen.
    It serves as an alternative to using the 'clear' shell command via subprocess, which can be choppy and slow.
    """
    if use_ansi:
        # Using ANSI escape sequences to clear the terminal instead of clear, since clear is too choppy and slow
        # '\033[H' moves the cursor to the home position (top-left corner) of the terminal.
        # '\033[J' clears the screen from the cursor down.
        print('\033[H\033[J')
    else:
        subprocess.run('clear', shell=True)

def enable_sudo(max_fail_count:int=3, print_padding:bool=True) -> None:
    try:
        """
        Prompts for sudo password up to max_fail_count times, masking input with asterisks.
        If sudo timestamp is already valid, skips prompting.
        """
        # If sudo timestamp is still valid, no password is necessary
        no_pass = subprocess.run(
            'sudo -n true', shell=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode == 0

        if no_pass:
            if print_padding:
                println()
            hint('No sudo password required; privileges already granted.', use_prefix=False)
            return
        
        if print_padding:
            println()

        def _getpass_masked(prompt: str) -> str:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            passwd = ''
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch == '\x03': # Ctrl+C
                        sys.stdout.write('\n')
                        raise KeyboardInterrupt
                    if ch in ('\r', '\n'):
                        sys.stdout.write('\n')
                        break
                    if ch == '\x7f': # Backspace
                        if passwd:
                            passwd = passwd[:-1]
                            sys.stdout.write('\b \b')
                    else:
                        passwd += ch
                        sys.stdout.write('*')
                    sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return passwd

        for attempt in range(1, max_fail_count + 1):
            log(f'{EscapeColor.LIGHT_GREEN}Elevated privileges required. Please enter your password:')
            password = _getpass_masked('Password: ')
            # Validate password without leftover output
            cmd = f'echo {shlex.quote(password)} | sudo -S -v >/dev/null 2>&1'
            ret = subprocess.run(cmd, shell=True).returncode
            if ret == 0:
                println()
                log(f'{EscapeColor.LIGHT_GREEN}Privileges elevated successfully.')
                return
            else:
                remaining = max_fail_count - attempt
                err(
                    'Invalid password. '
                    f'{remaining} attempt{"s" if remaining != 1 else ""} remaining.',
                    pad_before=1, pad_after=1, verbose=False, use_prefix=False
                )

        err('Maximum password attempts exceeded. Aborting.', pad_before=1, pad_after=1, exit=True, verbose=False, use_prefix=False)
    except KeyboardInterrupt:
        err('Sudo elevation cancelled by user.', pad_before=1, pad_after=1, exit=True, verbose=False, use_prefix=False)
    except Exception as exc:
        err(f'Error enabling sudo: {exc}. Trying to grant privileges automatically.', pad_before=1, pad_after=1)
        try:
            cmd = f'sudo -S -v >/dev/null 2>&1'
            ret = subprocess.run(cmd, shell=True).returncode
            if ret == 0:
                log(f'{EscapeColor.LIGHT_GREEN}Privileges elevated successfully.')
                return
            else:
                log(f'Automatic sudo elevation failed.', pad_before=1, pad_after=1)
        except Exception as exc:
            err(f'Error enabling sudo: {exc}', pad_before=1, pad_after=1)
    finally:
        if print_padding:
            println()

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

def shell(command:str,
          cwd:str=False,
          combine_stdout_and_stderr:bool=False,
          detached:bool=False,
          env:dict=None,
          format_stdout:bool=True,
          mute:bool=False,
          return_output:bool=False,
          return_stdout:bool=False,
          sudo:bool=False,
          timeout:float=None,) -> any:
    """
    Executes a shell command using the subprocess module.

    This method runs a shell command in a subprocess and returns the exit code of the command.
    It provides options to run the command with sudo, set the current working directory,
    pass environment variables, and specify a timeout for the command execution.

    Args:
        command (str): The shell command to be executed.
        sudo (bool): Whether to run the command with sudo privileges. Default is False.
        cwd (bool): Whether to set the current working directory for the command. Default is False.
        env (dict): A dictionary of environment variables to be passed to the command. Default is None.
        timeout (float): The timeout in seconds for the command execution. Default is None.

    Returns:
        int: The exit code of the completed process.
    """
    
    # List of lambda functions to handle specific error scenarios
    edge_cases = [
        lambda stderr, command, output: (
            err(
                f'Shell command "{command}" seems to have thrown an error. '
                'If you believe this to be a mistake, set "ignore_warnings=True", '
                'otherwise set "mute=False" to debug.',
                pad_before=1,
                pad_after=1 
            ),
            setattr(output, 'returncode', 1) # Modify the output object's returncode attribute to 1 to indicate an error
        ) if 'exit code: 1' in stderr else None, # Apply this lambda only if the specific error is detected
    ]
    
    if combine_stdout_and_stderr:
        # If combine_stdout_and_stderr is True, redirect stderr to stdout
        command += ' 2>&1'
    
    if detached:
        # If detached is True, run the command in a new process group
        # This allows the command to run independently of the parent process
        command += ' &'
        
    # if detached and 'sudo' in command:
    #     command = command.replace('sudo ', 'sudo -S ')  # Use -n to avoid prompting for password in detached mode
    
    # If sudo is True, prepend 'sudo' to the command
    if sudo:
        # Asking for sudo permissions before script executes any further and suppresses usage information
        subprocess.run('sudo 2>/dev/null', shell=True)
        command = f'sudo {command}'
    try:
        # Run the command in a subprocess
        # shell=True allows the command to be executed through the shell
        # cwd is set to None by default, but can be specified if cwd is True
        # env is set to None by default, but can be specified with env
        # timeout is set to None by default, but can be specified with timeout
        # Not using a command list array, since I am using shell=True
        output = subprocess.run(command, # Split the command into a list of arguments
                                shell=True, # Execute the command through the shell
                                cwd=None if not cwd else cwd,
                                env=env if not env else current_env.get(),
                                # preexec_fn=os.setsid if detached else None,
                                text=return_stdout,
                                timeout=timeout,
                                stdout=subprocess.PIPE if mute or return_stdout else None,
                                stderr=subprocess.PIPE if mute else None)

        # Check if errors should not be ignored before processing
        stderr = str(output.stderr) # Convert the subprocess's standard error output from bytes to a string for analysis
        for edge_case in edge_cases:
            # Iterate over each edge case handler function in the list
            # and execute it with the current stderr, command, and output
            edge_case(stderr, command, output)
    except KeyboardInterrupt:
        class _KeyboardInterruptOutput:
            returncode:int=0
            stdout:str='KeyboardInterrupt'
        return _KeyboardInterruptOutput()
    except Exception as exc:
        # If an exception is raised, return the exit code 1 as a failsafe
        # Sometimes the command may fail due to a non-zero exit code, but still return
        # an exit code of 0. In such cases, the exception will be caught and the exit code will be set to 1.
        if return_stdout:
            str(exc)
        else:
            output.returncode = 1
    
    if return_output:
        # If return_output is True, return the original response object
        # This allows the caller to access the original response object and its attributes
        return output
    else:
        if return_stdout:
            # Retrieve the standard output from the subprocess
            stdout = output.stdout
            if not format_stdout:
                return stdout 
            # Count the number of newline characters in the stdout
            newline_count = stdout.count('\n')
            if newline_count > 1:
                # If multiple lines are present, split the stdout into a list of lines
                stdout = stdout.split('\n')[:-1] # Remove the last empty line
            else:
                # If only one line, remove the newline character from stdout
                stdout = stdout.replace('\n', '')
            # Return the processed stdout to the caller
            return stdout
        
        # Return the exit code of the completed process
        return output.returncode

# TODO: Disabled for now, since it will break the shell
# refresh = shell('exec bash')