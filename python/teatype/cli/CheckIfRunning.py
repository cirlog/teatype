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
from teatype.cli import BaseCLI

class CheckIfRunning(BaseCLI):
    def __init__(self):
        super().__init__(
            auto_init=False,
            auto_parse=False,
            auto_validate=False,
            auto_execute=False)
    
    def meta(self):
        return {
            'name': 'check-if-running',
            'shorthand': 'cr',
            'help': 'Check if a process is running',
            'flags': [
                {
                    'short': 'h',
                    'long': 'hide-output',
                    'help': 'Hide verbose output of script',
                    'required': False
                }
            ],
        }

    def execute(self):
        pass

if __name__ == '__main__':
    CheckIfRunning()