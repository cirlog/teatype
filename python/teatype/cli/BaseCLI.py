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
import sys

# From system imports
from abc import ABC, abstractmethod
from typing import List

# From package imports
from pathlib import Path
from teatype.cli import Argument, Command, Flag
from teatype.data.dict import update_dict
from teatype.logging import err

# TODO: Replace with package constant
TAB='    '

# TODO: Document all return types
# TODO: Make the class functionality less obscure, more options, maybe return to constructors?
class BaseCLI(ABC):
    """
    Base class for command-line interfaces.

    Attributes:
        name (str): The name of the CLI.
        shorthand (str): The shorthand notation for the CLI.
        help (str): A brief description of the CLI.
        arguments (list): A list of Argument instances representing the CLI arguments.
        commands (list): A list of Command instances representing the CLI commands.
        flags (list): A list of Flag instances representing the CLI flags.
        parsed_arguments (list): A list of parsed positional arguments.
        parsed_command (str): The parsed command name.
        parsed_flags (dict): A dictionary of parsed flags.
        parsing_errors (list): A list of parsing errors encountered during validation.
    """
    def __init__(self,
                 auto_init: bool = True,
                 auto_parse: bool = True,
                 auto_validate: bool = True,
                 auto_execute: bool = True,
                 auto_activate_venv: bool = True,
                 env_path: str = '.../.env',
                 proxy_mode: bool = False):
        """
        Initializes the BaseCLI instance with configuration options.

        Args:
            auto_init (bool, optional): If set to True, the CLI will automatically initialize upon instantiation.
                                         Defaults to True.
            auto_parse (bool, optional): If set to True, the CLI will automatically parse command-line arguments upon initialization.
                                          Defaults to True.
            auto_validate (bool, optional): If set to True, the CLI will automatically validate parsed arguments after parsing.
                                             Defaults to True.
            auto_execute (bool, optional): If set to True, the CLI will automatically execute the main functionality after validation.
                                            Defaults to True.
            auto_activate_venv (bool, optional): If set to True, the CLI will automatically activate the virtual environment specified by `env_path`.
                                                 Defaults to True.
            env_path (str, optional): The file path to the `.env` file from which environment variables will be loaded.
                                       Defaults to '.../.env'.
            proxy_mode (bool, optional): If set to True, the CLI will operate in proxy mode, altering its behavior to function as a proxy.
                                          Defaults to False.
        """
        # Load the environment variables from the specified .env file
        env_file = Path(env_path) # Create a Path object for the environment file path
        if env_file.exists(): # Check if the .env file exists at the given path
            with env_file.open() as f: # Open the .env file for reading
                for line in f: # Iterate over each line in the .env file
                    # Strip whitespace and ignore empty lines or lines starting with '#'
                    if line.strip() and not line.startswith('#'):
                        # Split the line into key and value at the first '=' character
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value # Set the environment variable in the OS environment
        
        if auto_init:
            self.init()
        
        if auto_parse:
            # Parse the command-line arguments and flags
            self.parse_args()

            if auto_validate:
                self.validate_args()
        
        if auto_execute:
            # Hook for pre-execution logic
            if hasattr(self, 'pre_execute') and callable(getattr(self, 'pre_execute')):
                self.pre_execute()
            
            self.execute()
            
    def init(self):
        """
        Initializes the CLI with meta information.

        This method sets up the CLI by initializing its name, shorthand, help description,
        arguments, commands, and flags based on the provided meta information. It also
        performs pre-initialization logic if defined in the child class.

        Args:
            meta (dict, optional): A dictionary containing meta information for the CLI.
                                   If not provided, the meta method will be called to obtain it.
        """
        # Hook for pre-initialization logic
        if hasattr(self, 'pre_init') and callable(getattr(self, 'pre_init')):
            self.pre_init()
            
        meta = self.meta()
        
        # Hook for modifying meta information
        if hasattr(self, 'modified_meta') and callable(getattr(self, 'modified_meta')):
            modfied_meta = self.modified_meta()
            meta = update_dict(meta, modfied_meta)

        # Initialize the name of the CLI
        self.name = meta['name'] if 'name' in meta else None
        # Initialize the shorthand notation for the CLI
        self.shorthand = meta['shorthand'] if 'shorthand' in meta else None
        # Initialize the brief description of the CLI
        self.help = meta['help'] if 'help' in meta else None
        
        arguments = meta['arguments'] if 'arguments' in meta else []
        commands = meta['commands'] if 'commands' in meta else []
        value_error = None
        if len(commands) > 0:
            if len(arguments) > 0:
                value_error = True
        elif len(arguments) > 0:
            if len(commands) > 0:
                value_error = True
        if value_error:
            raise ValueError('You cannot have pre-defined arguments and commands at the same time.')
        
        # Initialize the list of Argument instances representing the CLI arguments
        self.arguments = []
        for index, argument in enumerate(arguments):
            self.arguments.append(Argument(**argument, position=index))
        
        # Initialize the list of Command instances representing the CLI arguments
        self.commands = []
        for command in commands:
            self.commands.append(Command(**command))
        
        # Initialize the list of Flag instances representing the CLI flags
        flags = meta['flags'] if 'flags' in meta else []
        self.flags = []
        for flag in flags:
            self.flags.append(Flag(**flag))

    # TODO: Make positioning of arguments optional
    # TODO: Make flag assignment work with "="
    def parse_args(self):
        """
        Custom argument parsing logic to be independent from argparser for custom formatting reasons.
        
        This function parses command-line arguments passed to the script.
        It distinguishes between the command name, positional arguments, and flags.
        
        Returns:
            tuple: A tuple containing the command name (str), a list of positional arguments (list),
                   and a dictionary of flags (dict).
        """
        # Hook for pre-parsing logic
        if hasattr(self, 'pre_parse') and callable(getattr(self, 'pre_parse')):
            self.pre_parse()
        
        # If there are fewer than 2 arguments, return None for command_name and empty lists/dicts for args and kwargs
        if len(sys.argv) < 1:
            return {}
        
        # Initialize empty lists for positional arguments and a dictionary for flags
        arguments = []
        command = None
        flags = {}
        
        # Iterate over the remaining command-line arguments
        # Initialize the index to start from the first argument after the script name
        i = 1
        
        # Loop through the command-line arguments starting from the second element
        while i < len(sys.argv):
            arg = sys.argv[i]
            
            # Check if the argument is a flag (starts with '-')
            if arg.startswith("-"):
                # Check if the next argument exists and is not another flag
                if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("-"):
                    # If the next argument is a value, add it to flags with the current flag as the key
                    flags[arg] = sys.argv[i + 1]
                    # Skip the next argument since it's already processed as a value
                    i += 1
                else:
                    # If the next argument is another flag or doesn't exist, set the current flag to True
                    flags[arg] = True
            else:
                if len(self.commands) > 0:
                    if command is None:
                        for search_command in self.commands:
                            if arg == search_command.name or arg == search_command.shorthand:
                                command = arg
                                continue
                # If the argument is not a flag, add it to the positional arguments list
                arguments.append(arg)
            
            # Move to the next argument
            i += 1
            
        # Assign the parsed command name, positional arguments, and flags
        self.parsed_arguments = arguments
        self.parsed_command = command
        self.parsed_flags = flags
    
    # TODO: Reduce repetition and amount of loops, more efficient algorithm
    def validate_args(self):
        """
        Pre-execution checks for required arguments and flags.

        This method ensures that all required arguments and flags have been provided
        before the main execution of the CLI. If any required argument or flag is missing,
        it prints an error message and returns False, indicating that the execution should not proceed.

        Returns:
            bool: True if all required arguments and flags are provided, False otherwise.
        """
        
        # Initialize an empty list to store any parsing errors encountered
        parsing_errors = []

        # Check if the help flag ('-h' or '--help') is present in the parsed flags
        help_flag_detected = '-h' in self.parsed_flags or '--help' in self.parsed_flags
        # Check if the help flag ('-h' or '--help') is present in the parsed flags
        if help_flag_detected:
            # If the help flag is detected, print the CLI usage information
            self.print()
            sys.exit(0)
        else:
            # TODO: Check too many commands and wrong commands
            if len(self.commands) > 0:
                if self.parsed_command:
                    for command in self.commands:
                        if self.parsed_command == command.name or self.parsed_command == command.shorthand:
                            command.value = self.parsed_command
                else:
                    parsing_errors.append('No command provided.')
            else:
                # Determine the number of parsed arguments and the total number of expected arguments
                amount_of_parsed_arguments = len(self.parsed_arguments)
                amount_of_all_arguments = len(self.arguments)
                # Check if the number of parsed arguments exceeds the number of expected arguments
                if amount_of_parsed_arguments > amount_of_all_arguments:
                    parsing_errors.append(
                        f'Number of possible arguments provided ({amount_of_parsed_arguments}) is greater than expected ({amount_of_all_arguments}).'
                    )

                # Calculate the number of required arguments
                amount_of_required_arguments = len([argument for argument in self.arguments if argument.required])
                amount_of_required_additional_arguments = amount_of_required_arguments - amount_of_parsed_arguments

                # Check if the number of parsed arguments is less than the number of required arguments
                if amount_of_parsed_arguments < amount_of_required_arguments:
                    parsing_errors.append(
                        f'Script requires ({amount_of_required_additional_arguments}) additional argument{"s" if amount_of_required_additional_arguments > 1 else ""}.'
                    )

                # Check for missing required arguments
                for argument in self.arguments:
                    if argument.required and amount_of_required_additional_arguments > 0:
                        parsing_errors.append(f'Missing required argument: <{argument.name}>.')
                        continue
                        
                    if self.parsed_arguments[argument.position]:
                        argument.value = self.parsed_arguments[argument.position]

            # Check for unknown flags in the parsed flags
            for parsed_flag in self.parsed_flags:
                search_result = [flag for flag in self.flags if flag.short == parsed_flag or flag.long == parsed_flag]
                if len(search_result) == 0:
                    parsing_errors.append(f'Unknown flag: {parsed_flag}.')

            # Check for missing required flags and validate flag values
            for flag in self.flags:
                if flag.required:
                    if flag.short not in self.parsed_flags and flag.long not in self.parsed_flags:
                        parsing_errors.append(f'Missing required flag: {flag.short}, {flag.long}.')
                        
                if flag.short in self.parsed_flags or flag.long in self.parsed_flags:
                    parsed_flag_value = self.parsed_flags.get(flag.short) or self.parsed_flags.get(flag.long)
                    if parsed_flag_value and flag.options is None and parsed_flag_value is not True:
                        parsing_errors.append(
                            f'Flag "{flag.short}, {flag.long}" does not expect a value, but one was given: "{parsed_flag_value}".'
                        )
                    else:
                        flag.value = parsed_flag_value

        # Assign the list of parsing errors encountered
        amount_of_parsing_errors = len(parsing_errors)
        if amount_of_parsing_errors > 0:
            print()
            print(f'({amount_of_parsing_errors}) Parsing errors occured:')
            for parsing_error in parsing_errors:
                print(parsing_error)
            print()
            print('Hint: Use the -h, --help flag for usage information.')
            print()
            sys.exit(1)
    
    # TODO: Restore replace name functionality directly to streamline function header
    def format_str(self, include_args:bool, include_meta:bool, minify_usage:bool, tab_padding:int):
        """
        Formats the CLI usage and meta information into a string.

        This method generates a formatted string containing the CLI's usage information,
        including arguments, commands, and flags. It can also include meta information
        such as the CLI's name, shorthand, and help description.

        Args:
            include_meta (bool): Whether to include meta information in the formatted string.
            print_usage (bool): Whether to include minified usage information in the formatted stri
            tab_padding (int): The number of spaces to use for indentation

        Returns:
            str: The formatted string containing the CLI's usage and meta information.
        """
        def pad(indented_formatted_string:str):
            """
            Pads the given string with a specified number of tab characters.

            Args:
                indented_formatted_string (str): The string to be padded with tabs.

            Returns:
                str: The input string prefixed with the specified number of tab characters.

            Detailed Comments:
            - tabs = '': Initialize an empty string to accumulate tab characters.
            - for _ in range(tab_padding): Loop over the range of tab_padding to determine the number of tabs to add.
            - tabs += TAB: Append a tab character to the tabs string in each iteration.
            - return f'{tabs}{indented_formatted_string}': Concatenate the accumulated tabs with the input string and return the result.
            """
            tabs = ''
            for _ in range(tab_padding):
                tabs += TAB
            return f'{tabs}{indented_formatted_string}'
        
        # Initialize an empty string to store the formatted output
        indented_formatted_string = ''
        
        # Set the name to './<name>' by default
        name = f'./{self.name}'
        if minify_usage:
            # Add shorthand and name to the formatted string
            indented_formatted_string = pad(f'{self.shorthand}, {self.name}')
        else:
            # Add usage information to the formatted string
            indented_formatted_string += '\n'
            indented_formatted_string += f'Usage:\n{TAB}{name}'
        
        # TODO: Reduce repetition
        amount_of_arguments_greater_0 = len(self.arguments)
        if amount_of_arguments_greater_0:
            indented_formatted_string += ' [ARGUMENTS]'
        
        amount_of_commands_greater_0 = len(self.commands)
        if amount_of_commands_greater_0:
            indented_formatted_string += ' [COMMAND]'
        
        amount_of_flags_greater_0 = len(self.flags)
        if amount_of_flags_greater_0:
            indented_formatted_string += ' [FLAGS]'
            
        if include_meta:
            indented_formatted_string += pad(f'\n\t{self.help}')
        
        if include_args:
            indented_formatted_string += '\n'
            
            # This variable will be used to keep track of the maximum width of the formatted lines
            line_width = 0
            # TODO: Refactor to prevent unncessay loops
            # Check if there are any arguments and calculate the maximum line width for formatting
            if amount_of_arguments_greater_0:
                for argument in self.arguments:
                    # Format the argument line with indentation and argument name
                    argument_line = f'{TAB}<{argument.name}>'
                    # Update the maximum line width based on the length of the argument line
                    line_width = max(line_width, len(argument_line))
                            
            # Check if there are any commands and calculate the maximum line width for formatting
            if amount_of_commands_greater_0:
                for command in self.commands:
                    # Format the command line with indentation, shorthand, and command name
                    command_line = f'{TAB}{command.shorthand}, {command.name}'
                    # Update the maximum line width based on the length of the command line
                    line_width = max(line_width, len(command_line))              
            
            # Check if there are any flags and calculate the maximum line width for formatting
            if amount_of_flags_greater_0:
                for flag in self.flags:
                    # Format the flag line with indentation, short flag, and long flag
                    flag_line = f'{TAB}{flag.short}, {flag.long}'
                    # If the flag has options, include them in the flag line
                    if flag.options:
                        flag_line += f' <{flag.long.replace("-", "")}>'
                    # Update the maximum line width based on the length of the flag line
                    line_width = max(line_width, len(flag_line))
                    
            def pad_arg_line(arg_line:str, arg_help:str|List[str], arg_options:List[str]=None):
                """
                Pads the argument line with the appropriate amount of spaces for alignment and adds help text.

                Args:
                    arg_line (str): The formatted argument/command/flag line.
                    arg_help (str or list): The help text associated with the argument/command/flag.

                Returns:
                    str: The formatted string with the argument/command/flag line and help text.
                """
                # Initialize an empty string to store the formatted output
                formatted_string = ''
                # Add the argument/command/flag line to the formatted string
                formatted_string += arg_line
                # Calculate the remaining width after the argument/command/flag line
                arg_line_rest_width = len(arg_line) - line_width
                # Check if the help text is a list (multiple lines of help text)
                if isinstance(arg_help, list):
                    # Iterate over each line of help text
                    for index, help_line in enumerate(arg_help):
                        if index == 0:
                            # For the first line of help text, add it with indentation
                            formatted_string += f'{TAB}{help_line}\n'
                            continue
                        # For subsequent lines of help text, add them with indentation and alignment
                        formatted_string += f'{TAB}{" " * line_width}{help_line}'
                else:
                    # If the help text is a single string
                    if arg_line_rest_width > 0:
                        # If there is remaining width, add the help text with indentation
                        help_line = f'{TAB}{arg_help}'
                    else:
                        # If there is no remaining width, add the help text with alignment
                        help_line = f'{TAB}{" " * (arg_line_rest_width * -1)}{arg_help}'
                    # Add the help text to the formatted string
                    formatted_string += help_line
                
                if arg_options:
                    formatted_string += '\n'
                    formatted_string += f'{TAB}{" " * line_width}Options: {arg_options}'
                    
                # Return the final formatted string
                return formatted_string
            
            # TODO: Reduce even more repetition
            # If there are arguments, include them in the formatted string
            if amount_of_arguments_greater_0:
                indented_formatted_string += '\n'
                indented_formatted_string += 'Arguments:\n'
                
                # Iterate over each argument and add its details to the formatted string
                for argument in self.arguments:
                    argument_line = f'{TAB}<{argument.name}>'
                    # Add the formatted argument line to the indented formatted string with a newline
                    indented_formatted_string += pad_arg_line(argument_line, argument.help)
                    indented_formatted_string += '\n' 
                            
            # # If there are commands, include them in the formatted string
            if amount_of_commands_greater_0:
                indented_formatted_string += '\n'
                indented_formatted_string += 'Commands:\n'
                
                # Iterate over each argument and add its details to the formatted string
                for command in self.commands:
                    # Format the command line with indentation
                    command_line = f'{TAB}{command.shorthand}, {command.name}'
                    # Add the formatted command line to the indented formatted string with a newline
                    indented_formatted_string += pad_arg_line(command_line, command.help)
                    indented_formatted_string += '\n'
            
            # If there are flags, include them in the formatted string
            if amount_of_flags_greater_0:
                indented_formatted_string += '\n'
                indented_formatted_string += 'Flags:\n'
                # Iterate over each flag and add its details to the formatted string
                for flag in self.flags:
                    # Format the flag line with indentation
                    flag_line = f'{TAB}{flag.short}, {flag.long}'
                    # TODO: Check wrong flag options
                    if flag.options:
                        flag_line += f' <{flag.long.replace("-", "")}>'
                    # Add the formatted flag line to the indented formatted string with a newline
                    indented_formatted_string += pad_arg_line(flag_line, flag.help, flag.options)
                    indented_formatted_string += '\n'
        
        return indented_formatted_string
            
    def print(self, include_args:bool=True, include_meta:bool=False, minify_usage:bool=False, tab_padding:int=0):
        """
        Prints the formatted CLI usage and meta information to the console.

        This method generates a formatted string containing the CLI's usage information,
        including arguments, commands, and flags. It can also include meta information
        such as the CLI's name, shorthand, and help description. The formatted string
        is then printed to the console.

        Args:
            include_args (bool): Whether to include arguments, commands, and flags in the formatted string.
            include_meta (bool): Whether to include meta information in the formatted string.
            minify_usage (bool): Whether to include minified usage information in the formatted string.
            tab_padding (int): The number of spaces to use for indentation.
        """
        
        # Generate the formatted string using the format_str method
        # The format_str method takes include_args, include_meta, minify_usage, and tab_padding as arguments
        indented_formatted_string = self.format_str(include_args, include_meta, minify_usage, tab_padding)
        
        # Print the final formatted string to the console
        print(indented_formatted_string)
    
    def get_meta(self):
        """
        Returns the meta information of the script for dynamic listing.
        """
        return {
            'name': self.name,
            'shorthand': self.short,
            'help': self.help,
            'arguments': self.arguments,
            'flags': self.flags,
        }

    def get_argument(self, name:str):
        """
        Returns the argument value with the given name.
        """
        for argument in self.arguments:
            if argument.name == name:
                return argument.value
        return None
        
    def get_command(self):
        """
        Returns the value of the command.

        This method retrieves the value associated with the command
        that has been parsed from the command-line input.

        Returns:
            Any: The value of the command, initially set to None.
        """
        # Access the value attribute of the command instance and return it
        # TODO: Always return long value of command
        for command in self.commands:
            if command.value:
                return command.value
        return None
        
    def get_flag(self, name:str) -> any:
        """
        Returns the flag value with the given name.
        """
        for flag in self.flags:
            if flag.short == f'-{name}' or flag.long == f'--{name}':
                return flag.value
        return None
    
    def set_flag(self, name:str, value:any) -> bool:
        """
        Sets the flag value with the given name.
        """
        for flag in self.flags:
            if flag.short == f'-{name}' or flag.long == f'--{name}':
                flag.value = value
                return True
        return False
    
    @abstractmethod
    def meta(self) -> dict[
        'name':str,
        'shorthand':str,
        'help':str,
        'arguments':List[Argument],
        'commands':List[Command],
        'flags':List[Flag]]:
        """
        Override this method in the child classes to provide meta information.
        
        This method is used to ensure that the script works the same way whether it is executed directly
        or imported and then executed. The meta information such as name, shorthand, help, arguments, commands,
        and flags must be provided by the child class implementing this method.
        """
        raise NotImplementedError("Each script MUST implement the 'meta' method.")
                
    @abstractmethod
    def execute(self):
        """
        Override this method in the child classes to implement functionality.
        """
        raise NotImplementedError("Each script MUST implement the 'execute' method.")
    
    """
    # TODO: Make default return type and then catch that instead of relying on developer to remember implementing function
    Optional method to be overridden in child classes for pre-execution logic.
    Not making it abstract, to prevent the need to implement it in every child class.
    
        def pre_init(self) -> void
    
    Optional method to be overridden in child classes for pre-parsing logic.
    Not making it abstract, to prevent the need to implement it in every child class.
    
        def pre_parse(self) -> void
    
    Optional method to be overridden in child classes for pre-execution logic.
    Not making it abstract, to prevent the need to implement it in every child class.
    
        def pre_execute(self) -> void
    
    Override this method in the child classes to modify meta information.

    This method is used to allow dynamic modification of the meta information
    such as name, shorthand, help, arguments, commands, and flags. The child class
    implementing this method must provide the modified meta information.

    Returns:
        dict: A dictionary containing the modified meta information with keys:
                'name', 'shorthand', 'help', 'arguments', 'commands', and 'flags'.
    
        def modified_meta(self) -> dict[
            'name':str,
            'shorthand':str,
            'help':str,
            'arguments':List[Argument],
            'commands':List[Command],
            'flags':List[Flag]]
    """