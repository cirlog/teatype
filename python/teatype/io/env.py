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
import os
import re

# From local imports
from teatype.logging import err
from teatype.io import file

def get(key:str=None, default:str=None) -> str | dict:
    """
    Retrieve environment variables.

    This function fetches the value of a specific environment variable if a key is provided.
    If no key is provided, it returns all environment variables as a dictionary.

    Args:
        key (str, optional): The name of the environment variable to retrieve. Defaults to None.
        default (str, optional): The default value to return if the specified environment variable is not found. Defaults to None.

    Returns:
        str | dict: The value of the specified environment variable, or all environment variables if no key is provided.
    """
    # If 'key' is provided, attempt to get its value from the environment variables.
    # If 'key' is not found, return 'default'.
    # If 'key' is not provided, return the entire environment variables dictionary.
    return os.environ.get(key, default) if (key or default) else os.environ

def load(env_path:str=None) -> bool:
    """
    Load environment variables from a .env file into the environment.

    This function checks for the existence of a .env file in the current directory.
    If the file exists, it reads each line, ignoring empty lines and comments,
    and sets the corresponding environment variables.
    """
    try:
        # Load environment variables from .env file if it exists
        env_vars = file.read(env_path if env_path else '.env', force_format='env')
        os.environ.update(env_vars)
        return True
    except FileNotFoundError:
        # Log an error message if the .env file is not found
        err('No .env file found in the current directory.')
        return False
    except Exception as e:
        # Log an error message if an exception occurs
        err(f'An error occurred while loading the .env file: {e}')
        return False
    
def set(key:str, value:str) -> None:
    """
    Set an environment variable.

    This function sets the value of an environment variable.

    Args:
        key (str): The name of the environment variable.
        value (str): The value to assign to the environment variable.
    """
    os.environ[key] = value
    
def substitute(cmd:str, env_variables:dict=get()) -> str:
    """
    Substitute environment variables in the command string with their actual values.
    The format for placeholders in the command string is '{{ENV_VAR}}'.

    Args:
        cmd (str): The command string containing placeholders for environment variables.
        env_variables (dict, optional): A dictionary of environment variables. Defaults to all environment variables.

    Returns:
        str: The command string with environment variables substituted.
    """
    pattern = r'\{\{(\w+)\}\}' # Regex pattern to match placeholders
    placeholder_var = re.search(pattern, cmd) # Search for placeholders in the command
    if not placeholder_var:
        return cmd
        
    # If a placeholder is found, isolate the placeholder variable name
    isolated_replacement_var = placeholder_var.group(1) # Isolate the placeholder variable name
    if isolated_replacement_var in env_variables:
        # Replace the placeholder with the actual value of the environment variable
        cmd = cmd.replace('{{' + isolated_replacement_var + '}}', env_variables[isolated_replacement_var])
    else:
        raise Exception(f'Environment variable {isolated_replacement_var} parsed not found.')

    # DEPRECATED: Solution not needed anymore and also kinda dumb
        # # Sort keys by length in descending order to handle nested variables correctly
        # for key in sorted(env_variables.keys(), key=len, reverse=True):
        #     placeholder = '{{' + key + '}}'
        #     cmd = cmd.replace(placeholder, env_variables[key])
    return cmd