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

# From system imports
from abc import ABC, abstractmethod
from typing import Generic, List, Type, TypeVar

_AVAILABLE_FIELDS = [
    'cls',
    'editable',
    # 'instance',
    'indexed',
    'key',
    'required',
    'type'
]
# Type alias for attribute types
T = TypeVar('T')

# TODO: Try to do automatic type checking and assignment in ValueWrapper as well
# TODO: Implement support for dicts and lists (potentially dangerous though)
class HSDBField(ABC, Generic[T]):
    _cached_value:object        # Cache for the field value
    _key:str                    # internal storage for key
    _value:object               # internal storage for value
    _wrapper:'_ValueWrapper'    # internal storage for value wrapper
    editable:bool               # Whether the attribute can be edited, automatically set to False if computed
    indexed:bool                # Whether the attribute is indexed
    key:str                     # Property for the field key
    name:str                    # The field name # TODO: Check if this is needed anymore, maybe refactor in future
    required:bool               # Whether the attribute is required, automatically set to True if computed
    shortkey:str                # The short key for the attribute, useful for compression
    type:T                      # The type of the attribute
    value:any                   # Property for the field value

    def __init__(self, editable:bool, indexed:bool, required:bool, SUPPORTED_TYPES:List[Type], type:Type):
        # Manual type checking to complement static type checking
        if type not in SUPPORTED_TYPES:
            raise ValueError(f'Unsupported type: {type.__name__}, supported types are: {SUPPORTED_TYPES}')
        if not isinstance(editable, bool):
            raise ValueError('editable must be a boolean')
        if not isinstance(indexed, bool):
            raise ValueError('indexed must be a boolean')
        if not isinstance(required, bool):
            raise ValueError('required must be a boolean')
        
        self.editable = editable
        self.indexed = indexed
        self.required = required
        self.type = type
        
        self._cached_value = None
        self._key = None
        self._value = None
        self._wrapper = None
        self.name = None
        
    def __set_name__(self, owner, name):
        """Automatically assigns the field name when the class is created."""
        self.name = name
        
    ##############
    # Properties #
    ##############
    
    @property
    def cls(self):
        return self.__class__
    
    @property
    def instance(self):
        return self.__instance

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value
        
    ######################
    # Descriptor Methods #
    ######################

    def __set__(self, instance, value):
        # Set the value and cache it
        # TODO: Fix validation
        # self._validate_value(value)
        # instance.__dict__[self.name] = value
        self._wrapper = None # Invalidate the cached wrapper

    def __set_name__(self, owner, name):
        self.name = name # Store the field name for later use in the instance
        self._key = name # Set the key to the field name by default
        
    ##################
    # Setter Methods #
    ##################

    @key.setter
    def key(self, new_key:str):
        self._validate_key(new_key)
        self._key = new_key

    @value.setter
    def value(self, new_value:any):
        # self._validate_value(new_value)
        self._value = new_value
        
    ####################
    # Internal Classes #
    ####################

    class _ValueWrapper(ABC):
        cache_values:dict = {} # Cache for the field values
        """
        Wrapper that stores both the value and the field pointer reference.
        """
        def __init__(self, value:any,
                     field:str,
                     additional_available_fields:List[str]=[],
                     available_functions:List[str]=[]):
            self._value = value
            # DEPRECATED: This is no longer needed since we are using lazy loading and caching
                # The field metadata (e.g., type, required), no longer keeping reference to the original HSDBField
            self._field = field
            
            self.cache_values = {}
            self._cached_metadata = None
            self._metadata_loaded = False
            
            # Dynamically create properties that fetch from metadata
            for prop in (_AVAILABLE_FIELDS + additional_available_fields):
                self.cache_values[prop] = getattr(self._field, prop)
                # Create a property for each available field
                # This allows us to access the metadata without needing to call a method
                setattr(self.__class__, prop, property(lambda self, p=prop: self._load_metadata().get(p)))
                
            # Dynamically create function aliases
            for func in available_functions:
                # Create a function alias for each available function
                # This allows us to access the metadata without needing to call a method
                setattr(self.__class__, func, lambda self, f=func: getattr(self._field, f)())

        # DEPRECATED: This method is not needed anymore since lazy loading and caching optimization
            # def __getattr__(self, item):
            #     """
            #     If we access metadata (e.g., `student_A.id.type`), return it from the field.
            #     """
            #     return getattr(self._field, item)

        def __repr__(self):
            return repr(self._value)

        def __str__(self):
            return str(self._value)
        
        def _load_metadata(self):
            """
            Load the metadata (lazy loading).
            """
            if not self._metadata_loaded:
                # Cache the metadata to avoid reloading it
                self._cached_metadata = {
                    'cls': self._field.cls,
                    # 'instance': self._field,
                    'key': self._field.key
                }
                
                # Add the cached values to the metadata
                for cache_key, cache_value in self.cache_values.items():
                    self._cached_metadata[cache_key] = cache_value
                    
                del self.cache_values
                self._metadata_loaded = True
            return self._cached_metadata