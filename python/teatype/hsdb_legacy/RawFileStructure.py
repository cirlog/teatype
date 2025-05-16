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
import copy

# From package imports
from teatype.io import env, file, path

__FS = {
    'hsdb': {
        'backups': {
            'index': {},
            'migration': {},
            'rawfiles': {}
        },
        'dumps': {},
        'exports': {},
        'index': {},
        'logs': {
            'migrations': {}
        },
        'meta': {},
        'models': {
            'adapters': {},
        },
        'rawfiles': {},
        'redundancy': {},
        'rejectpile': {
            'index': {},
            'rawfiles': {}
        }
    }   
}

class RawFileStructure:
    _fs:dict
    
    def __init__(self, root_data_path:str):
        self._fs = copy.deepcopy(__FS)
        
    def expand_fs(self, fs:dict, root_data_path:str):
        for key, value in fs.items():
            if isinstance(value, dict):
                path.create(f'{root_data_path}/{key}')
                self.expand_fs(value, f'{root_data_path}/{key}')
                
    def shrink_fs(self, fs:dict, root_data_path:str):
        for key, value in fs.items():
            if isinstance(value, dict):
                path.remove(f'{root_data_path}/{key}')
                self.shrink_fs(value, f'{root_data_path}/{key}')
                
    def get_fs(self):
        return self._fs