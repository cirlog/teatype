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
import logging
import traceback as traceback_exc
# import logging.handlers
import os
import sys
from datetime import datetime
from pprint import pformat
from typing import Literal
# Third-party imports
from teatype.enum import EscapeColor
from teatype.toolkit import colorwrap

SymbolPosition = Literal['start', 'center', 'end', None]
SymbolPositions = ['start', 'center', 'end', None]

# TODO: Maybe use class closure like with the old stopwatch, to set global variables once somewhere, for consistency
#       in the file saving, like the path to the log directory, etc.
#       This way, the log directory can be created once and used throughout all files.
class GLOBAL_LOGGING_CONFIG:
    """
    Global logging configuration class to store logging configurations.

    Attributes:
        BASE_LOG_DIR (str): The base directory for storing log files.
        LOG_DIRECTORY (str): The directory to store log files for the current session.
        LOG_FILE (str): The file name to store log messages.
        LOG_FORMAT (str): The format for log messages.
        LOG_LEVEL (int): The minimum log level to capture.
        SURPRESS_CONSOLE (bool): Flag to determine whether to suppress console output.
    """
    BASE_LOG_DIR=os.path.join(os.path.expanduser("~"), "ApplicationLogs")
    LOG_DIRECTORY=os.path.join(BASE_LOG_DIR, datetime.now().strftime("%Y-%m-%d"))
    LOG_NAME="global_custom_logger"
    LOG_FILE="application.log"
    LOG_FORMAT='%(asctime)s - %(levelname)s - %(message)s - [File: %(filename)s, Line: %(lineno)d]'
    LOG_LEVEL=logging.DEBUG
    SURPRESS_CONSOLE=False

