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
import builtins
import configparser
import csv
import json
import os
import shutil

# As-system imports
import xml.etree.ElementTree as ET

# As-package imports
import numpy as np

# From system imports
from pathlib import PosixPath
from typing import Dict, List

# From local imports
from teatype.logging import err, warn

# From-as system imports
from builtins import list as list_type

# From-as local imports
from teatype.io import path as path_functions

# TODO: Implement with context handling
class _File:
    def __init__(self, path:str, content:any=None, trimmed:bool=False, nested_depth:int=None):
        """
        Initializes a File object with various attributes based on the given path.
        
        Parameters:
            path (str): The path to the file or directory.
            content (any, optional): The content of the file. Defaults to None.
            trimmed (bool, optional): Whether to skip retrieving additional file attributes. Defaults to False.
        """
        self.path = path # Store the path to the file or directory
        self.nested_depth = nested_depth # Store the nested depth of the file or directory in case of recursive listing

        self.exists = os.path.exists(path) # Check if the file or directory exists
        if self.exists:
            self.content = content # Store the content of the file (if provided)
                
            # Check if the path is a file and store the result
            self.is_file = os.path.isfile(path)
            if self.is_file:
                # Extract the file extension from the path
                self.extension = os.path.splitext(path)[1]
                
            # Get the base name of the path (the final component) and store it
            self.name = os.path.basename(path)
            
            if not trimmed:
                # Retrieve the last accessed time of the file or directory
                self.accessed_at = os.path.getatime(path)
                # Retrieve the creation time of the file or directory
                self.created_at = os.path.getctime(path)
                # Get the group ID of the owner of the file or directory
                self.group = os.stat(path).st_gid
                # Check if the path is a symbolic link and store the result
                self.is_symlink = os.path.islink(path)
                # Retrieve the last modified time of the file or directory
                self.modified_at = os.path.getmtime(path)
                # Get the user ID of the owner of the file or directory
                self.owner = os.stat(path).st_uid
                # Get the parent directory of the path and store it
                self.parent = os.path.dirname(path)
                # Get the permission bits of the file and store them
                self.permissions = os.stat(path).st_mode
                
                if self.is_file:
                    # Get the size of the file in bytes and store it
                    self.size = os.path.getsize(path)
                else:
                    # Get the size of the directory in bytes
                    self.size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(path) for filename in filenames)
                    
    def append(self, data:any, force_format:str=None) -> bool:
        """
        Proxy-method for the append function to append data to the file at the specified path.
        
        Parameters:
            data (any): The data to append to the file.
            force_format (str, optional): The format to force when appending data. Defaults to None.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return append(self.path, data, force_format)
    
    def copy(self, destination:str, create_parent_directories:bool=True, overwrite:bool=True) -> bool:
        """
        Proxy-method for the copy function to copy the file from the source path to the destination path.
        
        Parameters:
            destination (str): The path to the destination file.
            create_parent_directories (bool, optional): Whether to create parent directories if they do not exist. Defaults to True.
            overwrite (bool, optional): Whether to overwrite the destination file if it already exists. Defaults to True.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return copy(self.path, destination, create_parent_directories, overwrite)
    
    def delete(self) -> bool:
        """
        Proxy-method for the delete function to delete the file (or directory) at the specified path.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return delete(self.path)
    
    def move(self, destination:str, create_parent_directories:bool=True, overwrite:bool=True) -> bool:
        """
        Proxy-method for the move function to move the file from the source path to the destination path.
        
        Parameters:
            destination (str): The path to the destination file.
            create_parent_directories (bool, optional): Whether to create parent directories if they do not exist. Defaults to True.
            overwrite (bool, optional): Whether to overwrite the destination file if it already exists. Defaults to True.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return move(self.path, destination, create_parent_directories, overwrite)
    
    def read(self, force_format:str=None, return_file:bool=False, trim_file:bool=False) -> any:
        """
        Proxy-method for the read function to read data from the file at the specified path.
        
        Parameters:
            force_format (str, optional): The format to force when reading data. Defaults to None.
            return_file (bool, optional): Whether to return a _File object with additional attributes. Defaults to False.
            trim_file (bool, optional): Whether to skip retrieving additional file attributes. Defaults to False.
        
        Returns:
            any: The data read from the file, or None if an error occurred.
        """
        return read(self, force_format, return_file, trim_file)
    
    def write(self, data:any, force_format:str=None) -> bool:
        """
        Proxy-method for the write function to write data to the file at the specified path.
        
        Parameters:
            data (any): The data to write to the file.
            force_format (str, optional): The format to force when writing data. Defaults to None.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return write(self.path, data, force_format)
                    
    def __str__(self):
        """
        Returns a string representation of the File object.
        
        Returns:
            str: A string representation of the File object.
        """
        return f'File(path="{self.path}", is_file={self.is_file}, name="{self.name}")'

def append(path:str, data:any, force_format:str=None) -> bool:
    """
    Append data to a file at the specified path.

    Depending on the file extension, the data is appended in the appropriate format:
    - .json: JSON format
    - .ini: INI configuration
    - .csv: CSV format
    - others: plain text

    Parameters:
        path (str): The path to the file.
        data (any): The data to append to the file.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Open the file in append mode
        with open(path, 'a') as f:
            if force_format == 'lines':
                # Append multiple lines to the file
                f.writelines(data)
            if path.endswith('.json') or force_format == 'json':
                # Append JSON data to the file
                json.dump(data, f)
            elif path.endswith('.ini') or force_format == 'ini':
                # Initialize ConfigParser and read existing INI configuration
                config = configparser.ConfigParser()
                config.read(path)
                # Update the configuration with new data
                config.update(data)
                # Write the updated configuration back to the file
                config.write(f)
            elif path.endswith('.csv') or force_format == 'csv':
                # Create a CSV writer object
                writer = csv.writer(f)
                # Write a new row to the CSV file
                writer.writerow(data)
            else:
                # Append plain text data to the file
                f.write(data)
        return True
    except Exception as e:
        # Log an error message if an exception occurs
        err(f'Error appending to file {path}: {e}')
        return False
    
