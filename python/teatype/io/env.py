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

def load_env():
    """
    Load environment variables from a .env file into the environment.

    This function checks for the existence of a .env file in the current directory.
    If the file exists, it reads each line, ignoring empty lines and comments,
    and sets the corresponding environment variables.
    """
    # Load environment variables from .env file if it exists
    if os.path.isfile('.env'):
        with open('.env') as env_file:
            for line in env_file:
                # Check if the line is not empty and does not start with a comment
                if line.strip() and not line.startswith('#'):
                    # Split the line into key and value using the first '=' as delimiter
                    key, _, value = line.partition('=')
                    # Strip whitespace and set the environment variable
                    os.environ[key.strip()] = value.strip()