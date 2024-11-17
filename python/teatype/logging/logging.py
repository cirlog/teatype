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
import logging
import logging.handlers
import os
import sys

# As system imports
import traceback as traceback_exc

# From system imports
from datetime import datetime
from pprint import pformat

# Define a global base log directory
BASE_LOG_DIR = os.path.join(os.path.expanduser("~"), "ApplicationLogs") # User home directory

def create_log_directory() -> str:
    """
    Create a log directory based on the current date.

    This function generates a directory path by joining the base log directory
    with the current date in YYYY-MM-DD format. It ensures that the directory
    exists by creating it if necessary.

    Returns:
        str: The path to the created or existing log directory.
    """
    log_dir = os.path.join(BASE_LOG_DIR, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(log_dir, exist_ok=True) # Create directory if it doesn't exist
    return log_dir

# Global logger instance
logger = logging.getLogger("global_custom_logger")
logger.setLevel(logging.DEBUG) # Set the minimum logging level to DEBUG

# Create log directory
# log_directory = create_log_directory()

# Console handler for compact logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG) # Set console handler to capture DEBUG and above

# TODO: Properly test and evaluate the implemented custom file logging functionality
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

# Console formatter (compact)
# console_formatter = logging.Formatter()
# console_handler.setFormatter(console_formatter) # Apply compact format to console

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
logger.addHandler(console_handler)
# logger.addHandler(info_file_handler)
# logger.addHandler(warning_file_handler)
# logger.addHandler(error_file_handler)
# Custom colored formatter

class ColoredFormatter(logging.Formatter):
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
    COLOR_CODES = {
        logging.DEBUG: '\033[94m', # Blue
        logging.WARNING: '\033[93m', # Yellow
        logging.ERROR: '\033[91m', # Red
        logging.CRITICAL: '\033[95m', # Magenta
    }
    RESET_CODE = '\033[0m'

    def format(self, record):
        color = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        message = record.getMessage()
        return f'{color}{message}{self.RESET_CODE}'
    
# Apply the colored formatter to the console handler
console_handler.setFormatter(ColoredFormatter())

def _format(message:any,
            pad_top:int|None=None,
            verbose:bool=False) -> any:
    """
    Formats a message with optional padding and verbosity.
    Only has an effect on terminal logging, not file logging.

    Args:
        message (any, optional): The message to format. Defaults to ''.
        pad_top (int | None, optional): Number of blank lines to add before the message. Defaults to None.
        pad_bottom (int | None, optional): Number of blank lines to add after the message. Defaults to None.
        verbose (bool, optional): If True, includes caller's filename and line number. Defaults to False.

    Returns:
        any: The formatted message string.
    """
    formatted_message = message  # Initialize the formatted message as an empty string
    
    # Add a blank line before the message if pad_top is specified and greater than 0
    if pad_top and pad_top > 0:
        for _ in range(pad_top):
            print() # Print a blank line to add padding above the message
            
    # If verbose is True, include caller's filename and line number in the message
    if verbose:
        frame = inspect.currentframe().f_back # Get the caller's frame
        filename = os.path.basename(frame.f_code.co_filename) # Extract the filename from the caller's frame
        # TODO: Shows the wrong line number, shows line number of logging.py, not class calling it
        lineno = frame.f_lineno # Extract the line number from the caller's frame
        # TODO: Add handling for different types of messages
        formatted_message = f'{message} - [{filename}, PRINTLN: {lineno}]' # Format the message with caller info
    
    return formatted_message

def err(message:str,
        exit=False,
        pad_bottom:int|None=None,
        pad_top:int|None=None,
        traceback:bool=False,
        verbose:bool=True) -> None:
    """
    Logs an error message and optionally includes the traceback of the current exception.

    Args:
        message (str): The error message to be logged.
        pad_top (int | None, optional): Number of blank lines to add before the message. Defaults to None.
        pad_bottom (int | None, optional): Number of blank lines to add after the message. Defaults to None.
        traceback (bool, optional): Flag to determine whether to include the traceback.
            Defaults to False.
        verbose (bool, optional): If True, includes caller's filename and line number. Defaults to False.

    Returns:
        int: Returns 1 to indicate an error has occurred.
    """
    # Retrieve the current exception information from the system
    exc_info = sys.exc_info()
    
    error_message = _format(f'ERROR - {message}', pad_top, verbose)
    # Log the error message as a critical error, potentially including the traceback
    if exit:
        error_message = f'FATAL EXIT {error_message}'
        
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
        
    if pad_bottom and pad_bottom > 0:
        for _ in range(pad_bottom):
            print() # Print a blank line to add padding below the message
        
    if exit:
        # If the exit flag is set, exit the program with an error code
        sys.exit(1)
    
def hint(message:str,
         pad_bottom: int | None = None,
         pad_top: int | None = None,
         verbose: bool = False) -> int:
    """
    Provide a hint message with optional padding and verbosity.
    
    Args:
        message (str): The message to display as a hint.
        pad_bottom (int, optional): Number of blank lines to add below the message. Defaults to None.
        pad_top (int, optional): Number of blank lines to add above the message. Defaults to None.
        verbose (bool, optional): If True, include additional verbosity in the message. Defaults to False.
    Returns:
        int: Status code indicating the outcome of the operation.
    """
    hint_message = _format(message, pad_top, verbose) # Format the message with optional padding and verbosity
    
    # Log the final message at the INFO level using the global logger
    logger.debug(f'HINT - {hint_message}') # Log the message as is
        
    # Add a blank line after the message if pad_bottom is specified and greater than 0
    if pad_bottom and pad_bottom > 0:
        for _ in range(pad_bottom):
            print() # Print a blank line to add padding below the message
    
def log(message:any,
        pad_bottom:int|None=None,
        pad_top:int|None=None,
        prettify:bool=False,
        verbose:bool=False) -> None:
    """
    Logs a message with optional formatting, padding, and prettification.
    
    This function formats the provided message, optionally adds padding above and below
    the message, prettifies complex objects for better readability, and logs the message
    at the INFO level using the global logger. It returns a status code indicating
    successful logging.
    
    Args:
        message (any, optional): The message to be logged. Defaults to ''.
        pad_bottom (int | None, optional): Number of blank lines to add after the message. Defaults to None.
        pad_top (int | None, optional): Number of blank lines to add before the message. Defaults to None.
        prettify (bool, optional): If True, formats complex objects into a pretty-printed string. Defaults to False.
        verbose (bool, optional): If True, includes caller's filename and line number in the log message. Defaults to False.
    """
    # Format the message with optional padding and verbosity
    log_message = _format(message, pad_top, verbose)
    
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
    
    # Log the final message at the INFO level using the global logger
    logger.info(log_message)  # Log the message as is
        
    # Add a blank line after the message if pad_bottom is specified and greater than 0
    if pad_bottom and pad_bottom > 0:
        for _ in range(pad_bottom):
            print() # Print a blank line to add padding below the message
    
def nl(amount:int=1) -> None:
    """
    Logs a blank line.
    
    Args:
        amount (int): The number of blank lines to log.
    """
    for _ in range(amount):
        print()

def warn(message:str='',
         pad_bottom:int|None=None,
         pad_top:int|None=None,
         verbose:bool=False) -> None:
    """
    Logs a warning message.

    Args:
        message (str): The warning message to be logged.
        pad_bottom (int | None, optional): Number of blank lines to add after the message. Defaults to None.
        pad_top (int | None, optional): Number of blank lines to add before the message. Defaults to None.
        verbose (bool, optional): If True, includes caller's filename and line number. Defaults to False.

    Returns:
        int: Returns 0 after logging the warning.
    """
    warn_message = _format(message, pad_top, verbose)
    logger.warning(f'WARNING - {warn_message}') # Log the warning message
    # Add a blank line after the message if pad_bottom is specified and greater than 0
    if pad_bottom and pad_bottom > 0:
        for _ in range(pad_bottom):
            print() # Print a blank line to add padding below the message