def copy(source:str,
         destination:str,
         create_parent_directories:bool=True,
         overwrite:bool=True) -> bool:
    """
    Copy a file from the source path to the destination path.

    Parameters:
        source (str): The path to the source file.
        destination (str): The path to the destination file.
        create_parent_directories (bool): Whether to create parent directories if they do not exist.
        overwrite (bool): Whether to overwrite the destination file if it already exists.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        if not exists(source):
            # Log an error message if the source file does not exist
            err(f'File "{source}" does not exist.')
            return False
        
        if exists(destination):
            if not overwrite:
                # Log an error message if the destination file already exists
                err(f'File "{destination}" already exists. Call with "overwrite=True" to replace it.')
                return False
            
        shutil.copy(source, destination)
        return True
    except Exception as exc:
        # Log an error message if an exception occurs
        err(f'Error copying file from {source} to {destination}: {exc}')
        return False

def delete(path:str, silent_fail:bool=True) -> bool:
    """
    Delete a file (or directory) at the specified path.

    Parameters:
        path (str): The path to the file.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Check if the path exists and determine if it's a file
        file_exists, is_file = exists(path)
        if file_exists:
            if is_file:
                # If it's a file, log a warning indicating that a directory will be deleted
                err(f'"{path}" is a directory. Deleting the directory and its contents.')
                # Recursively remove the directory and all its contents
                shutil.rmtree(path)
            else:
                # If it's not a file (i.e., it's a regular file), remove it
                os.remove(path)
        return True
    except Exception as exc:
        if not silent_fail:
            # Log an error message if an exception occurs
            err(f'Error deleting file "{path}": {exc}')
        return False
    
