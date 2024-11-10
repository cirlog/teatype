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
import os

# From package imports
from teatype.cli import BaseCLI
from teatype.io import load_env, shell
from teatype.logging import err, warn

class Start(BaseCLI):
    def meta(self):
        return {
            'name': 'start',
            'shorthand': 's',
            'help': 'Start a process',
            'flags': [
                {
                    'short': 'd',
                    'long': 'detached',
                    'help': 'Start process in detached mode',
                    'required': False
                },
                {
                    'short': 'i',
                    'long': 'ignore-running',
                    'help': 'Ignore if process is already running',
                    'required': False
                },
                {
                    'short': 't',
                    'long': 'tail-logs',
                    'help': 'Tail logs of process',
                    'required': False
                }
            ]
        }

    def execute(self):
        """
        Executes the start command to initiate the process.

        This method performs the following steps:
        1. Checks if 'start_command' is defined.
        2. Changes the current working directory to its parent directory.
        3. Appends shell redirections to the start command.
        4. Executes the start command, optionally in detached mode.
        5. Handles keyboard interrupts gracefully.
        """
        # Verify that the 'start_command' attribute exists; if not, log an error and exit
        if not hasattr(self, 'start_command'):
            err('No "self.start_command" provided in source code. Please provide a command to start a process in the pre_execute function.',
                exit=True)
        
        # Retrieve the current working directory
        current_dir = os.getcwd()
        # Determine the parent directory of the current working directory
        parent_dir = os.path.dirname(current_dir)
        # Change the working directory to the parent directory
        os.chdir(parent_dir)
        
        # Append shell redirection to merge stderr with stdout
        self.start_command += ' 2>&1'
        
        # If the 'detached' flag is set, run the command in the background
        if self.get_flag('detached'):
            self.start_command += ' &'
        
        load_env() # Load the environment variables
        
        try:
            # Execute the start command using the shell
            shell(self.start_command)
        except KeyboardInterrupt:
            # Log a warning if the process is interrupted by the user (e.g., Ctrl+C)
            warn('Process killed by SIGINT signal (probably user keyboard interrupt).', pad_bottom=1, pad_top=2)