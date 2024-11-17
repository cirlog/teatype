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
import inspect
import os
import signal
import shutil
import sys

# From package imports
from teatype.cli import BaseCLI, Stop
from teatype.io import load_env, shell
from teatype.logging import err, warn

# From-as system imports
from importlib import util as iutil

# From-as package imports
from teatype.io import TemporaryDirectory as TempDir

class Start(BaseCLI):
    def __init__(self, auto_navigate=True):
        self.auto_navigate = auto_navigate
        
        super().__init__()
    
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
        
   # TODO: Decouple this class from CheckIfRunning into BaseCLI to prevent DRY
    def load_script(self):
        """
        Discover and import all Python scripts in the `scripts/` directory, skipping __init__.py and non-Python files.
        """
        scripts = {}

        # Determine the absolute path of the current script file based on the module name
        current_file = os.path.abspath(self.__class__.__module__.replace('.', '/') + '.py')
        # Get the parent directory of the current script
        current_directory = os.path.dirname(current_file)
        # Define the path to the scripts directory
        script_directory = os.path.join(current_directory, 'scripts')
        
        # Create a temporary directory within the scripts directory for renaming and importing modules
        with TempDir(directory_path=script_directory) as temp_dir:
            try:
                # Iterate over all files in the scripts directory
                for filename in os.listdir(script_directory):
                    # Skip the __init__.py file and any __pycache__ directories
                    if filename != '__init__.py' and filename != '__pycache__':
                        # Check if the current filename is a directory; if so, skip it
                        if os.path.isdir(os.path.join(script_directory, filename)):
                            continue
                        
                        # Convert filename from kebab-case to snake_case for consistent module naming
                        formatted_module_name = filename.replace('-', '_').replace('.py', '')
                        formatted_filename = formatted_module_name + '.py'

                        # Define full paths for the original and temporary files
                        original_filepath = os.path.join(script_directory, filename)
                        temp_filepath = os.path.join(temp_dir, formatted_filename)

                        try:
                            try:
                                # Copy the original file to the temporary directory with the new snake_case name
                                shutil.copy2(original_filepath, temp_filepath)
                            except Exception as e:
                                # Log an error if the file copy fails
                                err("An error occurred during file copy:", e)

                            # Create a module spec from the temporary file location
                            spec = iutil.spec_from_file_location(formatted_module_name, temp_filepath)
                            # Create a new module based on the spec
                            module = iutil.module_from_spec(spec)
                            # Execute the module to load its contents
                            spec.loader.exec_module(module)

                            # Convert the snake_case module name to CamelCase for class identification
                            camel_case_name = ''.join(word.capitalize() for word in formatted_module_name.split('_'))

                            # Retrieve the class from the module by name
                            script_class = getattr(module, camel_case_name, None)

                            # Ensure the retrieved class exists, is a class type, and is a subclass of Stop
                            if script_class and inspect.isclass(script_class) and camel_case_name == 'Stop':
                                # Having to use "camel_case_name == 'Stop'" even though issubclass(script_class, Stop) should work
                                # But after 30 minutes of debugging, I am tired of this stupid shit not working even though it should
                                # And it works perfectly fine in the stop script with the check-if-running relation
                                # I am convinced at this point that the line above is vodoo cursed and I have been working with
                                # cursed lines all along, so I just gave up and am ready to move on even though I don't want to
                                # https://www.youtube.com/watch?v=bH17fIsYirI&ab_channel=SimonDToppin
                                
                                # Instantiate the class without automatic validation or execution
                                stop = script_class(auto_validate=False,
                                                    auto_execute=False)
                                # Set the '--hide-output' flag to suppress verbose output
                                stop.set_flag('hide-output', True)
                                # TODO: Maybe implement some sort of proxy mode to prevent this or maybe a function variable
                                # Validate the arguments provided to the script
                                # stop.validate_args()
                                # Perform any necessary pre-execution setup
                                stop.pre_execute()
                                # Execute the script
                                stop.execute()

                        except Exception as e:
                            # Log an error if loading the script fails
                            err(f'Error loading script "{filename}": {e}')

            finally:
                # Ensure the temporary directory is removed from sys.path after import
                sys.path.pop(0)

        # Sort the scripts dictionary by keys for consistent ordering
        scripts = dict(sorted(scripts.items()))
        return scripts

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
            
        self.load_script()
        
        if self.auto_navigate:
            # Determine the directory of the current (inherited) script
            script_dir = os.path.abspath(self.__class__.__module__.replace('.', '/') + '.py')
            # Determine the parent directory of the current script
            parent_dir = os.path.dirname(script_dir)
            # Change the working directory to the parent directory
            os.chdir(parent_dir)
        
        # If the 'detached' flag is set, run the command in the background
        if self.get_flag('detached'):
            # Append shell redirection to merge stderr with stdout
            self.start_command += ' > /dev/null 2>&1 &'
        
        load_env() # Load the environment variables
        
        def signal_handler(signum, _):
            try:
                signal_name = signal.Signals(signum).name
            except ValueError:
                signal_name = f"Unknown signal ({signum})"
                
            if signum == signal.SIGINT:
                warning_addendum = ' (possibly user keyboard interrupt)'
                
            # Log a warning if the process is interrupted by the user (e.g., Ctrl+C)
            warn(f'Process killed by {signal_name} signal{warning_addendum}.', pad_bottom=1, pad_top=2)
            exit(1) # Double making sure that the process is killed (maybe a bad idea)?

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        signal.signal(signal.SIGUSR1, signal_handler)
        signal.signal(signal.SIGUSR2, signal_handler)
        # Hint: You cannot catch SIGKILL signal, it is a kernel-level signal and cannot be caught by the process
        # So do NOT even bother to try to catch it
        
        shell(self.start_command)