def exists(path:PosixPath|str, return_file:bool=False, trim_file:bool=False) -> bool|_File:
    """
    Check if a file exists at the specified path.

    Parameters:
        path (str): The path to the file.
        return_file (bool): Whether to return a _File object with additional attributes.
        trim_file (bool): Whether to skip retrieving additional file attributes.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if trim_file and not return_file:
        # Warn the user that trimming is ignored because a _File object is not being returned
        warn('Cannot trim file without returning a _File object. Ignoring "trim_file" parameter.')
    
    # Check if the provided path is a PosixPath object
    if isinstance(path, PosixPath):
        # Convert PosixPath to string for compatibility with os.path functions
        path_string = str(path)
    else:
        # Use the path as-is if it's already a string
        path_string = path
    
    file_exists = os.path.exists(path_string)
    if return_file:
        # Return a _File object with the specified path and trimming option if requested
        return _File(path_string, trimmed=trim_file) if file_exists else None
    # Otherwise, return a boolean indicating whether the path exists
    return file_exists
    
def list(directory:str,
         walk:bool=False,
         depth:int=None,
         ignore_folders:List[str]=None,
         only_include:List[str]=None, # TODO: Seperate include_extensions and include_regex
         trim_files:bool=True,
         stringify:bool=False) -> List[_File]:
    """
    Walk through a directory and return a list of files and subdirectories.

    Parameters:
        directory (str): The path to the directory to walk through.
        walk (bool): Whether to walk through subdirectories recursively.
        depth (int): The maximum depth to walk through subdirectories.
        ignore_folders (list): A list of folder names to ignore.
        only_include (list): A list of file extensions to include.
        trim_files (bool): Whether to skip retrieving additional file attributes.

    Returns:
        list: A list of files and subdirectories in the directory.
    """
    try:
        # Check if a depth greater than 1 is specified without enabling recursive walking
        if depth is not None and walk == False:
            warn('Cannot specify depth without walking through subdirectories. Ignoring depth parameter.')
        
        # Initialize an empty list to store the results of files and directories
        results = []
        
        # Define an inner function to handle recursive directory walking
        def walk_directory(dir_path, current_depth):
            # Terminate recursion if the current depth exceeds the specified maximum depth
            if current_depth > depth:
                return
            # Iterate over each entry in the current directory
            for entry in os.scandir(dir_path):
                if entry.is_dir():
                    if ignore_folders:
                        # Skip folders that are in the ignore list
                        if entry.name in ignore_folders:
                            continue
                    # Append directory details to the results list
                    results.append(_File(entry.path, trimmed=trim_files, nested_depth=current_depth))
                    # Recursively walk through the subdirectory, increasing the depth
                    walk_directory(entry.path, current_depth + 1)
                else:
                    if only_include:
                        # Skip files that do not have the specified extensions
                        if not entry.name.endswith(tuple(only_include)):
                            continue
                    # Append directory details to the results list
                    results.append(_File(entry.path, trimmed=trim_files, nested_depth=current_depth))
                    
        if not walk:
            depth = 1
        walk_directory(directory, 1)
        
        if stringify:
            results = [str(result) for result in results]
        # Return the compiled list of files and directories with their details
        return results
    except Exception as exc:
        # Log an error message if an exception occurs during directory walking
        err(f'Error walking through directory "{directory}": {exc}')
        # Re-raise the exception to allow further handling upstream
        raise exc

def move(source:str, destination:str, create_parents:bool=True, overwrite:bool=True) -> bool:
    """
    Move a file from the source path to the destination path.

    Parameters:
        source (str): The path to the source file.
        destination (str): The path to the destination file.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        if not exists(source):
            # Log an error message if the source file does not exist
            err(f'File "{source}" does not exist.')
            return False
        
        if exists(destination):
            if overwrite:
                pass
            else:
                # Log an error message if the destination file already exists
                err(f'File "{destination}" already exists. Call with "overwrite=True" to replace it.')
                return False
            
        if create_parents:
            # Create parent directories if they do not exist
            parent_path = ''.join(subpath + '/' for subpath in destination.split('/')[:-1])
            path_functions.create(parent_path)
            
        shutil.move(source, destination)
        return True
    except Exception as exc:
        # Log an error message if an exception occurs
        err(f'Error moving file from {source} to {destination}: {exc}')
        return False

