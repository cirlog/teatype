# Copyright (C) 2024-2026 Burak Günaydin
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

# Third-party imports
from typing import Literal
from teatype.cli import BaseCLI
from teatype.io import path
from teatype.logging import *
from teatype.toolkit import dt

class InstallStep:
    def __init__(self,
                 name:str,
                 operation:callable,
                 type:Literal['system', 'package', 'config']):
        self.name = name
        self.operation = operation
        self.type = type

class InstallCache:
    def __init__(self, cache_file:str):
        self.cache_file = cache_file
        self.executed_steps = {}
        
        self._load_cache()
    
    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line:
                            step_name, timestamp = line.split('=', 1)
                            self.executed_steps[step_name.strip()] = timestamp.strip()
            except:
                err(f'Failed to load cache',
                    exit=True,
                    traceback=True)
    
    def is_executed(self, step_name:str) -> bool:
        return step_name in self.executed_steps
    
    def mark_executed(self, step_name:str):
        timestamp = dt.now()
        self.executed_steps[step_name] = timestamp
        self._save_cache()
        
# TODO: Write base install script that creates dist folder, adds it to .gitignore if not yet exists,
#       and creates an install flag file in the dist folder where everytime the install script is
#       executed, append the exact time and date of the installation and whether it was successful or not
#       into the install flag file.
class BaseInstallCLI(BaseCLI):
    def __init__(self):
        # Skipping 1 step in the call stack to get the script path implementing this class
        self.parent_path = path.caller_parent(reverse_depth=2, skip_call_stacks=-1)
        self.steps = []
        
        super().__init__()
    
    #########
    # Hooks #
    #########
    
    def meta(self):
        return {
            'name': 'install',
            'shorthand': 'i',
            'help': 'Install a package/module',
            'flags': [
                {
                    'shorthand': 'co',
                    'name': 'configs-only',
                    'help': 'Only install configuration file operations',
                    'required': False
                },
                {
                    'shorthand': 'po',
                    'name': 'packages-only',
                    'help': ['Only install package operations', 'Can be multi-threaded externally'],
                    'required': False
                },
                {
                    'shorthand': 'so',
                    'name': 'system-only',
                    'help': 'Only perform system operations amd installation',
                    'required': False
                }
            ]
        }

    def execute(self):
        if len(self.steps) == 0:
            err('No installation steps defined.',
                exit=True,
                verbose=False)