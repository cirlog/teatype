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
import re

# From system imports
from abc import ABC, abstractmethod

# From-as system imports
from datetime import datetime as dt

# From-as package imports
from teatype import generate_id

# TODO: Add validation method inside model
# TODO: Add attribute supports
# TODO: Add language supports
class HSDBModel(ABC):
    # created_at=HSDBAttribute('created_at', computed=True)
    # id=HSDBAttribute('id', computed=True, unique=True)
    # file_path=HSDBAttribute('file_path', computed=True)
    # is_fixture=HSDBAttribute('is_fixture', editable=False)
    # name=HSDBAttribute('name', computed=True)
    # plural_name=HSDBAttribute('plural_name', computed=True)
    # root_raw_path=HSDBAttribute('root_raw_path', computed=True)
    # updated_at=HSDBAttribute('updated_at', computed=True)
    _overwrite_file_path:str
    _overwrite_parsed_name:str
    _overwrite_parsed_plural_name:str
    _parsed_name:str
    _parsed_plural_name:str
    _plural_name:str
    app_name:str
    created_at:dt
    id:str
    is_fixture:bool=False
    migration_id:int
    relations:dict
    synced:bool=False
    synced_at:dt
    updated_at:dt
    
    def __init__(self,
                 id:str=None,
                 # TODO: Remove this stupid attribute
                 name:str=None,
                 created_at:str=None,
                 updated_at:str=None,
                 overwrite_file_path:str=None,
                 
                 migration_id:int=1,
                 migration_app_name:str='raw',
                 migrated_at:str=None,
                 
                 **kwargs):
        # TODO: Turn into util function
        def _parse_name(raw_name:str, seperator:str='-', plural:bool=False):
            return re.sub(r'(?<!^)(?=[A-Z])', seperator, raw_name).lower()
        
        if id is not None:
            self.id = id
        else:
            self.id = generate_id()
            
        if name is not None:
            self.name = name
        
        # TODO: Remove model name for redunancy when using a model index
        self.model_name = type(self).__name__ 
        self.model = self.__class__
        # TODO: Turn into util function
        self.parsed_name = _parse_name(self.model_name).replace('-model', '')
        self.parsed_plural_name = self.parsed_name + 's' if not self.parsed_name.endswith('s') else self.parsed_name + 'es'
        
        if overwrite_file_path:
            self.file_path = overwrite_file_path
        self.file_path = f'{self.parsed_plural_name}/{self.id}.json'
        
        if created_at:
            self.created_at = dt.fromisoformat(created_at)
        else:
            self.created_at = dt.now()
        if updated_at:
            self.updated_at = dt.fromisoformat(updated_at)
        else:
            self.updated_at = dt.now()
        
        # TODO: Make this dynamic
        self.app_name = 'raw'
        
        self.migration_id = migration_id
        
        if migration_app_name:
            self.migration_app_name = migration_app_name
            
        if migrated_at:
            self.migrated_at = dt.fromisoformat(migrated_at)
            
    # TODO: Figure out how to do this
    #     self._establishRelations()
    
    # # TODO: Implement
    # def _establishRelations(self):
    #     pass
    
    @abstractmethod
    def serializer(self) -> dict:
        raise NotImplementedError('Model does not have serializer')
    
    def serialize(self, json_dump:bool=False, use_data_key:bool=False) -> dict|str:
        serialized_data = self.serializer()
        data_key = self.parsed_name + '_data' if use_data_key else 'data'
        base_data = {
            'created_at': str(self.created_at),
            'id': self.id,
            'updated_at': str(self.updated_at)
        }
        migration_data = {
            'app_name': self.app_name,
            'migration_id': self.migration_id,
            # 'migration_precursor': self.migration_precursor,
        }
        if hasattr(self, 'migrated_at'):
            migration_data['migrated_at'] = str(self.migrated_at)
        if hasattr(self, 'migration_name'):
            migration_data['migration_name'] = self.migration_name
        if hasattr(self, 'migration_app_name'):
            migration_data['migration_app_name'] = self.migration_app_name
            
        model_data = {
            'app_name': self.app_name,
            'model_name': self.model_name,
        }
        relational_data = {}
        full_data = {
            'base_data': base_data,
            'migration_data': migration_data,
            'model_data': model_data,
            'relational_data': relational_data,
        }
        full_data[data_key] = serialized_data
        # TODO: Make this optional instead of baked into base model?
        if hasattr(self, 'name'):
            full_data[data_key]['name'] = self.name
            
        return full_data if not json_dump else json.dumps(full_data, indent=4)
    
    def snapshot(self) -> dict:
        snapshot_dict = {}
        for key, value in self.__dict__.items():
            # TODO: If variable is of type HSDBAttribute
            if isinstance(value, dt):
                snapshot_dict[key] = str(value)
        return snapshot_dict
    
    def update(self, data:dict):
        for key, value in data.items():
            setattr(self, key, value)
        self.updated_at = dt.now()