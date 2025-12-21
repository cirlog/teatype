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

# Standard-library imports
import json
from typing import List

# Third-party imports
from pympler import asizeof
from teatype.enum import EscapeColor
from teatype.db.hsdb.indices import Index, RelationalIndex
from teatype.logging import *

class _MemoryFootprint:
    def __init__(self, index_db:'IndexDatabase'):
        self.size_in_bytes = asizeof.asizeof(index_db)
        self.size_in_kilo_bytes = round(self.size_in_bytes / 1024, 2)
        self.size_in_mega_bytes = round(self.size_in_kilo_bytes / 1024, 2)
        
    def __repr__(self):
        return f'Index db memory footprint: {self.size_in_bytes} bytes, ' \
               f'{self.size_in_kilo_bytes} KB, '\
               f'{self.size_in_mega_bytes} MB'
        
    def __str__(self):
        return self.__repr__()
        
class IndexDatabase:
    # _cache_register:dict # For all dynamic query cache values
    # _compute_index:dict # For all compute values for easy modification
    _db:Index # For all raw data
    # _indexed_fields:dict # For all indexed fields for faster query lookups
    # _model_index:dict # For all model references for faster model query lookups
    _relational_index:RelationalIndex # For all relations between models parsed dynamically from the model definitions
    models:List[type] # For all models
    
    def __init__(self,
                 models:List[type]):
        self.models = models
        
        self._db = Index(cache_entries=False, 
                         primary_index_key='id',
                         max_size=None)
        
        # self._cache_register = dict()
        # self._compute_index = dict()
        # self._indexed_fields = dict()
        # self._model_index = dict()
        self._relational_index = RelationalIndex()
        
    ##############
    # Properties #
    ##############
        
    @property
    def memory_footprint(self) -> '_MemoryFootprint':
        # TODO: Replace with probe.memory()
        return _MemoryFootprint(self)
    
    @property
    def size(self) -> int:
        """
        Get the size of the database.
        """
        return len(self._db)
        
    ##################
    # ORM Operations #
    ##################
                
    def create_entry(self, model:type, data:dict, parse:bool=False) -> object|None:
        """
        Return codes:
            - 200: Success
            - 409: Conflict (Entry already exists)
            - 500: Internal Server Error
        """
        try:
            if parse:
                data = {
                    **data.get('base_data'),
                    **data.get('data')
                }
            # TODO: Restore proper validation
            model_instance = model(**data)
            model_name = model_instance.model_name
            with self._model_index_lock:
                if model_name not in self._model_index:
                    self._model_index[model_name] = {}
            
            model_id = model_instance.id
            if model_id in self._db:
                return self._db.fetch(model_id), 409
            
            # Model.create(root_path, model_instance)
            # TODO: Quick and dirty hack, need to refactor this with proper attributes
            # need for algorithm to be implemented with the model callhandlers
            existing_match = None
            match model_name:
                case 'InstrumentModel':
                    existing_match = next(
                        (
                            obj
                            for obj in self._db.values
                            if getattr(obj, 'model_name', None) == 'InstrumentModel'
                            and getattr(obj, 'article_number', None) == data.get('article_number')
                            and getattr(obj, 'manufacturer', None) == data.get('manufacturer')
                            # and getattr(obj, 'manufacturer_id', None) == data.get('manufacturer_id')
                        ),
                        None,
                    )
                case 'InstrumentTypeModel':
                    existing_match = next(
                        (
                            obj
                            for obj in self._db.values
                            if getattr(obj, 'model_name', None) == 'InstrumentTypeModel'
                            and getattr(obj, 'name', None) == data.get('name')
                        ),
                        None,
                    )
                case 'ManufacturerModel':
                    existing_match = next(
                        (
                            obj
                            for obj in self._db.values
                            if getattr(obj, 'model_name', None) == 'ManufacturerModel'
                            and getattr(obj, 'name', None) == data.get('name')
                        ),
                        None,
                    )
                case 'SurgeryTypeModel':
                    existing_match = next(
                        (
                            obj
                            for obj in self._db.values
                            if getattr(obj, 'model_name', None) == 'SurgeryTypeModel'
                            and getattr(obj, 'name', None) == data.get('name')
                        ),
                        None,
                    )
            if existing_match:
                return existing_match, 409
                    
            # if 'name' in data:
            #     with self._indexed_fields_lock:
            #         indexed_field_name = model_name + '_name'
            #         if indexed_field_name not in self._indexed_fields:
            #             self._indexed_fields[indexed_field_name] = {}
                    
            #         id = data.get('id')
            #         name = data.get('name')
            #         if name not in self._indexed_fields[indexed_field_name]:
            #             self._indexed_fields[indexed_field_name][name] = id
            
            self._db.add(model_id, model_instance)
            return model_instance, 200
        except:
            err('Could not create index database entry.', traceback=True)
            return None, 500
        
    def fetch_all(self, serialize:bool=False) -> List[object]:
        """
        Fetch all entries from the database.
        """
        entries = []
        for entry_id in self._db:
            entry = self._db.fetch(entry_id)
            if serialize:
                entry = entry.model.serialize(entry)
            entries.append(entry)
        return entries
        
    # TODO: Query optimization with indices
    def fetch_model_entries(self, model:type, serialize:bool=False) -> List[object]:
        entries = []
        for entry in self._db:
            if entry.model_name == model.__name__:
                if serialize:
                    entry = entry.model.serialize(entry)
                entries.append(entry)
        return entries
    
    def fetch_entry(self, id, serialize:bool=False) -> object|None:
        entry = self._db.fetch(id)
        if serialize:
            return entry.model.serialize(entry)
        return entry
        
    def print(self, limit:int=0) -> None:
        """
        Print the database.
        """
        counter = 0
        println()
        print('########################')
        print('Index database raw data:')
        print('------------------------')
        for entry in self._db:
            println()
            json_entry = json.dumps(entry.model.serialize(entry), indent=4)
            print(f'{EscapeColor.GREEN}{entry.id} {EscapeColor.GRAY}[{entry.id.key}]{EscapeColor.RESET}:')
            string_entry = str(json_entry).replace('{', '').replace('}', '').replace('"', '').replace(',', '').strip()
            string_entries = string_entry.split('\n')
            
            print(f'    {EscapeColor.RED}model: {EscapeColor.LIGHT_RED}{entry.model_name}{EscapeColor.RESET}')
            for sub_string_entry in string_entries:
                sub_string_entries = sub_string_entry.strip().split(':')
                if sub_string_entries[0] == 'id':
                    continue
                print(f'    {EscapeColor.BLUE}{sub_string_entries[0]}: {EscapeColor.LIGHT_CYAN}{sub_string_entries[1]}{EscapeColor.RESET}')
            
            if limit > 0:
                counter += 1
                if counter == limit:
                    break
        
        if limit > 0 and self.size > limit:
            println()
            print(f'... {self.size - limit} more entries')
        println()
        print('########################')
        println()
    
    def update_directly(self, id_data_pair:dict) -> object|None:
        """
        Update an entry directly in the database.
        Only for internal and testing use, skips all validation and parsing.
        """
        self._db.update(id_data_pair)