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

# From package imports
from teatype.logging import err

# From system imports
from typing import List

class Flag:
    """
    Represents a command-line flag.
    Attributes:
        short (str): The short form of the flag (e.g., '-h').
        long (str): The long form of the flag (e.g., '--help').
        help (str): A brief description of the flag.
        depends_on (List[str]): A list of flags that this flag depends on.
        required (bool): Indicates whether the flag is required.
        options (List[any]|type): A list of options for the flag or the type of option for the flag.
    """
    def __init__(self,
                short:str,
                long:str,
                help:str|List[str],
                required:bool,
                depends_on:List[str]=None,
                options:List[any]|type=None):
        self.help = help
        self.depends_on = depends_on
        self.required = required
        
        self.short = f'-{short}'
        self.long = f'--{long}'
        
        # Check if 'options' are provided for the flag
        if options:
            # Verify that 'options' is either a list or a type
            if not isinstance(options, list) and not isinstance(options, type):
                # Append ' <option>' to the flag line to indicate that an option is expected
                flag_line += ' <option>'
                # Log a runtime error with details about the invalid 'options' type and terminate execution
                err(f'Runtime error: Flag options must be a list or a type, not {type(options).__name__}. Affected flag: {short}, {long}.',
                    pad_before=1,
                    pad_after=1,
                    exit=True,
                    raise_exception=TypeError)
            else:
                # TODO: Check type consistency of list
                pass
        # Assign the validated 'options' to the flag's 'options' attribute
        self.options = options
        
        self.value = None # Initialize the value of the flag to None