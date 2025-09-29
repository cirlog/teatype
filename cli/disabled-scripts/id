#!/usr/bin/env python3.11

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
import time

# From package imports
from teatype.cli import BaseCLI
from teatype.io import file
from teatype.logging import err, hint, log, println

# From-as package imports
from teatype import generate_id

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

class Id(BaseCLI):
    def meta(self):
        return {
            'name': 'id',
            'shorthand': 'id',
            'help': 'Generates one or multiple (globally) unique identifiers',
            'flags': [
                # {
                #     'short': 'c',
                #     'long': 'count',
                #     'help': 'Set the number of identifiers to generate in burst-mode',
                #     'options': int,
                #     'required': False  
                # },
                # {
                #     'short': 'l',
                #     'long': 'length',
                #     'help': 'Set the length of the identifier',
                #     'options': int,
                #     'required': False
                # },
                {
                    'short': 'm',
                    'long': 'mode',
                    'help': ['Select the mode of the identifier generation', 'Default: single'],
                    'options': ['single', 'continous'],
                    # 'options': ['single', 'burst', 'continous'],
                    'required': False
                },
                {
                    'short': 'o',
                    'long': 'output',
                    'help': 'Save the generated identifier to a specified file',
                    'options': str,
                    'required': False
                }
            ]
        }
        
    #########
    # Hooks #
    #########
    
    def execute(self):
        # count = self.get_flag('count')
        # length = self.get_flag('length')
        
        println()
        
        mode = self.get_flag('mode')
        has_defaulted = False
        if mode is None:
            mode = 'single'
            has_defaulted = True
            
        if mode == 'continous':
            try:
                if not PYPERCLIP_AVAILABLE:
                    hint('Pyperclip is not available. Please install it to use continous mode.')
                else:
                    hint('Pyperclip is enabled. The generated ID will be copied to your clipboard.')
                    
                hint('Press CTRL+C to stop', use_prefix=False)
                println()
                while True:
                    id = generate_id()
                    print(id)
                    if PYPERCLIP_AVAILABLE:
                        pyperclip.copy(id)
                    
                    time.sleep(0.1)
                        
            except KeyboardInterrupt:
                println()
                log('Continous mode stopped.')
                println()
                return
        elif mode == 'burst':
            err('Burst mode is not yet implemented.')
            return
        elif mode == 'single':
            generated_ids = generate_id()
            
        if PYPERCLIP_AVAILABLE:
            hint('Result copied to clipboard')
            pyperclip.copy(generated_ids)
        
        println()
        log('Generated IDs:')
        log(generated_ids)
        
        output = self.get_flag('output')
        if output:
            file.write(output, generated_ids)
            
        if has_defaulted:
            println()
            hint('More options available, use `-h, --help` for more information')
            
        println()

if __name__ == '__main__':
    Id()