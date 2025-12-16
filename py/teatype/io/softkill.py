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
                 max_attempts:int=3):
        """
        Initialize process terminator.
        
        Args:
            process_set: Set of process identifiers to match.
            signal_delay: Delay between termination attempts in seconds.
            max_attempts: Maximum termination attempts per process.
        """
        self.process_set = process_set or self.DEFAULT_process_set
        self.signal_delay = signal_delay
        self.max_attempts = max_attempts
    
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
        except (OSError, PermissionError):
            err(f'Failed to signal PID {pid}', traceback=True)
            return False
    
    def _terminate_process(self, pid:int) -> bool:
        """
        Attempt to terminate process using escalating signals.
        
        Args:
            pid: Process ID to terminate.
            
        Returns:
            True if process terminated successfully.
        """
        for attempt, signal_type in enumerate(self.TERMINATION_SIGNALS, 1):
            print(f'Attempt {attempt}/{self.max_attempts}: Sending {signal_type.name} to PID {pid}')
            
            if not self._send_signal(pid, signal_type):
                return False
            
            time.sleep(self.signal_delay)
            
            if not psutil.pid_exists(pid):
                print(f'PID {pid} terminated successfully on attempt {attempt}')
                return True
            
            print(f'PID {pid} still active after attempt {attempt}')
        
        print(f'PID {pid} could not be terminated. Manual intervention required.')
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
                    
                    if self._terminate_process(process.info['pid']):
                        termination_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            err(f'Error during process iteration:', traceback=True)
        return termination_count

# Convenience function for backward compatibility and ease of use
def softkill(process_set:Optional[List[str]], delay:float=0.5) -> int:
    """
    Terminate processes matching process identifiers.
    """
    terminator = _ProcessTerminator(
        process_set=set(process_set) if process_set else None,
        signal_delay=delay
    )
    return terminator.terminate_matching_processes()