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

# From system imports
from pathlib import Path

def join(*args, stringify:bool=True) -> str:
    """
    Join multiple path components intelligently.

    Args:
        *args (str): The path components to join.
        stringify (bool): If True, returns the joined path as a string.
                           If False, returns as a Path object. Defaults to True.

    Returns:
        str: The joined path as a string if stringify is True.
    """
    joined_path = Path(*args) # Join the path components
    return str(joined_path) if stringify else joined_path # Return the joined path as string or Path object

def parent(reverse_depth:int=1, stringify:bool=True) -> str:
    """
    Retrieve the parent directory of the script's path.

    Args:
        reverse_depth (int): The number of levels to traverse up the directory tree.
                             Defaults to 1.
        stringify (bool): If True, returns the parent path as a string.
                           If False, returns as a Path object. Defaults to True.

    Returns:
        str: The parent directory path as a string if stringify is True.
        Path: The parent directory as a Path object if stringify is False.
    """
    script_path = script(stringify=False) # Get the script path as a Path object
    parent = script_path.parent # Get the immediate parent directory
    for _ in range(reverse_depth - 1):
        parent = parent.parent # Traverse up the directory tree
    return str(parent) if stringify else parent # Return the parent path as string or Path object

def script(stringify: bool = True) -> str:
    """
    Retrieve the path of the calling script.

    This function inspects the call stack to determine the file path of the script
    that invoked this function. It allows retrieval of the path either as a string
    or as a Path object based on the `stringify` parameter.

    Args:
        stringify (bool): Determines the return type of the script path.
                          - If True, returns the path as a string.
                          - If False, returns the path as a Path object.
                          Defaults to True.

    Returns:
        str: The caller's script path as a string if `stringify` is True.
        Path: The caller's script path as a Path object if `stringify` is False.
    """
    stack = inspect.stack() # Get the current call stack
    for frame in stack:
        # Iterate through each frame in the call stack
        if frame.filename != __file__:
            # Identify the first frame that is not this file, i.e., the caller
            caller_frame = frame
            break
    caller_path = Path(caller_frame.filename).resolve() # Resolve the absolute path of the caller's script
    return str(caller_path) if stringify else caller_path # Return the path as string or Path object based on `stringify`

def workdir(stringify: bool = True) -> str:
    """
    Retrieve the current working directory.

    Args:
        stringify (bool): If True, returns the working directory as a string.
                           If False, returns as a Path object. Defaults to True.

    Returns:
        str: The current working directory as a string if stringify is True.
        Path: The current working directory as a Path object if stringify is False.
    """
    cwd_path = Path.cwd() # Get the current working directory as a Path object
    return str(cwd_path) if stringify else cwd_path # Return as string or Path object