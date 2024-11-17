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
import time

# From package imports
from teatype.cli import BaseCLI, CheckIfRunning
from teatype.logging import err, hint, log, nl, warn

# From-as system imports
from importlib import util as iutil

# From-as package imports
from teatype.io import TemporaryDirectory as TempDir

class Stop(BaseCLI):
    def meta(self):
        return {
            'name': 'stop',
            'shorthand': 'sp',
            'help': 'Stop a process',
            'flags': [
                # TODO: Implement hide-output flag
                {
                    'short': 'f',
                    'long': 'force-signal',
                    'help': 'Force a specific signal',
                    'options': ['SIGINT', 'SIGTERM', 'SIGKILL'],
                    'required': False
                },
                {
                    'short': 'h',
                    'long': 'hide-output',
                    'help': 'Hide verbose output of script',
                    'required': False
                },
                {
                    'short': 's',
                    'long': 'sleep',
                    'help': 'Sleep time between process checks',
                    'options': [0.25, 0.5, 1, 2, 3],
                    'required': False
                }
            ],
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

                            # Ensure the retrieved class exists, is a class type, and is a subclass of CheckIfRunning
                            if script_class and inspect.isclass(script_class) and issubclass(script_class, CheckIfRunning):
                                # Instantiate the class without automatic validation or execution
                                self.check_if_running = script_class(auto_validate=False,
                                                                     auto_execute=False)
                                # Set the '--hide-output' flag to suppress verbose output
                                self.check_if_running.set_flag('hide-output', True)
                                # Validate the arguments provided to the script
                                # self.check_if_running.validate_args()
                                # Perform any necessary pre-execution setup
                                self.check_if_running.pre_execute()
                                # Execute the script and retrieve the list of process PIDs
                                self.process_pids = self.check_if_running.execute()

                        except Exception as e:
                            # Log an error if loading the script fails
                            err(f'Error loading script "{filename}": {e}')

            finally:
                # Ensure the temporary directory is removed from sys.path after import
                sys.path.pop(0)

        # Sort the scripts dictionary by keys for consistent ordering
        scripts = dict(sorted(scripts.items()))
        return scripts
        
    def is_process_running(self, pid):
        """
        Check if a process with the given PID is currently running.

        Args:
            pid (int): Process ID to check.

        Returns:
            bool: True if the process is running, False otherwise.
        """
        try:
            # Sending signal 0 does not kill the process but checks its existence
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def attempt_stop(self, pid, signal_type, max_attempts, signal_name):
        """
        Attempt to stop a process by sending a specific signal, retrying up to a maximum number of attempts.

        Args:
            pid (int): Process ID to stop.
            signal_type (int): Signal to send (e.g., signal.SIGTERM).
            max_attempts (int): Maximum number of attempts to send the signal.
            signal_name (str): Name of the signal for logging purposes.

        Returns:
            bool: True if the process was successfully stopped, False otherwise.
        """
        attempts = 0
        while self.is_process_running(pid):
            if attempts >= max_attempts:
                # Warn if maximum attempts have been reached without success
                warn(f"Failed to stop process (PID: {pid}) after {max_attempts} attempts with {signal_name}.")
                return False
            # Log the attempt to stop the process
            log(f"Attempt {attempts + 1} to stop process (PID: {pid}) with {signal_name}...")
            try:
                # Send the specified signal to the process
                os.kill(pid, signal_type)
            except OSError as e:
                # Log an error if sending the signal fails
                err(f"Error sending signal {signal_name} to PID {pid}: {e}")
                return False
            attempts += 1
            # Wait for a short period before the next attempt
            sleep = 1
            if self.get_flag('sleep'):
                sleep = self.get_flag('sleep')
            time.sleep(sleep)
        # Log success if the process has been stopped
        log(f"Process (PID: {pid}) stopped using {signal_name}.")
        return True

    def stop_process(self, pid):
        """
        Attempt to stop a process using SIGINT, then SIGTERM, and finally SIGKILL if necessary.

        Args:
            pid (int): Process ID to stop.

        Returns:
            bool: True if the process was successfully stopped, False otherwise.
        """
        MAX_SIGINT_ATTEMPTS = 3
        MAX_SIGTERM_ATTEMPTS = 3
        MAX_SIGKILL_ATTEMPTS = 3
        
        force_signal = self.get_flag('force-signal')
        if force_signal:
            match force_signal:
                case 'SIGINT':
                    if not self.attempt_stop(pid, signal.SIGINT, MAX_SIGINT_ATTEMPTS, "SIGINT"):
                        return False
                case 'SIGTERM':
                    if not self.attempt_stop(pid, signal.SIGTERM, MAX_SIGTERM_ATTEMPTS, "SIGTERM"):
                        return False
                case 'SIGKILL':
                    if not self.attempt_stop(pid, signal.SIGKILL, MAX_SIGKILL_ATTEMPTS, "SIGKILL"):
                        return False
        else:
            # Attempt to stop the process using SIGINT
            if not self.attempt_stop(pid, signal.SIGINT, MAX_SIGINT_ATTEMPTS, "SIGINT"):
                # Warn and attempt to stop using SIGTERM if SIGINT fails
                warn("SIGINT attempts failed. Trying with SIGTERM...")
                if not self.attempt_stop(pid, signal.SIGTERM, MAX_SIGTERM_ATTEMPTS, "SIGTERM"):
                    # Warn and attempt to stop using SIGKILL if SIGTERM fails
                    warn("SIGTERM attempts failed. Trying with SIGKILL...")
                    if not self.attempt_stop(pid, signal.SIGKILL, MAX_SIGKILL_ATTEMPTS, "SIGKILL"):
                        # Log an error if all attempts fail
                        err("SIGKILL failed. Manual intervention required.")
                        return False
        return True
    
    def recursive_kill(self):
        """
        Recursively attempt to kill all processes in the process_pids list until no processes remain.
        """

        # Execute the check_if_running to update the list of process PIDs
        self.process_pids = self.check_if_running.execute()
        if len(self.process_pids) == 0:
            # Inform the user if there are no more processes to stop
            log('No more processes alive.')
            return
        
        # Iterate over each PID in the process_pids list
        for process_pids in self.process_pids:
            if self.is_process_running(process_pids):
                # Attempt to stop the process and log the result
                if self.stop_process(process_pids):
                    log(f'Process (PID: "{process_pids}") has been stopped.')
                else:
                    # Log an error if the process could not be stopped
                    err(f'Process (PID: "{process_pids}") could not be stopped. Manual intervention required.')
            else:
                # Log if the process is not running
                log(f'Process (PID: "{process_pids}") is not running.')
            nl()
                
        if len(self.process_pids) > 0:
            # Recursively call itself to handle any remaining processes
            self.recursive_kill()

    def execute(self):
        """
        Execute the stop command by loading scripts, checking for processes, and initiating the kill sequence.
        """
        # Load and import all relevant scripts
        self.load_script()
        
        if len(self.process_pids) == 0:
            nl()
            # Inform the user if there are no processes to stop
            log('No processes to stop.')
        else:
            nl()
            force_signal = self.get_flag('force-signal')
            if force_signal:
                hint(f'Forcing signal: {force_signal}')
            sleep = self.get_flag('sleep')
            if sleep:
                hint(f'Only sleeping {sleep}s seconds between attempts')
            if force_signal or sleep:
                nl()
            # Begin the recursive kill process
            self.recursive_kill()
        
        nl()

if __name__ == '__main__':
    Stop()