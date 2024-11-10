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
import subprocess

def shell(command:str,
          sudo:bool=False,
          cwd:bool=False,
          env:dict=None,
          timeout:float=None) -> int:
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
    
    # If sudo is True, prepend 'sudo' to the command
    if sudo:
        # Asking for sudo permissions before script executes any further and surpresses usage information
        subprocess.run('sudo 2>/dev/null', shell=True)
        command = f'sudo {command}'
        
    # Run the command in a subprocess
    # shell=True allows the command to be executed through the shell
    # cwd is set to None by default, but can be specified if cwd is True
    # env is set to None by default, but can be specified with env
    # timeout is set to None by default, but can be specified with timeout
    # Not using a command list array, since I am using shell=True
    completed_process = subprocess.run(command, 
                                        shell=True, 
                                        cwd=None if not cwd else cwd, 
                                        env=None if not env else env, 
                                        timeout=timeout)
    
    # Return the exit code of the completed process
    return completed_process.returncode