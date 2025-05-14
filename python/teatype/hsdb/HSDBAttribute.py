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
import sys

# From system imports
from typing import Generic, Type, TypeVar

# From package imports
from teatype.hsdb import HSDBField
from teatype.util import dt

# Supported attribute types
_AVAILABLE_FIELDS = [
    'computed',
    'description',
    'max_size',
    'required',
    'searchable',
    'unique'
]
_SUPPORTED_TYPES = [bool, dt, float, int, str]
# Type alias for attribute types
T = TypeVar('T')

# TODO: Try to do automatic type checking and assignment in ValueWrapper as well
# TODO: Implement support for dicts and lists (potentially dangerous though)
class HSDBAttribute(HSDBField):
    computed:bool         # Whether the attribute is computed, more of a flavour attribute, laxily enforced
    description:str       # Description of the attribute
    max_size:int          # Maximum size of the attribute value (only relevant for strings)
    searchable:bool       # Whether the attribute is searchable
    type:Type[T]          # holds an actual Python type, e.g. str, int, etc.
    unique:bool           # Whether the attribute value must be unique

    def __init__(self,
                 type:Type[T],
                 computed:bool=False,
                 description:str=None,
                 editable:bool=True,
                 indexed:bool=False,
                 max_size:int=sys.maxsize,
                 required:bool=False,
                 searchable:bool=False,
                 unique:bool=False):
        super().__init__(editable, indexed, required, _SUPPORTED_TYPES, type)
        
        if not isinstance(computed, bool):
            raise ValueError('computed must be a boolean')
        if not isinstance(description, str) and description != None:
            raise ValueError('description must be a string')
        if not isinstance(max_size, int):
            raise ValueError('max_size must be an integer')
        if not isinstance(searchable, bool):
            raise ValueError('searchable must be a boolean')
        if not isinstance(unique, bool):
            raise ValueError('unique must be a boolean')
        if max_size < 0:
            raise ValueError('max_size must be a positive integer')
        
        self.computed = computed
        self.description = description
        self.editable = False if computed else editable
        self.max_size = max_size
        self.required = True if computed else required
        self.searchable = searchable
        self.unique = unique

    def __get__(self, instance, owner):
        if self._wrapper is None: # Lazy loading of the wrapper
            value = instance.__dict__['_fields'].get(self.key)
            self._wrapper = self._AttributeWrapper(value.value, self)
        return self._wrapper
    
    def _validate_key(self, key):
        if self._key is not None:
            raise ValueError('key is already set')
        if not isinstance(key, str) or not key:
            raise ValueError('key must be a non-empty string')
        
    def _validate_value(self, value):
        # Check that value is of the expected type
        if not isinstance(value, self.type):
            raise ValueError(
                f'Value for attribute "{self.key}" must be of type {self.type.__name__}'
            )

        # Additional check: if value is a string, enforce max_size if applicable.
        if self.type is str and len(value) > self.max_size:
            raise ValueError(
                f'Value for attribute "{self.key}" exceeds maximum size ({self.max_size})'
            )
     
        if self.computed:
            raise ValueError(f'Attribute "{self.key}" is computed and cannot be set manually')
            
        if not self.editable:
            raise ValueError(f'Attribute "{self.key}" is not editable after it has been set once')
        
    #################
    # Class methods #
    #################
    
    @classmethod
    def __class_getitem__(cls, item: Type[T]) -> Type['HSDBAttribute']:
        """
        This method is used to handle generic types for HSDBAttribute.
        It ensures that the class can be correctly instantiated with the
        proper type (e.g., HSDBAttribute[str]).
        """
        # Ensure item is a valid type
        if item not in _SUPPORTED_TYPES:
            raise ValueError(f'Unsupported type: {item.__name__}, supported types are: {_SUPPORTED_TYPES}')
        # Return the class type with the parameter
        return cls
        
    ####################
    # Internal Classes #
    ####################
    
    class _AttributeWrapper(HSDBField._ValueWrapper):
        def __init__(self, value:any, field:str):
            super().__init__(value, field, _AVAILABLE_FIELDS)