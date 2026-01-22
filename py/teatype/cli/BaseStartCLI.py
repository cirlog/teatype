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
import datetime
import inspect
import os
import signal
import shutil
import sys
import threading
from abc import abstractmethod
from importlib import util as iutil

# Third-party imports
from teatype.cli import BaseCLI, BaseStopCLI
from teatype.io import env, file, path, shell
from teatype.logging import *
from teatype.io import TemporaryDirectory as TempDir
from watchfiles import watch

class BaseStartCLI(BaseCLI):
    LOGS_PATH:str='/var/log'
    
    def __init__(self, 
                 auto_init:bool=True,
                 auto_parse:bool=True,
                 auto_validate:bool=True,
                 auto_execute:bool=True,
                 auto_parent_path:bool=True):
        
        if auto_parent_path:
            # TODO: Put this into BaseCLI instead, but with call_stack=2
            # Skipping 1 step in the call stack to get the script path implementing this class
            self.parent_path = path.caller_parent(reverse_depth=2, skip_call_stacks=-1)
        
            # Construct the path to the module configuration file
            config_path = path.join(self.parent_path, 'config', 'module.cfg')
            if file.exists(config_path):
                # Read the configuration file and assign its contents to self.module_config
                self.module_config = file.read(config_path)
            else:
                self.module_config = None
        else:
            self.parent_path = None
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
                    'shorthand': 'd',
                    'name': 'detached',
                    'help': 'Start process in detached mode',
                    'required': False
                },
                {
                    'shorthand': 'ir',
                    'name': 'ignore-running',
                    'help': 'Ignore if process is already running',
                    'required': False
                },
                {
                    'shorthand': 'ht',
                    'name': 'hot-reload',
                    'help': 'Hot-reload on file changes',
                    'required': False
                },
                {
                    'shorthand': 's',
                    'name': 'silent',
                    'help': 'Silent mode (no output)',
                    'required': False
                },
                {
                    'shorthand': 't',
                    'name': 'tail',
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
        scripts_directory = path.caller_parent(skip_call_stacks=-1)
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
                                self.stop = script_class(auto_validate=False,
                                                         auto_execute=False)
                                self.stop.scripts_directory = scripts_directory
                                # Perform any necessary pre-execution setup
                                self.stop.pre_execute()
                                # Execute the script
                                self.stop.execute()
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
                        warn('No "stop" script found. Creating default in-memory stop script using process_name...')
                    # Create default in-memory stop script using process_name from start script
                    self._create_default_stop_script(scripts_directory, silent_mode)
            finally:
                # Ensure the temporary directory is removed from sys.path after import
                sys.path.pop(0)

        # Sort the scripts dictionary by keys for consistent ordering
        scripts = dict(sorted(scripts.items()))
        return scripts
    
    def _create_default_stop_script(self, scripts_directory:str, silent_mode:bool=False):
        """
        Create a default in-memory stop script that uses the process_name from the start script.
        This is used when no stop script is found in the scripts directory.
        """
        from teatype.cli import BaseIsRunningCLI
        from teatype.cli.BaseStopCLI import BaseStopCLI as StopCLIBase
        
        # Get the process_name from the start script (set in pre_execute)
        if not hasattr(self, 'process_name'):
            if not silent_mode:
                warn('Cannot create default stop script: no "self.process_name" defined in start script.')
            return
        
        process_name = self.process_name
        
        # Create a dynamic IsRunning class that uses the process_name
        class DefaultIsRunning(BaseIsRunningCLI):
            def __init__(self, process_names_list, **kwargs):
                self._process_names_list = process_names_list
                super().__init__(**kwargs)
                
            def pre_execute(self):
                self.process_names = self._process_names_list
        
        # Store reference for use in DefaultStop
        default_is_running_cls = DefaultIsRunning
        
        # Create a dynamic Stop class that uses the DefaultIsRunning
        class DefaultStop(StopCLIBase):
            def __init__(self, process_names_list, **kwargs):
                self._process_names_list = process_names_list
                super().__init__(**kwargs)
            
            def load_script(self):
                """
                Override to use the in-memory IsRunning instead of loading from file.
                """
                # Create the is_running instance with the process names
                self.is_running = default_is_running_cls(
                    self._process_names_list,
                    auto_validate=False,
                    auto_execute=False
                )
                self.is_running.set_flag('silent', True)
                self.is_running.pre_execute()
                self.process_pids = self.is_running.execute()
                self.process_names = self.is_running.process_names
        
        # Instantiate the default stop script
        self.stop = DefaultStop(
            [process_name],
            auto_validate=False,
            auto_execute=False
        )
        self.stop.scripts_directory = scripts_directory
        # NOTE: Only store the stop script here, do NOT execute it yet.
        # Execution happens in _run_with_reloader when a restart is needed.
        
        if not silent_mode:
            log(f'Default stop script created for process: "{process_name}"')

    # TODO: Implement exclude paths from reloader
    # TODO: Make sure that multiple rapid changes do not trigger multiple restarts
    def _run_with_reloader(self, full_cmd:str, watch_paths:list[str], silent_mode:bool=False, detached:bool=False):
        # If detached mode, fork the watcher process to run in background
        if detached:
            pid = os.fork()
            if pid > 0:
                # Parent process - return immediately
                if not silent_mode:
                    log(f'[reloader] started in background with PID {pid}')
                return
            else:
                # Child process - detach from terminal
                os.setsid()  # Create new session, detach from controlling terminal
                # Redirect stdin/stdout/stderr to /dev/null for true detachment
                sys.stdin = open(os.devnull, 'r')
                sys.stdout = open(os.devnull, 'w')
                sys.stderr = open(os.devnull, 'w')
                silent_mode = True  # Force silent mode in detached child
        
        restarting = False
        lock = threading.Lock()
        
        def start_process():
            # Don't add combine_stdout_and_stderr here as the command may already
            # have redirections (e.g., from --detached mode adding tee/dev/null)
            shell(full_cmd,
                  detached=True)

        def stop_process():
            # Perform any necessary pre-execution setup
            self.stop.pre_execute()
            # Execute the script
            self.stop.execute()
            
        self.stop.set_flag('silent', True)
        self.stop.set_flag('sleep', 0.25)
            
        start_process()

        try:
            if not silent_mode:
                log(f'[reloader] watching for changes in: {", ".join(watch_paths)}')

            for changes in watch(*watch_paths, recursive=True):
                # Filter only .py changes and ignore obvious noise
                changes_detected = [
                    (change, path_str)
                    for (change, path_str) in changes
                    if 'venv/' not in path_str
                    # and path_str.endswith('.py')
                    and '~temp' not in path_str
                    and '.venv/' not in path_str
                    and '/logs/' not in path_str
                    and 'pycache' not in path_str
                ]
                if not changes_detected:
                    continue

                with lock:
                    if restarting:
                        if not silent_mode:
                            log('[reloader] change detected but restart already in progress, skipping.')
                        continue
                    restarting = True

                if not silent_mode:
                    println()
                    warn(f'[reloader] {len(changes_detected)} .py change(s) detected. Restarting ...', include_symbol=True, use_prefix=False)
                    println()

                stop_process()
                start_process()

                with lock:
                    restarting = False
        except KeyboardInterrupt:
            if not silent_mode:
                println()
                warn('[reloader] keyboard interrupt detected, shutting down gracefully...', pad_before=1)
        finally:
            stop_process()
    
    #########
    # Hooks #
    #########
    
    def execute(self):
        """
        Executes the start command to initiate the process.

        This method performs the following steps:
            - Checks if 'start_command' is defined.
            - Changes the current working directory to its parent directory.
            - Appends shell redirections to the start command.
            - Executes the start command, optionally in detached mode.
            - Handles keyboard interrupts gracefully.
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

        if self.module_config is None:
            if not silent_mode:
                warn('No module configuration found. Limited functionality available.')
        else:
            if not silent_mode:
                # Log the successful application of the module configuration
                log('Module configuration found. Applying configuration to "self.module_config".')
                
        ignore_running = self.get_flag('ignore-running')
        if not ignore_running:
            self.load_compatible_scripts(silent_mode=silent_mode)
            
        # Auto-navigating after loading compatible scripts, to not mess with the functionality of the algorithm
        os.chdir(self.parent_path)
    
        # If the 'detached' flag is set, run the command in the background
        self.stdout_path = path.join('./logs', f'_{self.process_name}.stdout')
        detached = self.get_flag('detached')
        if detached:
            path.create('./logs') # Create a logs directory if it does not exist
            
            # Create logs directory structure with process name and current date
            logs_base = path.join(self.LOGS_PATH, self.process_name)
            if not path.exists(logs_base):
                try:
                    path.create(logs_base)
                except PermissionError:
                    denied_logs_base = logs_base
                    logs_base = path.join('/home', env.get('USER'), 'logs', self.process_name)
                    err(f'Permission denied while creating logs directory at {denied_logs_base}. Trying to create folder under ${logs_base} instead.',
                        include_symbol=True,
                        use_prefix=False,
                        verbose=False)
                    try:
                        path.create(logs_base)
                    except Exception as e:
                        err(f'Failed to create logs directory at {logs_base} as well: {e}',
                            exit=True)
            
            today = datetime.date.today().strftime('%Y-%m-%d')
            logs_daily = path.join(logs_base, today)
            if not path.exists(logs_daily):
                path.create(logs_daily)
                success(f'Created daily logs directory at {logs_daily}.',
                        include_symbol=True)

            # Create secondary log file with current time as filename
            current_time = datetime.datetime.now().strftime('%H-%M-%S')
            secondary_log_path = path.join(logs_daily, f'{current_time}.log')

            # Append shell redirection to merge stderr with stdout and pipe to tee for both logs
            # Redirect tee's output to /dev/null to prevent terminal output in detached mode
            self.start_command = f'{self.start_command} 2>&1 | tee {self.stdout_path} {secondary_log_path} > /dev/null'
        
        if file.exists('./.env'):
            env.load() # Load the environment variables
        else:
            warn('No ".env" file found. Limited functionality available.')
        
        def signal_handler(signum, _):
            """
            Handle incoming signals and perform appropriate actions based on the signal type.
            """
            try:
                signal_name = signal.Signals(signum).name
            except ValueError:
                signal_name = f'Unknown signal ({signum})'
            
            warning_addendum = ''
            if signum == signal.SIGSTOP or signum == signal.SIGINT:
                warning_addendum = ' (possibly user keyboard interrupt)'
            
            if not silent_mode:
                warn(f'Process killed by {signal_name} signal{warning_addendum}.', pad_before=2)
            
            try:
                self.implemented_trap()
                
                if not silent_mode:
                    hint('Executed implemented trap.', pad_after=1)
            except:
                if not silent_mode:
                    warn('No implemented trap found.', pad_after=1)
            
            # WARNING: Doubly making sure that the process is killed (maybe a bad idea)?
            if signum == signal.SIGSTOP or signum == signal.SIGINT:
                exit(0)
            else:
                exit(1)

        # WARNING: You cannot catch SIGKILL.
        signal.signal(signal.SIGINT,  signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP,  signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        signal.signal(signal.SIGUSR1, signal_handler)
        signal.signal(signal.SIGUSR2, signal_handler)
    
        if not silent_mode:
            hint('"auto_activate_venv" automatically set to "True". Trying to activate a possibly present virtual environment ...',
                 pad_before=1)
        
        venv_name = None
        venv_path = ''
        venv_found = False

        if hasattr(self, 'venv_name'):
            venv_name = self.venv_name
            venv_path = path.join(self.parent_path, venv_name)
            if not path.exists(venv_path):
                err(f'Virtual environment {venv_name} does not exist.')
                venv_found = False
            else:
                venv_found = True
        
        if not venv_name:
            if not silent_mode:
                warn('No self.venv_name in start-script specified, trying to locate venv automatically instead ...')
            # Iterate through all files in the parent directory to locate a virtual environment
            for f in file.list(self.parent_path):
                if 'venv' in f.name:
                    venv_path = f.path
                    if not silent_mode:
                        log(f'Virtual environment {f.name} found.')
                    venv_found = True
                    break

        env.set('VIRTUAL_ENV', venv_path)
        env.set('PYTHONUNBUFFERED', '1')
        env.set('PYTHONDONTWRITEBYTECODE', '1')

        if not venv_found:
            if not silent_mode:
                warn('No virtual environment found. Script functionality may be limited.', pad_after=1)
            full_cmd = self.start_command
        else:
            if not silent_mode:
                log('Virtual environment activated.')
            full_cmd = f'. {venv_path}/bin/activate && {self.start_command}'

        reload_enabled = self.get_flag('hot-reload')
        if reload_enabled:
            # Watch the module directory for changes and restart on .py edits
            watch_paths = [self.parent_path]
            self._run_with_reloader(full_cmd, watch_paths=watch_paths, silent_mode=silent_mode, detached=detached)
            # signal_handler(signal.SIGSTOP, None) # Kill the process after successful activation
            return

        # Normal (non-reload) behaviour
        try:
            shell(full_cmd,
                  combine_stdout_and_stderr=True,
                  detached=True if detached else False)
        except Exception as e:
            if not silent_mode:
                err('An error occurred while trying to start the process:', e)
        
        if detached:
            if self.get_flag('tail'):
                shell(f'tail -f {self.stdout_path}')
        else:
            signal_handler(signal.SIGSTOP, None) # Kill the process after successful activation
        
    ####################
    # Abstract methods #
    ####################
    
    @abstractmethod
    def pre_execute(self):
        raise NotImplementedError('The "pre_execute" method must be implemented in the derived class.')
