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

# From system imports
from typing import Union

# From package imports
from teatype.enum import EscapeColor
from teatype.logging import err, log

class GLOBAL_STOPWATCH_CONFIG:
    """
    Global configuration for the stopwatch utility.
    """
    DISABLE_STOPWATCHES:bool = False
    PRINT_START:bool = False
    TIME_CONVERSION:bool = False

# Module-specific state tracker, unique to each importing module
STATE = {
    'active': False, # Flag to track if a stopwatch is currently active
    'last_label': None # Label of the last active stopwatch
}

# TODO: Deshittify the stopwatch function, allow specifying label for start and stop to allow nesting
def stopwatch(label:str=None, pad:Union[int,int]=(0,0), tab:int=0):
    """
    Using function closure to measure execution time between calls.
    If called with a label, it starts the timer and stores the label.
    If called without a label, it prints the elapsed time since the last labeled call.
    A new stopwatch cannot be started if the previous stopwatch hasn't been closed in the context of the importing module.
    """
    # Check if the stopwatches are disabled
    if GLOBAL_STOPWATCH_CONFIG.DISABLE_STOPWATCHES:
        # If stopwatches are disabled in the global config, exit the function
        return

    global STATE # Use the global state tracker
    
    # DEPRECATED: Not using class closure to track the timer anymore, using a global state tracker instead
        # # Internal state to track the timer
        # state = getattr(stopwatch, '_state', None)
        # if state is None:
        #     # Initialize the state if it doesn't exist
        #     stopwatch._state = state = {"active": False}

    # Check for an active stopwatch
    if STATE['active'] and label:
        error_message = f'Stopwatch "{STATE["last_label"]}" is still active. Close it before starting a new one.'
        err(f'Code runtime error: {error_message}', traceback=True)
        raise RuntimeError(f'{error_message}')

    if label:
        # Start a timer for the given label
        STATE['last_label'] = label # Store the label of the current stopwatch
        STATE[label] = time.time() # Record the start time
        STATE['active'] = True # Mark the stopwatch as active
        if GLOBAL_STOPWATCH_CONFIG.PRINT_START:
            # Optionally get current time and log the start of the stopwatch
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            start_message = f'Started stopwatch for "{label}" at {current_time}.'
            if tab > 0:
                start_message = f'{"    " * tab}{start_message}'
            log(start_message)
    else:
        # Ensure there is a previous label to calculate elapsed time
        last_label = STATE['last_label']
        if last_label and last_label in STATE:
            # Calculate the elapsed time since the stopwatch started
            elapsed = time.time() - STATE[last_label]

            if GLOBAL_STOPWATCH_CONFIG.TIME_CONVERSION:
                # Convert elapsed time to a human-readable format
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
                # Default to seconds if time conversion is disabled
                elapsed = f'{elapsed:.4f} seconds'
            
            elapsed_mesage = f'{EscapeColor.BLUE}Stopwatch {EscapeColor.LIGHT_CYAN}[{last_label}]{EscapeColor.LIGHT_GREEN}: {elapsed}.'
            # Log the elapsed time with appropriate color formatting
            if tab > 0:
                elapsed_mesage = f'{"    " * tab}{elapsed_mesage}'
            log(elapsed_mesage)
            STATE['active'] = False
        else:
            # Log an error if there is no active stopwatch to measure
            err(f'No active stopwatch found to measure elapsed time.', traceback=True)
            raise RuntimeError('No active stopwatch found to measure elapsed time.')