#!/usr/bin/env python3.11

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
import shutil
import sys

# From package imports
from teatype.cli import BaseCLI, Command
from teatype.enum import EscapeColor
from teatype.io import clear_shell, file, path
from teatype.logging import err, log, hint, println

# From-as system imports
from importlib import util as iutil

# From-as package imports
from teatype.io import TemporaryDirectory as TempDir

# TODO: Time the execution of the CLI with stopwatch
# TODO: Increase performance of CLI execution by using a single instance of the CLI loaded in memory
class MainCLI(BaseCLI):
    parent_path:str
    scripts:dict
    tuis:dict
    
    def __init__(self, auto_parse:bool=False, auto_validate:bool=False, parent_path:str=None) -> None:
        """
        Initializes the MainCLI instance, setting up the CLI environment.
        
        Args:
            parent_path (str, optional): The parent directory path where the CLI scripts and TUIs are located. 
                                         If None, it defaults to two levels up from the current file's location.
            auto_parse (bool, optional): If True, automatically parses command-line arguments upon initialization.
            auto_validate (bool, optional): If True, automatically validates parsed arguments upon initialization.
        """
        if parent_path == None:
            self.parent_path = path.caller_parent(reverse_depth=2)
        else:
            self.parent_path = parent_path
            
        super().__init__(auto_parse=auto_parse, auto_validate=auto_validate)
        
        self.scripts = {}
        self.tuis = {}
        
    def discover_python_modules(self, folder_name:str) -> dict:
        """
        Dynamically discovers and loads python files from the specified directory and tries to load them into memory.
        Returns a sorted dictionary of module instances keyed by their names.
        
        The function creates a temporary directory to safely load modules without
        polluting the system path, and handles potential loading errors gracefully.
        """
        module_registry = {} # Dictionary to store discovered script instances
        current_directory = self.parent_path # Get the directory containing this file
        module_directory = path.join(current_directory, folder_name) # Path to scripts directory

        # Create temporary directory for safe module loading
        with TempDir(directory_path=current_directory) as temporary_directory:
            try:
                # Iterate through files in the scripts directory
                for f in file.list(module_directory):
                    # Skip special Python files
                    if f not in ['__init__.py', '__pycache__']:
                        # Convert filename to valid Python module name
                        module_name = f.name.replace('-', '_').replace('.py', '')
                        temp_file = path.join(temporary_directory, module_name + '.py')
                        original_file = path.join(module_directory, f.path)

                        try:
                            # Copy script to temp directory and load as module
                            shutil.copy2(original_file, temp_file)
                            spec = iutil.spec_from_file_location(module_name, temp_file)
                            module = iutil.module_from_spec(spec)
                            spec.loader.exec_module(module)

                            # Convert module_name to CamelCase for class name
                            class_name = ''.join(part.capitalize() for part in module_name.split('_'))
                            script_class = getattr(module, class_name, None)
                            # Verify class is valid CLI script
                            if script_class and inspect.isclass(script_class) and issubclass(script_class, BaseCLI):
                                # Initialize script instance without auto-execution
                                script_instance = script_class(proxy_mode=True,
                                                               auto_parse=False,
                                                               auto_validate=False,
                                                               auto_execute=False)
                                module_registry[script_instance.name] = script_instance
                        except Exception as exc:
                            err(f'Failed to load script "{file}": {exc}')
            finally:
                # Clean up system path after module loading
                sys.path.pop(0)
        return dict(sorted(module_registry.items())) # Return alphabetically sorted scripts
    
    def discover_scripts(self) -> dict:
        return self.discover_python_modules('cli-scripts')
    
    def discover_tuis(self) -> dict:
        return self.discover_python_modules('cli-tuis')

    def display_help(self) -> None:
        """
        Displays formatted help message showing available scripts and their basic information.
        Includes usage instructions and a hint for accessing detailed help for specific scripts.
        """
        disclaimer = self.help
        println()
        log(disclaimer)
        help_message = f'Usage:\n    {self.shorthand} <script> [args]\n\nScripts:\n'
        # Format and add each script's information to help message
        max_line_width = max([
            len(f'{script.shorthand}, {script.name}')
            for script in self.scripts.values()
        ] + [
            len(f'{tui.shorthand}, {tui.name}')
            for tui in self.tuis.values()
        ])
        for _, script_key in enumerate(self.scripts):
            script = self.scripts[script_key]
            script_name = script.shorthand + ', ' + script.name
            script_info = f'    {script_name.ljust(max_line_width)}    {script.help}'
            help_message += f'{script_info}\n'
        help_message += f'\nTUIs: {EscapeColor.GRAY}(Terminal User-Interfaces)\n{EscapeColor.RESET}'
        for _, tui_key in enumerate(self.tuis):
            tui = self.tuis[tui_key]
            tui_name = tui.shorthand + ', ' + tui.name
            tui_info = f'    {tui_name.ljust(max_line_width)}    {tui.help}'
            help_message += f'{tui_info}\n'
        log(help_message)
        hint(f'Use `$ {self.shorthand} <script> -h, --help` for more details on specific scripts.', pad_after=1)
        
    #########
    # Hooks #
    #########
    
    def execute(self) -> None:
        """
        Main execution method that handles script discovery, argument parsing,
        and delegation to the appropriate script handler.
        """
        # DEPRECATED: Advising against using this, because it's confusing
            # clear_shell()
        
        # Discover available scripts and create command objects
        self.scripts = self.discover_scripts()
        self.tuis = self.discover_tuis()
        self.commands = [Command(name=script.name, shorthand=script.shorthand, help=script.help) for script in self.scripts.values()]
        self.commands += [Command(name=tui.name, shorthand=tui.shorthand, help=tui.help) for tui in self.tuis.values()]
        self.parse()
        
        # Display help if no arguments provided
        if not self.parsed_arguments and not self.parsed_flags:
            self.display_help()
            return

        try:
            if self.parsed_command in [script.name for script in self.scripts.values()] + [script.shorthand for script in self.scripts.values()]:
                # Resolve script name from command (handle shorthand)
                script_name = self.parsed_command
                for script in self.scripts.values():
                    if script.shorthand == self.parsed_command:
                        script_name = script.name
                        break

                # Execute selected script
                selected_script = self.scripts[script_name]
                # DEPRECATED: Not having to call proxy_mode since hook-call is integrated with base function
                    # selected_script.proxy_mode = False # Disable auto-call to restore default functionality of script
                # Not having to call pre_parse since hook-call is integrated with base function
                selected_script.parse() 
                del selected_script.parsed_arguments[0] # Remove script name from arguments
                selected_script.parsed_command = None
                if len(selected_script.commands) > 0 and len(selected_script.parsed_arguments) > 0:
                    selected_script.parsed_command = selected_script.parsed_arguments[0] # Set command for script
                # Not having to call validate since hook-call is integrated with base function
                selected_script.validate()
                selected_script.pre_execute() # Having to call pre_execute since execute() has to be overriden
                selected_script.execute()
            elif self.parsed_command in [tui.name for tui in self.tuis.values()] + [tui.shorthand for tui in self.tuis.values()]:
                # Resolve tui name from command (handle shorthand)
                tui_name = self.parsed_command
                for tui in self.tuis.values():
                    if tui.shorthand == self.parsed_command:
                        tui_name = tui.name
                        break

                # Execute selected tui
                selected_tui = self.tuis[tui_name]
                # DEPRECATED: Not having to call proxy_mode since hook-call is integrated with base function
                    # selected_tui.proxy_mode = False # Disable auto-call to restore default functionality of tui
                # Not having to call pre_parse since hook-call is integrated with base function
                selected_tui.parse() 
                del selected_tui.parsed_arguments[0] # Remove tui name from arguments
                selected_tui.parsed_command = None
                if len(selected_tui.commands) > 0 and len(selected_tui.parsed_arguments) > 0:
                    selected_tui.parsed_command = selected_tui.parsed_arguments[0] # Set command for tui
                # Not having to call validate since hook-call is integrated with base function
                selected_tui.validate()
                selected_tui.pre_execute() # Having to call pre_execute since execute() has to be overriden
                selected_tui.execute()
            else:
                # If command not found, display help
                err(f'Unknown command: {self.parsed_command}. Use "{self.shorthand}" for help.', exit=True, pad_before=1, pad_after=1)
        except SystemExit:
            pass
        except Exception as e:
            err(f'Error executing script: {e}', exit=True, traceback=True)

if __name__ == '__main__':
    MainCLI()