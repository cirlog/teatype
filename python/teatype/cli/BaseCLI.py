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
from teatype.logging import err, hint

class GLOBAL_CLI_CONFIG:
    """
    Global configuration for the CLI utility.
    """
    DEBUG_MODE = False
    META_TYPE = dict[
        'name':str,
        'shorthand':str,
        'help':str,
        'arguments':List[Argument],
        'commands':List[Command],
        'flags':List[Flag]
    ]
    TAB = ' ' * 4
    USE_HELP_MESSAGE_ON_FAIL = True

# TODO: Make options and option seperate and option as a type descriptor only
# TODO: Make relations and depedencies between flags algorithmic
#       depends_on: 'flag_name' -> 'flag_name' must be set before this flag can be set
# TODO: Use log instead of print and println instead of pad_before and pad_after
# TODO: Seperate into optional and required arguments
# TODO: SIGINT handle_interrupt implemented traps
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
        _parsing_errors (list): A list of parsing errors encountered during validation.
    """
    _parsing_errors:List[str]
    arguments:List[Argument]
    commands:List[Command]
    flags:List[Flag]
    help:str
    name:str
    parsed_arguments:List[str]
    parsed_command:str
    parsed_flags:dict
    proxy_mode:bool
    shorthand:str
    
    def __init__(self,
                 proxy_mode:bool=False,
                 auto_init:bool=True,
                 auto_parse:bool=True,
                 auto_validate:bool=True,
                 auto_execute:bool=True,
                 env_path:str='.../.env'):
        """
        Initializes the BaseCLI instance with configuration options.

        Args:
            proxy_mode (bool, optional): If set to True, the CLI will operate in proxy mode, altering its behavior to function as a proxy.
                                          Defaults to False.
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
        """
        self.proxy_mode = proxy_mode
        
        # Load the environment variables from the specified .env file
        # TODO: Replace with own file class
        env_file = Path(env_path) # Create a Path object for the environment file path
        if env_file.exists(): # Check if the .env file exists at the given path
            with env_file.open() as f: # Open the .env file for reading
                for line in f: # Iterate over each line in the .env file
                    # Strip whitespace and ignore empty lines or lines starting with '#'
                    if line.strip() and not line.startswith('#'):
                        # Split the line into key and value at the first '=' character
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value # Set the environment variable in the OS environment
        
        self._parsing_errors = []
            
        if auto_init:
            self.init()
        
        if auto_parse:
            # Parse the command-line arguments and flags
            self.parse()

            if auto_validate:
                self.validate()
        
        if auto_execute:
            # This check is not really necessary, since hooks are present in code, but maybe using this
            # later to comment out the hooks and make them entirely optional and not available at runtime
            if hasattr(self, 'pre_execute') and callable(getattr(self, 'pre_execute')):
                # Hook for pre-execution logic
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
            
        # DEPRECATED: Disabled auto adding help flag for now
            # Add the default help flag for all scripts
            # self.flags.append(Flag(short='h', long='help', help='Display the (sometimes more detailed) help message.', required=False))
        self.flags.sort(key=lambda flag: flag.short) # Sort the flags by their short notation

    # TODO: Make positioning of arguments optional
    # TODO: Make flag assignment work with "="
    def parse(self):
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
                        command = arg
                        # DEPRECATED: Now allowing wrong commands to later handle them in validation
                            # for search_command in self.commands:
                            #     if arg == search_command.name or arg == search_command.shorthand:
                            #         command = arg
                            #         continue
                # If the argument is not a flag, add it to the positional arguments list
                arguments.append(arg)
            
            # Move to the next argument
            i += 1
            
        # Assign the parsed command name, positional arguments, and flags
        self.parsed_arguments = arguments
        self.parsed_command = command
        self.parsed_flags = flags
        
    def add_parsing_error(self, error_message:str):
        """
        Adds a new parsing error message to the list of parsing errors.

        This method appends a provided error message string to the internal
        list that tracks any errors encountered during argument parsing.
        """
        # Append the given error message to the _parsing_errors list,
        # which manages all accumulated parsing-related errors.
        self._parsing_errors.append(error_message)
        
    # TODO: Reduce repetition and amount of loops, more efficient algorithm
    def validate(self, silent_fail:bool=False, skip_hooks:bool=False):
        """
        Pre-execution checks for required arguments and flags.

        This method ensures that all required arguments and flags have been provided
        before the main execution of the CLI. If any required argument or flag is missing,
        it prints an error message and returns False, indicating that the execution should not proceed.

        Returns:
            bool: True if all required arguments and flags are provided, False otherwise.
        """
        def _validate_args():
            """
            Validates the parsed command-line arguments and flags.

            This function performs several validation checks on the parsed arguments and flags to ensure
            they meet the expected criteria defined by the CLI's configuration. It handles the presence
            of help flags, validates commands and their correctness, checks the number of arguments,
            and verifies the validity of flags and their associated values. Any encountered parsing
            errors are collected and reported to the user, optionally displaying the usage information.

            Raises:
                SystemExit: Exits the program if any parsing errors are detected.
            """
            if not skip_hooks:
                # Hook for pre-validation logic
                if hasattr(self, 'pre_validate') and callable(getattr(self, 'pre_validate')):
                    self.pre_validate()
            
            # Check if the help flag ('-h' or '--help') is present in the parsed flags
            if '-h' in self.parsed_flags or '--help' in self.parsed_flags:
                self.set_flag('help', True) # Set the help flag to True
                self.print_usage() # Display the CLI usage information
            else:
                if len(self.commands) > 0:
                    # If there are predefined commands, ensure only one command is provided
                    if len(self.parsed_arguments) > 1:
                        self.add_parsing_error('More than one command provided.')

                    if self.parsed_command:
                        found_command = False # Flag to indicate if the command is recognized
                        for command in self.commands:
                            # Check if the parsed command matches any predefined command name or shorthand
                            if self.parsed_command == command.name or self.parsed_command == command.shorthand:
                                command.value = self.parsed_command # Assign the parsed command value
                                found_command = True
                        if not found_command:
                            self.add_parsing_error(f'Unknown command: {self.parsed_command}.')
                    else:
                        self.add_parsing_error('No command provided.')
                else:
                    # If there are no predefined commands, validate the number of positional arguments
                    amount_of_parsed_arguments = len(self.parsed_arguments)
                    amount_of_all_arguments = len(self.arguments)
                    
                    if amount_of_parsed_arguments > amount_of_all_arguments:
                        self.add_parsing_error(
                            f'Number of possible arguments provided ({amount_of_parsed_arguments}) is greater than expected ({amount_of_all_arguments}).'
                        )

                    # Calculate the number of required arguments based on the CLI configuration
                    amount_of_required_arguments = len([argument for argument in self.arguments if argument.required])
                    amount_of_required_additional_arguments = amount_of_required_arguments - amount_of_parsed_arguments

                    if amount_of_parsed_arguments < amount_of_required_arguments:
                        plural = "s" if amount_of_required_additional_arguments > 1 else ""
                        self.add_parsing_error(
                            f'Script requires ({amount_of_required_additional_arguments}) additional argument{plural}.'
                        )

                        # Identify and report each missing required argument
                        for argument in self.arguments:
                            if argument.required and amount_of_required_additional_arguments > 0:
                                self.add_parsing_error(f'Missing required argument: <{argument.name}>.')
                                continue
                    else:
                        # Identify and report each missing required argument
                        for argument in self.arguments:
                            if self.parsed_arguments[argument.position]:
                                argument.value = self.parsed_arguments[argument.position]

                # Validate the presence of only known flags
                for parsed_flag in self.parsed_flags:
                    search_result = [flag for flag in self.flags if flag.short == parsed_flag or flag.long == parsed_flag]
                    if len(search_result) == 0:
                        self.add_parsing_error(f'Unknown flag: {parsed_flag}.')

                # Check for required flags and validate flag values
                for flag in self.flags:
                    if flag.required:
                        if flag.short not in self.parsed_flags and flag.long not in self.parsed_flags:
                            self.add_parsing_error(f'Missing required flag: {flag.short}, {flag.long}.')

                    if flag.short in self.parsed_flags or flag.long in self.parsed_flags:
                        # Retrieve the value associated with the flag, if any
                        parsed_flag_value = self.parsed_flags.get(flag.short) or self.parsed_flags.get(flag.long)
                        flag_options = flag.options
                        
                        # Validate flags that should not have a value
                        if parsed_flag_value and flag_options is None and parsed_flag_value is not True:
                            self.add_parsing_error(
                                f'Flag `{flag.short}, {flag.long}` does not expect a value, but one was given: "{parsed_flag_value}".'
                            )
                        else:
                            # Check if options even exist, otherwise treat as "True", "False"
                            if flag_options: 
                                if type(flag_options) == type:
                                    try:
                                        flag_options_name = flag_options.__name__
                                        # Convert the flag value to the expected type
                                        match flag_options_name:
                                            case 'int':
                                                parsed_flag_value = int(parsed_flag_value)
                                            case 'str':
                                                parsed_flag_value = str(parsed_flag_value)
                                            case 'bool':
                                                parsed_flag_value = bool(parsed_flag_value)
                                            case 'float':
                                                parsed_flag_value = float(parsed_flag_value)
                                    except Exception as exc:
                                        # Report type conversion errors
                                        self.add_parsing_error(
                                            f'Flag `{flag.short}, {flag.long}` expects a value of type {flag_options_name}, but "{parsed_flag_value}" was given.'
                                        )
                                else:
                                    # Validate that the flag value is within the allowed options
                                    if parsed_flag_value not in flag_options:
                                        self.add_parsing_error(
                                            f'Flag `{flag.short}, {flag.long}` expects a value from the list {flag_options}, but "{parsed_flag_value}" was given.'
                                        )
                            flag.value = parsed_flag_value # Assign the validated flag value
                            
                if not skip_hooks:
                    # Hook for pre-validation logic
                    if hasattr(self, 'post_validate') and callable(getattr(self, 'post_validate')):
                        self.post_validate()

                if not silent_fail:
                    amount_of__parsing_errors = len(self._parsing_errors) # Total number of errors found
                    if amount_of__parsing_errors > 0:
                        print() # Print a newline for better readability
                        err(f'({amount_of__parsing_errors}) Parsing errors occured:', use_prefix=False, verbose=False)
                        for parsing_error in self._parsing_errors:
                            print('  * ' + parsing_error) # List each parsing error
                        if GLOBAL_CLI_CONFIG.USE_HELP_MESSAGE_ON_FAIL:
                            self.print_usage() # Optionally display usage information on failure
                        else:
                            print()
                        sys.exit(1) # Exit the program due to parsing errors
                
        if GLOBAL_CLI_CONFIG.DEBUG_MODE:
            try:
                _validate_args()
            except SystemExit:
                pass # Allow SystemExit to pass silently in debug mode
            except:
                err('An error occured during validation.', exit=True, traceback=True)
        else:
            _validate_args()
    
    # TODO: Reduce code repetition, use more inline functions
    def format_str(self,
                   minify_usage:bool=False,
                   print_padding:int=0,
                   tab_padding:int=0) -> str:
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
        def pad(indented_formatted_string:str, print_padding:int=0) -> str:
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
            if print_padding:
                for _ in range(print_padding):
                    tabs += GLOBAL_CLI_CONFIG.TAB
            else:
                for _ in range(tab_padding):
                    tabs += GLOBAL_CLI_CONFIG.TAB
            return f'{tabs}{indented_formatted_string}'
        
        # Initialize an empty string to store the formatted output
        indented_formatted_string = ''
        
        amount_of_arguments_greater_0 = len(self.arguments)
        amount_of_commands_greater_0 = len(self.commands)
        # DEPRECATED: Not needed anymore really
            # Filter out the help flag from the list of flags
            # flags = list(filter(lambda flag: not flag.short == '-h' and not flag.long == '--help', self.flags)) 
        amount_of_flags_greater_0 = len(self.flags)
        
        # Set the name to './<name>' by default
        if self.proxy_mode:
            name = f'{self.shorthand}, {self.name}'
        else:
            name = f'./{self.name}'
        if minify_usage:
            # Add shorthand and name to the formatted string
            indented_formatted_string = pad(f'{name}\t{self.help}')
        else:
            # Add usage information to the formatted string
            indented_formatted_string += '\n'
            indented_formatted_string += f'Usage:\n{GLOBAL_CLI_CONFIG.TAB}{name}'

            if amount_of_arguments_greater_0:
                indented_formatted_string += ' [ARGUMENTS]'
            
            if amount_of_commands_greater_0:
                indented_formatted_string += ' [COMMAND]'
            
            if amount_of_flags_greater_0:
                indented_formatted_string += ' [FLAGS]'
                
            indented_formatted_string += '\n'
        
            # This variable will be used to keep track of the maximum width of the formatted lines
            line_width = 0
            # TODO: Refactor to prevent unncessay loops
            # Check if there are any arguments and calculate the maximum line width for formatting
            if amount_of_arguments_greater_0:
                for argument in self.arguments:
                    # Format the argument line with indentation and argument name
                    argument_line = f'{GLOBAL_CLI_CONFIG.TAB}<{argument.name}>'
                    # Update the maximum line width based on the length of the argument line
                    line_width = max(line_width, len(argument_line))
                            
            # Check if there are any commands and calculate the maximum line width for formatting
            if amount_of_commands_greater_0:
                for command in self.commands:
                    # Format the command line with indentation, shorthand, and command name
                    command_line = f'{GLOBAL_CLI_CONFIG.TAB}{command.shorthand}, {command.name}'
                    # Update the maximum line width based on the length of the command line
                    line_width = max(line_width, len(command_line))              
            
            # Check if there are any flags and calculate the maximum line width for formatting
            if amount_of_flags_greater_0:
                for flag in self.flags:
                    # Format the flag line with indentation, short flag, and long flag
                    flag_line = f'{GLOBAL_CLI_CONFIG.TAB}{flag.short}, {flag.long}'
                    # If the flag has options, include them in the flag line
                    if flag.options:
                        if type(flag.options) == list:
                            # DEPRECATED: Using default keyword 'option' instead for clarity
                                # flag_line += f' <{flag.long.replace("-", "")}>'
                            flag_line += ' <option>'
                        else:
                            if type(flag.options) == type:
                                flag_line += f' <{flag.options.__name__}>'
                            else:
                                err(f'Flag options must be a list or a type, not {type(flag.options).__name__}. Affected flag: {flag.short}, {flag.long}.',
                                    pad_before=1,
                                    pad_after=1,
                                    exit=True)
                    
                    # Update the maximum line width based on the length of the flag line
                    line_width = max(line_width, len(flag_line))
                    
            def pad_arg_line(arg_line:str, arg_help:str|List[str], arg_options:List[any]|type=None):
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
                            formatted_string += f'{" " * (arg_line_rest_width * -1)}{GLOBAL_CLI_CONFIG.TAB}{help_line}\n'
                            continue
                        # For subsequent lines of help text, add them with indentation and alignment
                        formatted_string += f'{GLOBAL_CLI_CONFIG.TAB}{" " * line_width}{help_line}'
                else:
                    # If the help text is a single string
                    if arg_line_rest_width > 0:
                        # If there is remaining width, add the help text with indentation
                        help_line = f'{GLOBAL_CLI_CONFIG.TAB}{arg_help}'
                    else:
                        # If there is no remaining width, add the help text with alignment
                        help_line = f'{GLOBAL_CLI_CONFIG.TAB}{" " * (arg_line_rest_width * -1)}{arg_help}'
                    # Add the help text to the formatted string
                    formatted_string += help_line
                
                if arg_options:
                    if type(arg_options) == list:
                        formatted_string += '\n'
                        formatted_string += f'{GLOBAL_CLI_CONFIG.TAB}{" " * line_width}Options: {arg_options}'
                    
                # Return the final formatted string
                return formatted_string
            
            # TODO: Reduce even more repetition
            # If there are arguments, include them in the formatted string
            if amount_of_arguments_greater_0:
                indented_formatted_string += '\n'
                indented_formatted_string += 'Arguments:\n'
                
                # Iterate over each argument and add its details to the formatted string
                for argument in self.arguments:
                    argument_line = f'{GLOBAL_CLI_CONFIG.TAB}<{argument.name}>'
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
                    command_line = f'{GLOBAL_CLI_CONFIG.TAB}{command.shorthand}, {command.name}'
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
                    flag_line = f'{GLOBAL_CLI_CONFIG.TAB}{flag.short}, {flag.long}'
                    # TODO: Check wrong flag options
                    if flag.options:
                        if type(flag.options) == list:
                            # DEPRECATED: Using default keyword 'option' instead for clarity
                                # flag_line += f' <{flag.long.replace("-", "")}>'
                            flag_line += ' <option>'
                        else:
                            flag_line += f' <{flag.options.__name__}>'
                                
                    # Add the formatted flag line to the indented formatted string with a newline
                    indented_formatted_string += pad_arg_line(flag_line, flag.help, flag.options)
                    indented_formatted_string += '\n'
        
        if print_padding > 0:
            lines = indented_formatted_string.split('\n')
            indented_formatted_string = '\n'.join([pad(line, print_padding) for line in lines])
        return indented_formatted_string
            
    def print_usage(self,
                    minify_usage:bool=False,
                    tab_padding:int=0,
                    print_padding:int=0):
        """
        Prints the formatted CLI usage and meta information to the console.

        This method generates a formatted string containing the CLI's usage information,
        including arguments, commands, and flags. It can also include meta information
        such as the CLI's name, shorthand, and help description. The formatted string
        is then printed to the console.

        Args:
            minify_usage (bool): Whether to include minified usage information in the formatted string.
            tab_padding (int): The number of spaces to use for indentation.
        """
        
        # Generate the formatted string using the format_str method
        # The format_str method takes include_args, include_meta, minify_usage, and tab_padding as arguments
        indented_formatted_string = self.format_str(minify_usage,
                                                    tab_padding,
                                                    print_padding)
        
        # Print the final formatted string to the console
        print(indented_formatted_string)
        sys.exit(1)
        
    def return_flags(self):
        """
        Returns a string of active flags with their corresponding values if applicable.

        This method iterates through all flags configured in the CLI. For each flag that has been set (i.e., has a value),
        it appends the long-form name of the flag to the result string. If the flag accepts an option, the value is appended
        alongside the flag name. The resulting string can be used for display or logging purposes to show which flags
        are currently active.
        
        Returns:
            str: A space-separated string of active flags, including their values if they have associated options.
        """
        # Initialize an empty string to accumulate active flags
        flags = ''
        
        # Iterate over each flag in the CLI's flags list
        for flag in self.flags:
            # Check if the current flag has been set (i.e., has a value)
            if flag.value:
                # If the flag accepts an option, append the flag's long name and its value
                if flag.options:
                    flags += f'{flag.long} {flag.value} '
                else:
                    # If the flag does not accept an option, append only the flag's long name
                    flags += f'{flag.long} '
        # Return the concatenated string of active flags
        return flags
        
    ###########
    # Getters #
    ###########
    
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
                return command.name
        return None
        
    def get_flag(self, name:str) -> any:
        """
        Returns the flag value with the given name.
        """
        for flag in self.flags:
            if flag.short == f'-{name}' or flag.long == f'--{name}':
                return flag.value
        return None
        
    ###########
    # Setters #
    ###########
    
    def set_flag(self, name:str, value:any) -> bool:
        """
        Sets the flag value with the given name.
        """
        for flag in self.flags:
            if flag.short == f'-{name}' or flag.long == f'--{name}':
                flag.value = value
                return True
        return False
    
    #########
    # Hooks #
    #########

    # TODO: Make default return type and then catch that instead of relying on developer to remember implementing function
    def modified_meta(self) -> GLOBAL_CLI_CONFIG.META_TYPE:
        """
        Override this method in the child classes to modify meta information.

        This method is used to allow dynamic modification of the meta information
        such as name, shorthand, help, arguments, commands, and flags. The child class
        implementing this method must provide the modified meta information.

        Returns:
            dict: A dictionary containing the modified meta information with keys:
                    'name', 'shorthand', 'help', 'arguments', 'commands', and 'flags'.
        """
        return {}
    
    def pre_init(self, *args, **kwargs) -> None:
        """
        Optional hook to be overridden in child classes for pre-parsing logic.
        Not making it abstract, to prevent the need to implement it in every child class.
        """
        pass
    
    def pre_parse(self, *args, **kwargs) -> None:
        """
        Optional hook to be overridden in child classes for pre-parsing logic.
        Not making it abstract, to prevent the need to implement it in every child class.
        """
        pass
    
    def pre_validate(self, *args, **kwargs) -> None:
        """
        Optional hook to be overridden in child classes for pre-validation logic.
        Not making it abstract, to prevent the need to implement it in every child class.
        """
        pass
        
    def post_validate(self, *args, **kwargs) -> None:
        """
        Optional hook to be overridden in child classes for post-validation logic.
        Not making it abstract, to prevent the need to implement it in every child class.
        """
        pass
    
    def pre_execute(self, *args, **kwargs) -> None:
        """
        Optional hook to be overridden in child classes for pre-execution logic.
        Not making it abstract, to prevent the need to implement it in every child class.
        """
        pass
    
    ######################
    # Abstract functions #
    ######################
    
    @abstractmethod
    def meta(self) -> GLOBAL_CLI_CONFIG.META_TYPE:
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