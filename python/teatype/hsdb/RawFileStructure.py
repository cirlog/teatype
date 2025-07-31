# Copyright (C) 2024-2025 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
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
from teatype.io import path

_DEFAULT_ROOT_PATH = '/var/lib/hsdb'
_FS = {
    'hsdb': {
        'backups': {
            'index': {},
            'migration': {},
            'rawfiles': {}
        },
        'dumps': {
            'migrations': {}
        },
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

class _FSProxy:
    _current_path:str
    _root_path:str
    _struct:dict
    
    def __init__(self, structure, root_path, current_path=''):
        self._structure = structure
        self._root_path = root_path
        self._current_path = path.join(root_path, current_path) if current_path else root_path
    
    def __getattr__(self, name):
        if name in self._structure:
            sub_structure = self._structure[name]
            return _FSProxy(sub_structure, self._root_path, path.join(self._current_path, name))
        raise AttributeError(f'No such attribute: {name}')
    
    @property
    def path(self):
        return self._current_path
    
    @property
    def struct(self):
        return self._structure
    
    def __repr__(self):
        return str({'path': self.path, 'struct': self.struct})

class RawFileStructure:
    _fs:_FSProxy
    _root_path:str
    
    def __init__(self, root_path:str, auto_create_folders:bool=True):
        self._root_path = root_path
        
        self._fs = _FSProxy(_FS, root_path)
        
        if auto_create_folders:
            self.create_fs(root_path, copy.deepcopy(_FS))
        
    def create_fs(self, base_path:str, struct:dict):
        for key, value in struct.items():
            dir_path = path.join(base_path, key)
            if not path.exists(dir_path):
                path.create(dir_path)
            if isinstance(value, dict):
                self.create_fs(dir_path, value)
        
    def get_fs(self):
        return self._fs