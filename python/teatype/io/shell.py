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

# System imports
import getpass
import subprocess
import sys

# From package imports
from teatype.enum import EscapeColor
from teatype.logging import err, log, println

# From-as package imports
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

def enable_sudo(max_fail_count:int=3) -> None:
    """
    Executes a sudo command with suppressed error output.

    This function runs the 'sudo' command to elevate privileges without displaying
    any error messages. It is intended to be used as a preliminary step before executing
    other shell commands that require root access.

    Returns:
        None
    """
    # if shell('sudo -n true'):
    #     log('User already has elevated privileges, not further prompting required.')
    #     return
    
    # def getpass_asterisk(prompt='Password: '):
    #     fd = sys.stdin.fileno()
    #     old = termios.tcgetattr(fd)
    #     try:
    #         tty.setraw(fd)
    #         print(prompt, end='', flush=True)
    #         password = []
    #         while True:
    #             ch = sys.stdin.read(1)
    #             if ch in ['\r', '\n']:
    #                 print()
    #                 break
    #             elif ch == '\x7f':
    #                 if password:
    #                     password.pop()
    #                     sys.stdout.write('\b \b')
    #                     sys.stdout.flush()
    #             else:
    #                 password.append(ch)
    #                 sys.stdout.write('*')
    #                 sys.stdout.flush()
    #         return ''.join(password)
    #     finally:
    #         termios.tcsetattr(fd, termios.TCSADRAIN, old)

    # for attempt in range(max_fail_count):
    #     remaining = max_fail_count - attempt
    #     log(f'{EscapeColor.LIGHT_GREEN}Elevated privileges required {EscapeColor.GRAY}({remaining} tries left){EscapeColor.RESET}')
    #     password = getpass_asterisk('Password: ')
    #     output = subprocess.run(f'echo {password} | sudo -S -v >/dev/null 2>&1', shell=True)
        
    #     if output.returncode == 0:
    #         log('Privileges elevated successfully.')
    #         return
    #     elif attempt < max_fail_count - 1:
    #         log(f'{EscapeColor.RED}Invalid password. Try again.')
    #     else:
    #         log(f'{EscapeColor.RED}Invalid password. Abort.', pad_before=1, pad_after=1)
    #         sys.exit(1)
    
    log(f'{EscapeColor.LIGHT_GREEN}Elevated privileges required. Please enter your password:')
    password = getpass.getpass('Password: ')
    # Invoke the 'sudo' command to elevate privileges
    # The '2>/dev/null' redirects standard error to null, suppressing any error messages
    # 'shell=True' allows the command to be executed through the shell
    # output = subprocess.run(f'echo {password} | sudo -S ls 2>&1 > /dev/null', shell=True)
    output = subprocess.run(f'echo {password} | sudo -S -v >/dev/null 2>&1', shell=True)
    if output.returncode != 0:
        log(f'{EscapeColor.RED}Invalid password. Abort.', pad_before=1, pad_after=1)
        sys.exit(1)
    else:
        log('Privileges elevated successfully.')

def shell(command:str,
          sudo:bool=False,
          cwd:bool=False,
          env:dict=None,
          timeout:float=None,
          mute:bool=False,
          return_stdout:bool=False) -> any:
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
            setattr(output, "returncode", 1) # Modify the output object's returncode attribute to 1 to indicate an error
        ) if 'exit code: 1' in stderr else None, # Apply this lambda only if the specific error is detected
    ]
    
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
        output = subprocess.run(command, 
                                shell=True, # Execute the command through the shell
                                cwd=None if not cwd else cwd,
                                env=env if not env else current_env.get(),
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
    except Exception:
        # If an exception is raised, return the exit code 1 as a failsafe
        # Sometimes the command may fail due to a non-zero exit code, but still return
        # an exit code of 0. In such cases, the exception will be caught and the exit code will be set to 1.
        output.returncode = 1
        
    if return_stdout:
        # Retrieve the standard output from the subprocess
        stdout = output.stdout
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