def create_log_directory() -> str:
    """
    Create a log directory based on the current date.

    This function generates a directory path by joining the base log directory
    with the current date in YYYY-MM-DD format. It ensures that the directory
    exists by creating it if necessary.

    Returns:
        str: The path to the created or existing log directory.
    """
    log_dir = os.path.join(GLOBAL_LOGGING_CONFIG.BASE_LOG_DIR, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(log_dir, exist_ok=True) # Create directory if it doesn't exist
    return log_dir

class _ColoredFormatter(logging.Formatter):
    """
    ColoredFormatter enhances log messages with ANSI color codes based on the severity level.

    Attributes:
        COLOR_CODES (dict): A dictionary mapping logging levels to their respective ANSI color codes.
            - logging.DEBUG: Blue
            - logging.WARNING: Yellow
            - logging.ERROR: Red
            - logging.CRITICAL: Magenta
        RESET_CODE (str): ANSI code to reset the text color to default.

    Methods:
        format(record):
            Overrides the default format method to prepend and append ANSI color codes to the log message.
            
            Args:
                record (logging.LogRecord): The log record to be formatted.
            
            Returns:
                str: The formatted log message with appropriate color codes.
    """
    # '\033[94m' # Dark Blue
    COLOR_CODES = {
        logging.DEBUG: '\033[96m', # Light Blue
        logging.WARNING: '\033[93m', # Yellow
        logging.ERROR: '\033[91m', # Red
        logging.CRITICAL: '\033[95m', # Magenta
    }
    RESET_CODE = '\033[0m'

    def format(self, record):
        color = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        message = record.getMessage()
        return f'{color}{message}{self.RESET_CODE}'

def _format(message:any,
            include_symbol:bool=False,
            pad_before:int=None,
            prefix:str=None,
            symbol:str|None=None,
            symbol_position:SymbolPosition='start',
            use_prefix:bool=True,
            verbose:bool=False) -> any:
    """
    Formats a message with optional padding and verbosity.
    Only has an effect on terminal logging, not file logging.

    Args:
        message (any, optional): The message to format. Defaults to ''.
        pad_after (int , optional): Number of blank lines to add after the message. Defaults to None.
        pad_before (int , optional): Number of blank lines to add before the message. Defaults to None.
        use_prefix (bool, optional): If True, includes the error prefix in the message. Defaults to True.
        verbose (bool, optional): If True, includes caller's filename and line number. Defaults to False.

    Returns:
        any: The formatted message string.
    """
    if include_symbol:
        if symbol is None:
            raise ValueError('Symbol must be provided if include_symbol is True.')
        if symbol_position not in SymbolPositions or symbol_position is None:
            raise ValueError(f'Symbol position must be one of {SymbolPositions}.')
        
    formatted_message = message  # Initialize the formatted message as an empty string
    
    # Add a blank line before the message if pad_before is specified and greater than 0
    if pad_before and pad_before > 0:
        for _ in range(pad_before):
            println() # Print a blank line to add padding above the message
            
    # If verbose is True, include caller's filename and line number in the message
    if verbose:
        # Traverse the stack to find the frame of the original caller
        stack = inspect.stack()
        for frame_info in stack:
            if 'logging.py' in frame_info.filename:
                continue
            
            if frame_info.function not in ['_format', 'err', 'log']: # Ignore internal functions
                caller_frame = frame_info
                break
        else:
            # Fallback in case no valid frame is found
            caller_frame = stack[-1]
        filename = os.path.basename(caller_frame.filename)
        lineno = caller_frame.lineno
        
        formatted_message = f'{message} - [{filename}, PRINTLN: {lineno}]' # Format the message with caller info
        
    if prefix and use_prefix:
        if include_symbol and symbol_position == 'center':
            formatted_message = f'{prefix} - {symbol} {formatted_message}'
        else:
            formatted_message = f'{prefix} - {formatted_message}'
    
    if include_symbol:
        if symbol_position == 'start':
            formatted_message = f'{symbol} {formatted_message}'
        elif symbol_position == 'end':
            formatted_message = f'{formatted_message} {symbol}'
    
    return formatted_message

def err(message:str,
        *,
        exit=False,
        include_symbol:bool=False,
        pad_before:int=None,
        pad_after:int=None,
        raise_exception:Exception|bool=False,
        symbol_position:SymbolPosition='start',
        use_prefix:bool=True,
        traceback:bool=False,
        verbose:bool=True) -> None:
    """
    Logs an error message and optionally includes the traceback of the current exception.

    Args:
        message (str): The error message to be logged.
        pad_before (int , optional): Number of blank lines to add before the message. Defaults to None.
        pad_after (int , optional): Number of blank lines to add after the message. Defaults to None.
        raise_exception (Exception, optional): If specified, raises the provided exception with the error message.
        traceback (bool, optional): Flag to determine whether to include the traceback.
            Defaults to False.
        use_prefix (bool, optional): If True, includes the error prefix in the message. Defaults to True.
        verbose (bool, optional): If True, includes caller's filename and line number. Defaults to False.
    Returns:
        int: Returns 1 to indicate an error has occurred.
    """
    # Retrieve the current exception information from the system
    exc_info = sys.exc_info()
    
    # Log the error message as a critical error, potentially including the traceback
    if not raise_exception:
        if exit:
            prefix = 'FATAL EXIT ERROR'
        elif traceback:
            prefix = 'FATAL ERROR'
        else:
            prefix = 'ERROR'
    else:
        prefix = None
        use_prefix = False
    error_message = _format(message=message,
                            include_symbol=include_symbol,
                            pad_before=pad_before,
                            prefix=prefix,
                            symbol='❌', # \u274C
                            symbol_position=symbol_position,
                            use_prefix=use_prefix,
                            verbose=verbose)
    
    # Handle the raising of exceptions based on the 'raise_exception' parameter
    if raise_exception:
        # Check if 'raise_exception' is an instance of the Exception class
        if isinstance(raise_exception, bool):
            # If 'raise_exception' is not an Exception instance, raise a generic Exception with the error message
            raise Exception(error_message)
        else:
            # Raise the provided exception with the specified error message
            raise raise_exception(error_message)
    
    # Check if there is an active exception
    if exc_info and exc_info[0] is not None:
        # Log the error message with exception information
        logger.error(error_message, exc_info=True)
        # If an exception exists, proceed to log the error with exception details
        if traceback:
            # Additionally, log the formatted traceback as a critical error
            logger.critical(traceback_exc.format_exc(), exc_info=True)
    else:
        # If no exception is present, log the error message without exception info
        logger.error(error_message)
    
    # Add a blank line after the message if pad_after is specified and greater than 0
    if pad_after:
        println(pad_after) # Print a blank line to add padding below the message
        
    if exit:
        # If the exit flag is set, exit the program with an error code
        sys.exit(1)

def hint(message:str,
         include_symbol:bool=False,
         pad_before:int=None,
         pad_after:int=None,
         symbol_position:SymbolPosition='start',
         use_prefix:bool=True) -> int:
    """
    Provide a hint message with optional padding and verbosity.
    
    Args:
        message (str): The message to display as a hint.
        pad_after (int, optional): Number of blank lines to add below the message. Defaults to None.
        pad_before (int, optional): Number of blank lines to add above the message. Defaults to None.
        verbose (bool, optional): If True, include additional verbosity in the message. Defaults to False.
    Returns:
        int: Status code indicating the outcome of the operation.
    """
    # Format the message with optional padding and verbosity
    hint_message = _format(message,
                           include_symbol=include_symbol,
                           pad_before=pad_before,
                           prefix='HINT',
                           symbol='ℹ️', # \u2139
                           symbol_position=symbol_position,
                           use_prefix=use_prefix,
                           verbose=False)
    
    # Log the final message at the INFO level using the global logger
    logger.debug(hint_message) # Log the message as is
    
    # Add a blank line after the message if pad_after is specified and greater than 0
    if pad_after:
        println(pad_after) # Print a blank line to add padding below the message

# TODO: Instead of using pad before and after use (0, 1) for before and after, respectively
#       This way, the function can be called with a single argument to specify padding
#       and the default value can be set to 0 for no padding
#       Also, allow this: (0,) and (,0) to specify padding before and after, respectively
# TODO: Allow args like in print and the rest as kwargs
def log(message:any,
        *,
        color:EscapeColor.Colors='default',
        pad_after:int=None,
        pad_before:int=None,
        prettify:bool=False,
        tab:int=0,
        verbose:bool=False) -> None:
    """
    Logs a message with optional formatting, padding, and prettification.
    
    This function formats the provided message, optionally adds padding above and below
    the message, prettifies complex objects for better readability, and logs the message
    at the INFO level using the global logger. It returns a status code indicating
    successful logging.
    
    Args:
        message (any, optional): The message to be logged. Defaults to ''.
        color (Colors=Literal['black', 'blue', 'cyan', 'gray', 'green', 'magenta', 'red', 'white', 'yellow', 'light_black', 'light_blue', 'light_cyan', 'light_green', 'light_magenta', 'light_red', 'light_white', 'light_yellow'], optional): The color to apply to the message. Defaults to 'default'.
        pad_after (int , optional): Number of blank lines to add after the message. Defaults to None.
        pad_before (int , optional): Number of blank lines to add before the message. Defaults to None.
        prettify (bool, optional): If True, formats complex objects into a pretty-printed string. Defaults to False.
        verbose (bool, optional): If True, includes caller's filename and line number in the log message. Defaults to False.
    """
    # Format the message with optional padding and verbosity
    log_message = _format(message,
                          verbose=verbose,
                          pad_before=pad_before)
    
    # Check if prettify flag is set to True to format the message for better readability
    if prettify:
        # Use pprint's pformat to convert complex objects into a formatted string with indentation
        pretty_string = pformat(message, indent=2)
        
        # Split the pretty-printed string into individual lines for processing
        lines = pretty_string.split('\n')
        
        MAX_LENGTH = 80 # Define the maximum allowed length for each line
        truncated_lines = [] # Initialize a list to hold processed lines
        
        # Iterate over each line in the pretty-printed message
        for line in lines:
            # Check if the current line exceeds the maximum length
            if len(line) > MAX_LENGTH:
                # Truncate the line and append an ellipsis to indicate continuation
                truncated_line = line[:MAX_LENGTH] + '...'
                truncated_lines.append(truncated_line)
            else:
                # If the line is within the limit, append it as is
                truncated_lines.append(line)
        
        # Join the processed lines back into a single string separated by newline characters
        log_message = '\n'.join(truncated_lines)

    if tab > 0:
        log_message = f'{"    " * tab}{log_message}'
    if color and color != 'default':
        log_message = colorwrap(log_message, color)
    # Log the final message at the INFO level using the global logger
    logger.info(f'{log_message}{EscapeColor.RESET}') # Log the message as is and reset the color

    # Add a blank line after the message if pad_after is specified and greater than 0
    if pad_after:
        println(pad_after) # Print a blank line to add padding below the message
    
def println(amount:int=1) -> None:
    """
    Logs a blank line.
    
    Args:
        amount (int): The number of blank lines to log.
    """
    if amount < 1:
        err('The amount of blank lines to print must be greater than 0.')
    elif amount == None:
        err('The amount of blank lines to print must be specified and can\'t be "None".')
        
    for _ in range(amount):
        print()
        
def success(message:str='',
            include_symbol:bool=False,
            pad_after:int=None,
            pad_before:int=None,
            symbol_position:SymbolPosition='start') -> None:
    """
    Logs a success message.
    """
    success_message = _format(message,
                              include_symbol=include_symbol,
                              pad_before=pad_before,
                              symbol='✅', # \u2705
                              symbol_position=symbol_position,
                              use_prefix=False,
                              verbose=False)
    logger.info(f'{EscapeColor.GREEN}{success_message}{EscapeColor.RESET}') # Log the success message
    # Add a blank line after the message if pad_after is specified and greater than 0
    if pad_after:
        println(pad_after) # Print a blank line to add padding below the message
        
def treeprint(object:dict, limit:int=10) -> None:
    """
    Print the object as a tree structure with a limit on the number of entries.
    
    Requires this format:
    {
        'entry': {
            'subentry': {
                'subentry',
                'subentry'
            }
        },
        'entry': {
            'subentry': {
                'subentry',
                'subentry'
            }
        }
    }
    """
    return
    for key, entries in object.items():
        entries_list = list(entries.items())
        for idx, (name, info) in enumerate(entries_list):
            is_last_entry = idx == len(entries_list) - 1
            prefix = '    '
            connector = '└── ' if is_last_entry else '├──limit '
            print(f"{prefix}{connector}{name}: {human_readable(info['size'])}")

            # for children, extend prefix: no vertical bar if parent is last
            sub_prefix = prefix + ('    ' if is_last_entry else '│   ')
            children = list(info.get('children', {}).items())
            for cidx, (child, csize) in enumerate(children):
                is_last_child = cidx == len(children) - 1
                child_connector = '└── ' if is_last_child else '├── '
                print(f"{sub_prefix}{child_connector}{child}: {human_readable(csize)}")

def warn(message:str='',
         include_symbol:bool=False,
         pad_after:int=None,
         pad_before:int=None,
         symbol_position:SymbolPosition='start',
         use_prefix:bool=True) -> None:
    """
    Logs a warning message.

    Args:
        message (str): The warning message to be logged.
        pad_after (int , optional): Number of blank lines to add after the message. Defaults to None.
        pad_before (int , optional): Number of blank lines to add before the message. Defaults to None.
        verbose (bool, optional): If True, includes caller's filename and line number. Defaults to False.

    Returns:
        int: Returns 0 after logging the warning.
    """
    warn_message = _format(message,
                           include_symbol=include_symbol,
                           pad_before=pad_before,
                           prefix='WARN',
                           symbol='⚠️', # \u26A0
                           use_prefix=use_prefix,
                           verbose=False)
    logger.warning(warn_message) # Log the warning message
    
    # Add a blank line after the message if pad_after is specified and greater than 0
    if pad_after:
        println(pad_after) # Print a blank line to add padding below the message
        
def whisper(message:str='',
            pad_after:int=None,
            pad_before:int=None) -> None:
    """
    Logs a subtle (whisper) message.
    """
    whisper = _format(message,
                      pad_before=pad_before,
                      use_prefix=False,
                      verbose=False)
    logger.info(f'{EscapeColor.GRAY}\033[3m{whisper}{EscapeColor.RESET}')
    
    # Add a blank line after the message if pad_after is specified and greater than 0
    if pad_after:
        println(pad_after) # Print a blank line to add padding below the message

# Global logger instance
logger = logging.getLogger(GLOBAL_LOGGING_CONFIG.LOG_NAME)
logger.setLevel(logging.DEBUG) # Set the minimum logging level to DEBUG

if not GLOBAL_LOGGING_CONFIG.SURPRESS_CONSOLE:
    # Console handler for compact logging
    # console_formatter = logging.Formatter()
    # console_handler.setFormatter(console_formatter) # Apply compact format to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG) # Set console handler to capture DEBUG and above
    logger.addHandler(console_handler)# Apply the colored formatter to the console handler
    console_handler.setFormatter(_ColoredFormatter()) # Apply colored format to console

# TODO: Properly test and evaluate the implemented custom file logging functionality
# Create log directory
# log_directory = create_log_directory()

# File handler for detailed logging at INFO level
# info_file_handler = logging.handlers.TimedRotatingFileHandler(
#     os.path.join(log_directory, "info.log"), 
#     when="midnight", # Rotate log at midnight
#     interval=1, # Rotate every 1 day
# )
# info_file_handler.setLevel(logging.INFO) # Set to capture INFO and above

# File handler for detailed logging at WARNING level
# warning_file_handler = logging.handlers.TimedRotatingFileHandler(
#     os.path.join(log_directory, "warning.log"), 
#     when="midnight", 
#     interval=1, 
# )
# warning_file_handler.setLevel(logging.WARNING) # Set to capture WARNING and above

# File handler for detailed logging at ERROR level
# error_file_handler = logging.handlers.TimedRotatingFileHandler(
#     os.path.join(log_directory, "error.log"), 
#     when="midnight", 
#     interval=1, 
# )
# error_file_handler.setLevel(logging.ERROR) # Set to capture ERROR and above

# File formatter (detailed)
# file_formatter = logging.Formatter(
#     '%(asctime)s - %(levelname)s - %(message)s - [File: %(filename)s, Line: %(lineno)d]', 
#     datefmt='%Y-%m-%d %H:%M:%S'  # Define date format for logs
# )

# Apply detailed formatter to all file handlers
# info_file_handler.setFormatter(file_formatter)
# warning_file_handler.setFormatter(file_formatter)
# error_file_handler.setFormatter(file_formatter)

# Add all handlers to the global logger
# logger.addHandler(info_file_handler)
# logger.addHandler(warning_file_handler)
# logger.addHandler(error_file_handler)