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
import time

from teatype.enum import EscapeColor
from teatype.logging import err, log

class GLOBAL_STOPWATCH_CONFIG:
    """
    Global configuration for the stopwatch utility.
    """
    DISABLE_STOPWATCHES:bool=True
    PRINT_START:bool=False
    TIME_CONVERSION:bool=False

def stopwatch(label: str = None):
    """
    Using class and function closure to measure execution time between calls.
    If called with a label, it starts the timer and stores the label.
    If called without a label, it prints the elapsed time since the last labeled call.
    A new stopwatch cannot be started if the previous stopwatch hasn't been closed.
    """
    # Check if the stopwatches are disabled
    if GLOBAL_STOPWATCH_CONFIG.DISABLE_STOPWATCHES:
        # If stopwatches are disabled in the global config, exit the function
        return

    # Internal state to track the timer
    state = getattr(stopwatch, '_state', None)
    if state is None:
        # Initialize the state if it doesn't exist
        stopwatch._state = state = {"active": False}

    # Check for an active stopwatch
    if state["active"] and label:
        # If a stopwatch is already active and a new label is provided, log an error
        err(f'Stopwatch "{state["last_label"]}" is still active. Close it before starting a new one.', exit=True)

    if label:
        # Start a timer for the given label
        state['last_label'] = label # Store the label of the current stopwatch
        state[label] = time.time() # Record the start time
        state['active'] = True # Mark the stopwatch as active
        if GLOBAL_STOPWATCH_CONFIG.PRINT_START:
            # Optionally log the start of the stopwatch
            log(f'Started stopwatch for "{label}".')
    else:
        # Ensure there is a previous label to calculate elapsed time
        last_label = state.get('last_label')
        if last_label and last_label in state:
            # Calculate the elapsed time since the stopwatch started
            elapsed = time.time() - state[last_label]

            if GLOBAL_STOPWATCH_CONFIG.TIME_CONVERSION:
                # Convert the elapsed time to a human-readable format
                if elapsed < 1e-6:
                    elapsed = f'{elapsed * 1e9:.2f} nanoseconds'
                elif elapsed < 1e-3:
                    elapsed = f'{elapsed * 1e6:.2f} microseconds'
                elif elapsed < 1:
                    elapsed = f'{elapsed * 1e3:.2f} milliseconds'
                elif elapsed < 60:
                    elapsed = f'{elapsed:.2f} seconds'
                elif elapsed < 3600:
                    minutes = int(elapsed // 60)
                    seconds = elapsed % 60
                    elapsed = f'{minutes} minutes, {seconds:.2f} seconds'
                else:
                    hours = int(elapsed // 3600)
                    minutes = int((elapsed % 3600) // 60)
                    seconds = elapsed % 60
                    elapsed = f'{hours} hours, {minutes} minutes, {seconds:.2f}'
            else:
                # Default format for elapsed time
                elapsed = f'{elapsed:.4f} seconds'

            # Log the elapsed time with appropriate color formatting
            log(f'{EscapeColor.BLUE}Stopwatch {EscapeColor.LIGHT_CYAN}[{last_label}]{EscapeColor.LIGHT_GREEN}: {elapsed}.')
            state['active'] = False # Mark the stopwatch as inactive
        else:
            # Log an error if there is no active stopwatch to measure
            err(f'No active stopwatch found to measure elapsed time.')