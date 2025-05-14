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
import json
import pprint

# From system imports
from abc import ABC
from typing import List

# From package imports
from teatype.hsdb import HSDBAttribute, HSDBField, HSDBMeta, HSDBQuery, HSDBRelation
from teatype.util import dt, staticproperty

# From-as package imports
from teatype.util import generate_id, kebabify

# TODO: Implement a short-key map for attributes for compression
#       - automate by implementing a smart algorithm that first checks how many seperations of underscore are there and then abbreviates that way
#       - it also uses indexing for shortenting attribute names and checks for collisions and adjusts index length accordingly
# TODO: Implement auto-compute variable for count of reverse lookup models (amount_of_<relation_name>s)
# TODO: Replace data with kwargs on init
# TODO: Add allowing to use string literal for relation name to avoid circular imports (need access to hybridstorage to iterate through models)
# TODO: Add validation method inside model
# TODO: Add language supports
class HSDBModel(ABC, metaclass=HSDBMeta):
    # Private class variables
    # _app_name:str # TODO: Implement these as computed properties
    _attribute_cache = {} # Cache to store attributes once for each class
    _overwrite_path:str
    _overwrite_name:str
    _overwrite_plural_name:str
    _relations:dict
    
    # Public class variables
    model:type['HSDBModel']
    path:str
    model_name:str
    resource_name:str
    resource_name_plural:str
    # migrated_at:dt
    # migration_app_name:str
    # migration_id:int
    # migration_name:str
    
    # HSDB attributes
    # app_name     = HSDBAttribute(str,  editable=False) # TODO: Maybe make this as a computed python property?
    created_at   = HSDBAttribute(dt,   computed=True)
    id           = HSDBAttribute(str,  computed=True, unique=True)
    # is_fixture   = HSDBAttribute(bool, computed=True) # TODO: Maybe make this as a computed python property?
    # migration_id = HSDBAttribute(int,  computed=True) # TODO: Maybe make this as a computed python property?
    # synced_at    = HSDBAttribute(dt,   computed=True)
    updated_at   = HSDBAttribute(dt,   computed=True)
    # was_synced   = HSDBAttribute(bool, computed=True)
    
    def __init__(self,
                 data:dict,
                 include_base_attributes:bool=True,
                 overwrite_path:str=None):
        # For every class variable that is an HSDBAttribute,
        # create an instance deepcopy, assign its key to the variable name,
        # and, if the field is provided in the data dict, set its value.
        # Necessary to avoid sharing the same attribute instance across all instances.
        # Look up cached attributes for this class
        # Cache the attributes if not already cached
        if self.__class__ not in self._attribute_cache:
            self._cache_attributes()
            
        # TODO: Make this more efficient since only class needs to know this information
        # Model name and pluralization
        self.model_name = type(self).__name__
        self.model = self.__class__
        self.resource_name = kebabify(self.model_name, remove='-model', plural=False)
        self.resource_name_plural = kebabify(self.model_name, remove='-model', plural=True)
        
        # Create a dict to hold instance-specific field values
        self._fields = {}
        for attribute_name, attribute in self._attribute_cache[self.__class__].items():
            if isinstance(attribute, HSDBRelation._RelationFactory):
                if attribute.required and attribute_name not in data:
                    raise ValueError(f'Model "{self.model_name}" init error: "{attribute_name}" is required')
                continue
            
            if attribute.required and not attribute.computed and attribute_name not in data:
                raise ValueError(f'Model "{self.model_name}" init error: "{attribute_name}" is required')
            
            if attribute_name in data:
                # Validate type before assignment
                if not isinstance(data.get(attribute_name), attribute.type):
                    raise ValueError(f'Field "{attribute_name}" must be of type {attribute.type.__name__}')
                if attribute.computed:
                    raise ValueError(f'{attribute_name} is computed and cannot be set')
                setattr(self, attribute_name, data.get(attribute_name))
        
        # TODO: Find a more elegant solution than this ugly a** hack
        # self.id.instance.__computational_override__(generate_id(truncate=5))
        self.id = generate_id()
                
        # Having to initalize lazily, because needing id to properly intialize relations
        for attribute_name, attribute in self._attribute_cache[self.__class__].items():
            if isinstance(attribute, HSDBAttribute):
                continue
            
            # Assume that if the attribute is not an HSDBAttribute, it is a relation
            if attribute_name in data:
                attribute_value = data.get(attribute_name)
                
                if attribute.type == List[str]:
                    if not all(isinstance(item, str) for item in attribute_value) and \
                       not all(isinstance(item, HSDBModel) for item in attribute_value) and \
                       not all(isinstance(item, HSDBAttribute._AttributeWrapper) for item in attribute_value):
                        raise ValueError(f'Field "{attribute_name}" must be a list of id strings or HSDBModel instances')
                else:
                    if not isinstance(attribute_value, attribute.type) and \
                       not isinstance(attribute_value, HSDBModel) and \
                       not isinstance(attribute_value, HSDBAttribute._AttributeWrapper):
                           raise ValueError(f'Field "{attribute_name}" must be of type "{attribute.type.__name__}" or an HSDBModel instance')
                
                # Allowing to pass both model instance and id string
                if isinstance(attribute_value, HSDBModel):
                    attribute_value = attribute_value.id
                elif isinstance(attribute_value, list):
                    # If the attribute is a list of HSDBModel instances, extract their IDs
                    if all(isinstance(item, HSDBModel) for item in attribute_value):
                        attribute_value = [item.id for item in attribute_value]
                    else:
                        attribute_value = [item for item in attribute_value]
                    
                # Initialize the relation lazily
                setattr(self, attribute_name, attribute_value)
        
        current_time = dt.now()
        self.created_at = current_time
        self.updated_at = current_time
            
        if overwrite_path:
            self.path = overwrite_path
        self.path = f'{self.resource_name_plural}/{self.id}.json'
        
        # TODO: Make this dynamic
        # self.app_name = 'raw'
        # self.migration_id = 1
    
    def __getattribute__(self, name):
        # If the field name is in our field cache, return the value from _fields
        _cache = object.__getattribute__(self, '_attribute_cache')
        model = type(self)
        if model in _cache and name in _cache[model]:
            return object.__getattribute__(self, '_fields').get(name).__get__(self, self.__class__)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        # if attribute_name in data:
        #     instance_relation = attribute.lazy_init(
        #         self.id,
                
        #         data.get(attribute_name),
        #     )
        #     instance_relation.key = attribute_name
            
        #     instance_relation.value = attribute._query_closure
        #     setattr(self, attribute_name, attribute_value)
        
        _cache = self.__class__._attribute_cache.get(self.__class__, {})
        if name in _cache:
            attribute = _cache[name]
            if isinstance(attribute, HSDBAttribute):
                instance_attribute = HSDBAttribute(
                    attribute.type, 
                    **{key: value for key, value in vars(attribute).items() if key not in [
                        'name', 'type', '_cached_value', '_key', '_value', '_wrapper']} # Exclude these keys
                )
                instance_attribute.key = attribute.name
                instance_attribute.value = value
            elif isinstance(attribute, HSDBRelation._RelationFactory):
                if attribute.type == List[str]:
                    instance_value = [v._value if isinstance(v._value, str) else v._value for v in value]
                else:
                    instance_value = [value._value] if isinstance(value._value, str) else value._value
                instance_attribute = attribute.lazy_init(
                    [self.id._value] if isinstance(self.id._value, str) else self.id._value,
                    self.model,
                    instance_value
                )
                instance_attribute.key = name
                instance_attribute.value = instance_attribute._value
            self.__dict__.setdefault('_fields', {})[name] = instance_attribute
        else:
            super().__setattr__(name, value)
    
    # TODO: Optimization
    def _cache_attributes(self):
        """
        Cache the attributes for this class (including its ancestors).
        """
        self._attribute_cache[self.__class__] = {}
        seen = set()

        # Traverse through the method resolution order to gather attributes
        for model in reversed(self.__class__.__mro__):
            for attribute_name, attribute in model.__dict__.items():
                if attribute_name in seen:
                    continue
                if isinstance(attribute, HSDBAttribute) or isinstance(attribute, HSDBRelation._RelationFactory):
                    seen.add(attribute_name)
                    self._attribute_cache[self.__class__][attribute_name] = attribute
                    
    @property
    def serializer(self) -> dict:
        """
        If this method is not overridden, collect all HSDBAttribute fields.
        If this method is overridden, collect all fields that are not computed.
        """
        serialized = dict()
        for attribute_name in self.__dict__['_fields']:
            # Skip non-HSDBAttribute fields
            try:
                if attribute_name in self._fields:
                    serialized[attribute_name] = getattr(self, attribute_name)
            except Exception as exc:
                continue
        return serialized
        
    @staticproperty
    def query(self):
        # Always return a new query builder instance when query is accessed.
        return HSDBQuery(self)
    
    def print(self):
        pprint.pprint(self.model.serialize(self))
    
    # TODO: Optimization
    # TODO: Group data with key and base data into index data
    @staticmethod
    def serialize(object:object,
                  fuse_data:bool=False,
                  include_migration:bool=True,
                  include_model:bool=True,
                  json_dump:bool=False,
                  strip_attributes:bool=False,
                  use_data_key:bool=False) -> dict|str:
        serialized_data = object.serializer
        return serialized_data
    
        serialized_data = dict()
            
        if fuse_data:
            return {**base_data, **serializer}
        else:
            base_data = {
                'created_at': str(self.created_at),
                'id': self.id,
                'updated_at': str(self.updated_at)
            } 
            serialized_data['base_data'] = base_data
        
        data_key = self.resource_name + '_data' if use_data_key else 'data'
        serialized_data[data_key] = serializer
        
        if include_migration:
            migration_data = {
                'app_name': self.app_name,
                'migration_id': self.migration_id,
            }  
            serialized_data['migration_data'] = migration_data
            
        if include_model:
            model_data = {
                'app_name': self.app_name,
                'model_name': self.model_name,
            }
            serialized_data['model_data'] = model_data
        
        return serialized_data if not json_dump else json.dumps(serialized_data, indent=4)
    
    def snapshot(self) -> dict:
        snapshot_dict = {}
        for key, value in self.__dict__.items():
            # TODO: If variable is of type HSDBAttribute
            if isinstance(value, dt):
                snapshot_dict[key] = str(value)
        return snapshot_dict
    
    def save(self):
        # TODO: Save to database and rawfile
        pass
    
    def update(self, data:dict):
        # TODO: Patch the model with the given data in model, db and rawfile
        for key, value in data.items():
            setattr(self, key, value)
        self.updated_at = dt.now()
    
    ##################
    # Static methods #
    ##################
    
    @staticmethod
    def load(self, dict_data:dict):
        pass