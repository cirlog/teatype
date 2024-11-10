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

class Focus(BaseCLI):
    def __init__(self):
        super().__init__(
            auto_init=False,
            auto_parse=False,
            auto_validate=False,
            auto_execute=False)
    
    def meta(self):
        return {
            'name': 'start',
            'shorthand': 'st',
            'help': 'Focus a process',
            'flags': [
                {
                    'short': 'e',
                    'long': 'env',
                    'help': 'Environment to consider',
                    'options': ['dev', 'prod'],
                    'required': True
                },
                {
                    'short': 'm',
                    'long': 'mode',
                    'help': 'Mode to consider',
                    'options': ['live', 'test'],
                    'required': False
                }
            ],
        }

    def execute(self):
        self.init()
        self.parse_args()
        self.validate_args()
        self.execute()

if __name__ == '__main__':
    Focus()