def read(file:_File|PosixPath|str,
         force_format:str=None,
         return_file:bool=False,
         trim_file:bool=False,
         silent_fail:bool=False) -> any:
    """
    Read data from a file at the specified path.

    Depending on the file extension, the data is read in the appropriate format:
    - .json: JSON data
    - .ini: INI configuration
    - .csv: CSV data
    - .env: Environment variables
    - others: plain text

    Parameters:
        path (str): The path to the file.

    Returns:
        any: The data read from the file, or None if an error occurred.
    """
    try:
        if isinstance(file, _File):
            path_string = file.path
            file_extension = file.extension
        if isinstance(file, PosixPath):
            path_string = str(file)
            file_extension = os.path.splitext(path_string)[1]
        else:
            path_string = file
            file_extension = '.' + path_string.split('.')[-1]
            
        # TODO: Make dynamic with plug'n'play function array and allow passing of custom functions
        # handlers = {
        #     'json': read_json,
        # }
        file_class =_File(path_string, trimmed=trim_file)
        if file_class.exists:
            if file_class.is_file:
                content = None
                with open(path_string, 'r') as f:
                    if force_format == 'lines':
                        # Read and return the lines of the file
                        content = f.readlines()
                    elif file_extension == '.xml' or force_format == 'xml':
                        # Parse and return XML data from the file
                        raw_xml_tree = ET.parse(path_string)
                        raw_xml_root = raw_xml_tree.getroot()
                        
                        def xmlToDict(element):
                            result = {}
                            text = element.text.strip() if element.text and element.text.strip() else None
                            if text:
                                result['value'] = text
                            if element.attrib:
                                attrs = {}
                                result['tag'] = element.tag
                                for key, value in element.attrib.items():
                                    if key == 'value_type':
                                        value = value.strip()
                                        try:
                                            if value == 'boolean':
                                                result['value'] = result.get('value', '').lower() in ('true', '1')
                                            elif value == 'float':
                                                result['value'] = float(result.get('value', 0))
                                            elif value == 'int':
                                                result['value'] = int(result.get('value', 0))
                                        except ValueError as ve:
                                            print(f"Conversion error for key '{key}': {ve}")
                                    attrs[key] = value
                                result['attributes'] = attrs
                            children = builtins.list(element)
                            if children:
                                child_dict = {}
                                for child in children:
                                    child_converted = xmlToDict(child)
                                    if child.tag in child_dict:
                                        if isinstance(child_dict[child.tag], builtins.list):
                                            child_dict[child.tag].append(child_converted)
                                        else:
                                            child_dict[child.tag] = [child_dict[child.tag], child_converted]
                                    else:
                                        child_dict[child.tag] = child_converted
                                result['children'] = child_dict
                            return result
                        content = xmlToDict(raw_xml_root)['children']
                    elif file_extension == '.ini' or file_extension == '.cfg' or force_format == 'ini' or force_format == 'cfg':
                        # Initialize ConfigParser and read INI configuration
                        config = configparser.ConfigParser()
                        config.read(path_string)
                        content = config
                    elif file_extension == '.jsonc' or force_format == 'jsonc':
                        dirty_content = f.read()
                        # Remove comments denoted by '//' to ensure valid JSON
                        clean_content = ''.join(line for line in dirty_content.splitlines() if not line.strip().startswith('//'))
                        content = json.loads(clean_content)
                    elif file_extension == '.json' or force_format == 'json':
                        # Load and return JSON data from the file
                        content = json.load(f)
                    elif file_extension == '.csv' or force_format == 'csv':
                        # Read and return CSV data as a list of rows
                        content = list(csv.reader(f))
                    elif file_extension == '.env' or force_format == 'env':
                        # Parse and return environment variables from the file
                        env_vars = {}
                        for line in f:
                            line = line.strip()
                            # Check if the line is not empty and does not start with a comment
                            if line and not line.startswith('#'):
                                # Split the line into key and value using the first '=' as delimiter
                                key, _, value = line.partition('=')
                                # Strip whitespace and set the environment variable
                                env_vars[key.strip()] = value.strip()
                        content = env_vars
                    else:
                        # Read and return plain text data from the file
                        content = f.read()
                
                if content is None:
                    # Log an error if the file is empty
                    warn(f'File "{path_string}" seems to be empty. Returning "None".')
                    return None
                
                if return_file:
                    # Return a _File object with the content if requested
                    file_class.content = content
                    return f
                return content
            else:
                file_is_folder_message = f'"{path_string}" is a directory, not a file.'
                if not silent_fail:
                    err(file_is_folder_message)
                raise IsADirectoryError(file_is_folder_message)
        else:
            file_not_found_message = f'File "{path_string}" does not exist.'
            if not silent_fail:
                # Log an error message if the file does not exist
                err(file_not_found_message)
            raise FileNotFoundError(file_not_found_message)
    except Exception as exc:
        if not silent_fail:
            # Log an error message if an exception occurs
            err(f'Error reading file "{path_string}": {exc}')
        raise exc

