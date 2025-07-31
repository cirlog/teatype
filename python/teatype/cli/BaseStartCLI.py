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

# From system imports
from abc import abstractmethod

# From package imports
from teatype.cli import BaseCLI, BaseStopCLI
from teatype.io import env, file, path, shell
from teatype.logging import err, hint, log, warn

# From-as system imports
from importlib import util as iutil

# From-as package imports
from teatype.io import TemporaryDirectory as TempDir

class BaseStartCLI(BaseCLI):
    def __init__(self, 
                 auto_init:bool=True,
                 auto_parse:bool=True,
                 auto_validate:bool=True,
                 auto_execute:bool=True):
        # TODO: Put this into BaseCLI instead, but with call_stack=2
        # Skipping 1 step in the call stack to get the script path implementing this class
        self.parent_path = path.caller_parent(reverse_depth=2, skip_call_stacks=1)
        
        # Construct the path to the module configuration file
        config_path = path.join(self.parent_path, 'config', 'module.cfg')
        if file.exists(config_path):
            # Read the configuration file and assign its contents to self.module_config
            self.module_config = file.read(config_path)
        else:
            self.module_config = None
        
        super().__init__(auto_init=auto_init,
                         auto_parse=auto_parse,
                         auto_validate=auto_validate,
                         auto_execute=auto_execute)
    
    def meta(self):
        return {
            'name': 'start',
            'shorthand': 's',
            'help': 'Start a process',
            'flags': [
                {
                    'short': 'a',
                    'long': 'auto',
                    'help': 'Start module with default configuration',
                    'required': False
                },
                {
                    'short': 'd',
                    'long': 'detached',
                    'help': 'Start process in detached mode',
                    'required': False
                },
                {
                    'short': 'ir',
                    'long': 'ignore-running',
                    'help': 'Ignore if process is already running',
                    'required': False
                },
                {
                    'short': 's',
                    'long': 'silent',
                    'help': 'Silent mode (no output)',
                    'required': False
                },
                {
                    'short': 't',
                    'long': 'tail',
                    'help': 'Tail logs of process',
                    'required': False
                }
            ]
        }
        
   # TODO: Decouple this class from Start into BaseCLI to prevent DRY
    def load_compatible_scripts(self, silent_mode:bool=False):
        """
        Discover and import all Python scripts in the `scripts/` directory, skipping __init__.py and non-Python files.
        """
        scripts = {}
        # Get the parent directory of the current script
        scripts_directory = path.caller_parent(skip_call_stacks=4)
        target_script = 'stop'
        # Create a temporary directory within the scripts directory for renaming and importing modules
        with TempDir(directory_path=scripts_directory) as temp_dir:
            try:
                stop_script_found = False
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
                        if formatted_module_name != target_script:
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
                                err('An error occurred during file copy: {exc}')
                                
                            # Create a module spec from the temporary file location
                            spec = iutil.spec_from_file_location(formatted_module_name, temp_filepath)
                            # Create a new module based on the spec
                            module = iutil.module_from_spec(spec)
                            # Execute the module to populate its namespace (this does not instantiate Stop)
                            spec.loader.exec_module(module)
                            # Convert the snake_case module name to CamelCase for class identification
                            camel_case_name = ''.join(word.capitalize() for word in formatted_module_name.split('_'))
                            # Retrieve the class from the module by name
                            script_class = getattr(module, camel_case_name, None)
                            if not script_class:
                                continue
                            if inspect.isclass(script_class):
                                # Only proceed if the class inherits from any of these bases
                                if not issubclass(script_class, (BaseCLI, BaseStopCLI)):
                                    continue
                                
                            # Execute the module to load its contents
                            spec.loader.exec_module(module)
                            # Ensure the retrieved class exists, is a class type, and is a subclass of BaseStopCLI
                            if camel_case_name == 'Stop' or camel_case_name == 'BaseStopCLI':
                                # Having to use "camel_case_name == 'BaseStopCLI'" even though issubclass(script_class, BaseStopCLI) should work
                                # But after 30 minutes of debugging, I am tired of this stupid shit not working even though it should
                                # And it works perfectly fine in the stop script with the check-running relation
                                # I am convinced at this point that the line above has been vodoo cursed by someone I wronged
                                # in my life (probably an ex-girlfriend) and I have been working with cursed lines all along,
                                # so I just gave up and am ready to move on even though I don't want to
                                # https://www.youtube.com/watch?v=bH17fIsYirI&ab_channel=SimonDToppin
                                
                                # Instantiate the class without automatic validation or execution
                                stop = script_class(auto_validate=False,
                                                    auto_execute=False)
                                stop.scripts_directory = scripts_directory
                                # Set the '--silent' flag to suppress verbose output
                                stop.set_flag('silent', True)
                                # Perform any necessary pre-execution setup
                                stop.pre_execute()
                                # Execute the script
                                stop.execute()
                                stop_script_found = True
                            if stop_script_found:
                                break
                        except Exception as exc:
                            if formatted_module_name == target_script:
                                if not silent_mode:
                                    # Log an error if loading the script fails
                                    err(f'Error loading script "{filename}": {exc}, skipping ...',
                                        use_prefix=False,
                                        verbose=False)
                if not stop_script_found:
                    if not silent_mode:
                        warn('No "stop" script found in scripts directory. Only limited functionality available.')

            finally:
                # Ensure the temporary directory is removed from sys.path after import
                sys.path.pop(0)

        # Sort the scripts dictionary by keys for consistent ordering
        scripts = dict(sorted(scripts.items()))
        return scripts
    
    #########
    # Hooks #
    #########
    
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
            
        # TODO: Put this into config instead
        if not hasattr(self, 'process_name'):
            err('No "self.process_name" provided in source code. Please provide a process name to start in the pre_execute function.',
                exit=True)
            
        silent_mode = self.get_flag('silent')        
        if not silent_mode:
            # Notify user that auto configuration discovery is initiated
            hint('"auto_find_config" automatically set to "True". Auto-finding module configuration...', pad_before=1)

        if self.module_config == None:
            if not silent_mode:
                warn('No module configuration found. Limited functionality available.')
        else:
            if not silent_mode:
                # Log the successful application of the module configuration
                log('Module configuration found. Applying configuration to "self.module_config".')
                
        ignore_running = self.get_flag('ignore-running')
        if not ignore_running:
            self.load_compatible_scripts(silent_mode=silent_mode)
            
        # Auto-nativaging after loading compatible scripts, to not mess with the functionality of the algorithm
        # Determine the parent directory of the current script
        parent_directory = path.caller_parent(reverse_depth=2, skip_call_stacks=3)
        # Change the working directory to the parent directory
        os.chdir(parent_directory)
        
        # If the 'detached' flag is set, run the command in the background
        detached = self.get_flag('detached')
        if detached:
            path.create('./logs') # Create a logs directory if it does not exist
            # Append shell redirection to merge stderr with stdout
            stdout_path = path.join('./logs', f'_{self.process_name}.stdout')
            self.start_command += f' > {stdout_path} 2>&1 &'
        
        if file.exists('./.env'):
            env.load() # Load the environment variables
        else:
            warn('No ".env" file found. Limited functionality available.', verbose=False)
        
        def signal_handler(signum, _):
            """
            Handle incoming signals and perform appropriate actions based on the signal type.

            Args:
                signum (int): The signal number received.
                _ (Any): Additional arguments (unused).

            This function is designed to handle various signals sent to the process.
            It logs a warning message indicating which signal was received and then exits
            the process gracefully or forcefully based on the signal type.
            """
            try:
                # Attempt to retrieve the name of the received signal
                signal_name = signal.Signals(signum).name
            except ValueError:
                # If the signal number is unrecognized, assign a default message
                signal_name = f'Unknown signal ({signum})'
            
            warning_addendum = ''
            # Check if the signal is SIGSTOP or SIGINT to provide additional context
            if signum == signal.SIGSTOP or signum == signal.SIGINT:
                warning_addendum = ' (possibly user keyboard interrupt)'
            
            if not silent_mode:
                # Log a warning indicating that the process was killed by a specific signal
                warn(f'Process killed by {signal_name} signal{warning_addendum}.', pad_before=2)
            
            try:
                self.implemented_trap()
                
                if not silent_mode:
                    hint('Executed implemented trap.', pad_after=1)
            except:
                if not silent_mode:
                    warn('No implemented trap found.', pad_after=1)
            
            # Determine the exit code based on the signal type
            # WARNING: Doubly making sure that the process is killed (maybe a bad idea)?
            if signum == signal.SIGSTOP or signum == signal.SIGINT:
                # Exit with code 0 for graceful termination on interrupt signals
                exit(0)
            else:
                # Exit with code 1 for other signals indicating abnormal termination
                exit(1)

        # WARNING: You cannot catch the SIGKILL signal, it is a kernel-level signal and cannot be caught
        #          by the process, so do NOT even bother to try to catch it, it is a waste of time
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        signal.signal(signal.SIGUSR1, signal_handler)
        signal.signal(signal.SIGUSR2, signal_handler)
        
        if not silent_mode:
            # Notify user that auto activation is attempted
            hint('"auto_activate_venv" automatically set to "True". Trying to activate a possibly present virtual environment ...',
                pad_before=1)
        
        venv_path = ''
        venv_found = False  # Initialize flag to track if a virtual environment is found
        # Iterate through all files in the parent directory to locate a virtual environment
        for f in file.list(self.parent_path):
            if 'venv' in f.name:
                venv_path = f.path # Store the path of the found virtual environment
                if not silent_mode:
                    log(f'Virtual environment {f.name} found.') # Log the discovery of the virtual environment
                venv_found = True # Update the flag as a virtual environment is found
                break # Exit the loop since the virtual environment has been found
            
        env.set('VIRTUAL_ENV', venv_path) # Set the VIRTUAL_ENV environment variable to an empty string
        env.set('PYTHONUNBUFFERED', '1') # Set the PYTHONUNBUFFERED environment variable to '1'
        env.set('PYTHONDONTWRITEBYTECODE', '1') # Set the PYTHONDONTWRITEBYTECODE environment variable to '1'
        if not venv_found:
            if not silent_mode:
                # Warn the user if no virtual environment is found, indicating limited functionality
                warn('No virtual environment found. Script functionality may be limited.', pad_after=1)
            shell(self.start_command)
        else:
            try:
                # Attempt to activate the found virtual environment
                if not silent_mode:
                    log('Virtual environment activated.') # Log successful activation
                shell(f'. {venv_path}/bin/activate && {self.start_command}')
            except Exception as e:
                if not silent_mode:
                    # Log an error if activation fails, providing the exception details
                    err('An error occurred while trying to activate the virtual environment:', e)
        
        if detached:
            if self.get_flag('tail'):
                shell(f'tail -f {stdout_path}')
        else:
            signal_handler(signal.SIGSTOP, None) # Kill the process after successful activation
        
    ####################
    # Abstract methods #
    ####################
    
    @abstractmethod
    def pre_execute(self):
        raise NotImplementedError('The "pre_execute" method must be implemented in the derived class.')