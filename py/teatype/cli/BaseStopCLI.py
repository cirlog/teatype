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
import inspect
import os
import shutil
import sys
from importlib import util as iutil

# Third-party imports
from teatype.cli import BaseCLI, BaseIsRunningCLI
from teatype.io import path, softkill
from teatype.logging import *
from teatype.io import TemporaryDirectory as TempDir

# TODO: Redis adapter to remove entries from a redis db?
class BaseStopCLI(BaseCLI):
    # TODO: Add flag that uses exit codes instead of returning boolean
    def meta(self):
        return {
            'name': 'stop',
            'shorthand': 'sp',
            'help': 'Stop a process',
            'flags': [
                {
                    'shorthand': 'f',
                    'name': 'force-signal',
                    'help': 'Force a specific signal',
                    'options': ['SIGINT', 'SIGTERM', 'SIGKILL'],
                    'required': False
                },
                {
                    'shorthand': 's',
                    'name': 'silent',
                    'help': 'Hide verbose output of script',
                    'required': False
                },
                {
                    'shorthand': 'sl',
                    'name': 'sleep',
                    'help': 'Sleep time between process checks',
                    'options': float,
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
        # Get the parent directory of the current script
        scripts_directory = path.caller_parent(skip_call_stacks=3)
        if hasattr(self, 'scripts_directory'):
            scripts_directory = self.scripts_directory
        # Create a temporary directory within the scripts directory for renaming and importing modules
        with TempDir(directory_path=scripts_directory) as temp_dir:
            try:
                # Iterate over all files in the scripts directory
                for filename in os.listdir(scripts_directory):
                    # Skip the __init__.py file and any __pycache__ directories
                    if filename != '__init__.py' and filename != '__pycache__':
                        # Check if the current filename is a directory; if so, skip it
                        if os.path.isdir(os.path.join(scripts_directory, filename)):
                            continue
                        
                        # Convert filename from kebab-case to snake_case for consistent module naming
                        formatted_module_name = filename.replace('-', '_').replace('.py', '')
                        formatted_filename = formatted_module_name + '.py'
                        if formatted_module_name != 'is_running':
                            continue

                        # Define full paths for the original and temporary files
                        original_filepath = os.path.join(scripts_directory, filename)
                        temp_filepath = os.path.join(temp_dir, formatted_filename)

                        try:
                            try:
                                # Copy the original file to the temporary directory with the new snake_case name
                                shutil.copy2(original_filepath, temp_filepath)
                            except Exception as exc:
                                # Log an error if the file copy fails
                                err(f'An error occurred during file copy: {exc}')

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

                            # Ensure the retrieved class exists, is a class type, and is a subclass of CheckIfRunning
                            if script_class and inspect.isclass(script_class) and issubclass(script_class, BaseIsRunningCLI):
                                # Instantiate the class without automatic validation or execution
                                self.is_running = script_class(auto_validate=False,
                                                               auto_execute=False)
                                # Set the '--silent' flag to suppress verbose output
                                self.is_running.set_flag('silent', True)
                                # Validate the arguments provided to the script
                                # self.is_running.validate()
                                # Perform any necessary pre-execution setup
                                self.is_running.pre_execute()
                                # Execute the script and retrieve the list of process PIDs
                                self.process_pids = self.is_running.execute()
                                self.process_names = self.is_running.process_names
                        except Exception as exc:
                            if formatted_module_name == 'is_running':
                                # Log an error if loading the script fails
                                err(f'Error loading script "{filename}": {exc}')
            finally:
                try:
                    # Ensure the temporary directory is removed from sys.path after import
                    sys.path.pop(0)
                except:
                    pass

        # Sort the scripts dictionary by keys for consistent ordering
        scripts = dict(sorted(scripts.items()))
        return scripts

    def execute(self):
        """
        Execute the stop command by loading scripts, checking for processes, and initiating the kill sequence.
        """
        # Load and import all relevant scripts
        self.load_script()
        
        silent = self.get_flag('silent', False)
        if len(self.process_pids) == 0:
            if not silent:
                println()
                # Inform the user if there are no processes to stop
                log('No processes to stop.')
                println()
            return True
        else:
            if not silent:
                println()
            force_signal = self.get_flag('force-signal')
            if not silent:
                if force_signal:
                    hint(f'Forcing signal: {force_signal}')
            sleep = self.get_flag('sleep', 1)
            if not silent:
                hint(f'Only sleeping {sleep}s seconds between attempts')
                if force_signal or sleep:
                    println()
                println()
            # Begin the recursive kill process
            return softkill(self.process_names,
                            force_signal=force_signal,
                            delay=sleep,
                            silent=silent)

if __name__ == '__main__':
    BaseStopCLI()