def write(path:str, data:any, force_format:str=None, prettify:bool=False, create_parents:bool=True) -> bool:
    """
    Write data to a file at the specified path.

    Depending on the file extension, the data is written in the appropriate format:
    - .json: JSON format
    - .ini: INI configuration
    - .csv: CSV format
    - others: plain text

    Parameters:
        path (str): The path to the file.
        data (any): The data to write to the file.
        force_format (str, optional): The format to force when writing data. Defaults to None.
        prettify (bool, optional): Whether to prettify the output. Defaults to False.
        create_parents (bool, optional): Whether to create parent directories if they do not exist. Defaults to True.
        
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    # TODO: Make dynamic with plug'n'play function array and allow passing of custom functions
    try:
        if create_parents:
            # Create parent directories if they do not exist
            parent_path = ''.join(subpath + '/' for subpath in path.split('/')[:-1])
            path_functions.create(parent_path)
            
        # JSON_DUMP_ENCODERS = {
        #     np.ndarray: lambda x: x.tolist(),
        # }
    
        class _JSON_DUMP_ENCODERS(json.JSONEncoder):
            """
            Custom JSON encoder for NumPy data types.
            
            This encoder is used to convert NumPy data types to standard Python data types
            when serializing to JSON format.
            """
            def default(self, value):
                if isinstance(value, dict):
                    # Recursively convert NumPy arrays in dictionaries to lists
                    return {key: self.default(val) for key, val in value.items()}
                elif isinstance(value, list_type):
                    # Recursively convert NumPy arrays in lists to lists
                    return [self.default(item) for item in value]
                elif isinstance(value, np.ndarray):
                    return value.tolist()
                return super().default(value)
        
        # Open the file in write mode
        with open(path, 'w') as f:
            if force_format == 'lines':
                # Write multiple lines to the file
                f.writelines(data)
            elif path.endswith('.json') or force_format == 'json':
                indent = None
                if prettify:
                    indent = 4
                # Write JSON data to the file
                json.dump(data, f, indent=indent, default=_JSON_DUMP_ENCODERS().default)
            elif path.endswith('.ini') or force_format == 'ini':
                # Initialize ConfigParser and update with new data
                config = configparser.ConfigParser()
                config.update(data)
                # Write the updated configuration to the file
                config.write(f)
            elif path.endswith('.csv') or force_format == 'csv':
                # Create a CSV writer object
                writer = csv.writer(f)
                # Write multiple rows to the CSV file
                writer.writerows(data)
            elif force_format == 'bytes':
                f.write(data.decode('utf-8'))
            else:
                # Write plain text data to the file
                f.write(data)
        return True
    except Exception as exc:
        # Log an error message if an exception occurs
        err(f'Error writing to file {path}: {exc}', traceback=True)
        raise exc