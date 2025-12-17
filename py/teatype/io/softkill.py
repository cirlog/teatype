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
import os
import time
import signal as io_signal
from enum import IntEnum
from typing import List, Optional

# Third-party imports
import psutil
from teatype.logging import *

class _TerminationStrategy(IntEnum):
    """
    Signal escalation strategy for process termination.
    """
    GRACEFUL=io_signal.SIGINT
    STANDARD=io_signal.SIGTERM
    FORCE=io_signal.SIGKILL

class _ProcessTerminator:
    """
    Handles termination of processes matching specified criteria.
    """
    TERMINATION_SIGNALS = [
        _TerminationStrategy.GRACEFUL,
        _TerminationStrategy.STANDARD,
        _TerminationStrategy.FORCE
    ]
    
    def __init__(self,
                 process_set:set=None,
                 signal_delay:float=0.5,
                 max_attempts:int=3,
                 *,
                 force_signal:Optional[str]=None,
                 silent:bool=False):
        """
        Initialize process terminator.
        
        Args:
            process_set: Set of process identifiers to match.
            signal_delay: Delay between termination attempts in seconds.
            max_attempts: Maximum termination attempts per signal type (default).
            force_signal: Force use of specific signal ('SIGINT', 'SIGTERM', 'SIGKILL').
            silent: Suppress logging output if True.
        """
        self.process_set = process_set or self.DEFAULT_process_set
        self.signal_delay = signal_delay
        self.max_attempts = max_attempts
        self.force_signal = force_signal
        self.silent = silent
    
    def _matches_criteria(self, cmdline:list) -> bool:
        """
        Check if command line matches any process.
        """
        return any(model in arg
                   for arg in cmdline
                   for model in self.process_set)
    
    def _send_signal(self, pid:int, signal:int) -> bool:
        """
        Send signal to process.
        
        Args:
            pid: Process ID.
            sig: Signal number.
            
        Returns:
            True if signal sent successfully.
        """
        try:
            os.kill(pid, signal)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            if not self.silent:
                err('OS denied permission access for process. Please run the script with sudo.', pad_after=1, exit=True, verbose=False)
            return False
        except OSError as e:
            if not self.silent:
                err(f'Failed to signal PID {pid}: {e}', traceback=True)
            return False
    
    def _terminate_process(self, pid:int) -> bool:
        """
        Attempt to terminate process using escalating signals.
        
        Args:
            pid: Process ID to terminate.
            
        Returns:
            True if process terminated successfully.
        """
        # If force_signal is set, use only that signal
        if self.force_signal:
            signal_map = {
                'SIGINT': _TerminationStrategy.GRACEFUL,
                'SIGTERM': _TerminationStrategy.STANDARD,
                'SIGKILL': _TerminationStrategy.FORCE
            }
            signal_type = signal_map.get(self.force_signal)
            if not signal_type:
                if not self.silent:
                    err(f'Invalid force_signal: {self.force_signal}')
                return False
            
            for attempt in range(1, self.max_attempts + 1):
                if not self.silent:
                    print(f'Attempt {attempt}/{self.max_attempts}: Sending {signal_type.name} to PID {pid}')
                
                if not self._send_signal(pid, signal_type):
                    return False
                
                time.sleep(self.signal_delay)
                
                if not psutil.pid_exists(pid):
                    if not self.silent:
                        print(f'PID {pid} terminated successfully on attempt {attempt}')
                    return True
                
                if not self.silent:
                    print(f'PID {pid} still active after attempt {attempt}')
            
            if not self.silent:
                warn(f'Failed to stop process (PID: {pid}) after {self.max_attempts} attempts with {signal_type.name}.')
            return False
        
        # Standard escalation strategy
        for signal_type in self.TERMINATION_SIGNALS:
            for attempt in range(1, self.max_attempts + 1):
                if not self.silent:
                    print(f'Attempt {attempt}/{self.max_attempts}: Sending {signal_type.name} to PID {pid}')
                
                if not self._send_signal(pid, signal_type):
                    return False
                
                time.sleep(self.signal_delay)
                
                if not psutil.pid_exists(pid):
                    if not self.silent:
                        print(f'PID {pid} terminated successfully on attempt {attempt}')
                    return True
                
                if not self.silent:
                    print(f'PID {pid} still active after attempt {attempt}')
            
            if not self.silent:
                warn(f'{signal_type.name} attempts failed. Trying with next signal...')
        
        if not self.silent:
            err('SIGKILL failed. Manual intervention required.')
        return False
    
    def terminate_matching_processes(self) -> int:
        """
        Terminate all processes matching process criteria.
        
        Returns:
            Count of successfully terminated processes.
        """
        termination_count = 0
        try:
            for process in psutil.process_iter(attrs=['pid', 'cmdline']):
                try:
                    cmdline = process.info['cmdline']
                    if not cmdline or not self._matches_criteria(cmdline):
                        continue
                    
                    pid = process.info['pid']
                    if self._terminate_process(pid):
                        termination_count += 1
                        if not self.silent:
                            print(f'Process (PID: {pid}) has been stopped.')
                    else:
                        if not self.silent:
                            err(f'Process (PID: {pid}) could not be stopped. Manual intervention required.')
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            if not self.silent:
                err(f'Error during process iteration:', traceback=True)
        return termination_count

# Convenience function for backward compatibility and ease of use
def softkill(process_set:List[str], 
             delay:float=0.5,
             max_attempts:int=3,
             *,
             force_signal:Optional[str]=None,
             silent:bool=False,) -> int:
    """
    Terminate processes matching process identifiers.
    
    Args:
        process_set: List of process identifiers to match in command lines.
        delay: Delay between termination attempts in seconds.
        max_attempts: Default maximum attempts per signal type.
        force_signal: Force use of specific signal ('SIGINT', 'SIGTERM', 'SIGKILL').
        silent: Suppress logging output.
        
    Returns:
        Count of successfully terminated processes.
    """
    terminator = _ProcessTerminator(set(process_set),
                                    delay,
                                    max_attempts,
                                    force_signal=force_signal,
                                    silent=silent)
    return terminator.terminate_matching_processes()