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

# Standard-library imports
import shlex
import subprocess
import sys
import termios
import tty

# Third-party imports
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