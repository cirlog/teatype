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
import threading

# From system imports
from typing import List

# From package imports
from pympler import asizeof
from teatype.enum import EscapeColor
from teatype.hsdb import HSDBAttribute
from teatype.hsdb.indices import Index, RelationalIndex
from teatype.logging import println

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
    _relational_index:dict # For all relations between models parsed dynamically from the model definitions
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
        return _MemoryFootprint(self)
    
    @property
    def size(self) -> int:
        """
        Get the size of the database.
        """
        with self._db_lock:
            return len(self._db.keys())
        
    ##################
    # ORM Operations #
    ##################
                
    def create_entry(self, model:type, data:dict, parse:bool=False) -> object|None:
        try:
            with self._db_lock:
                if parse:
                    data = {
                        **data.get('base_data'),
                        **data.get('data')
                    }
                # TODO: Validation
                model_instance = model(**data)
                model_name = model_instance.model_name
                with self._model_index_lock:
                    if model_name not in self._model_index:
                        self._model_index[model_name] = {}
                
                model_id = model_instance.id
                if model_id in self._db:
                    return None
                
                # Model.create(root_path, model_instance)
                # TODO: Quick and dirty hack, need to refactor this with proper attributes
                # need for algorithm to be implemented with the model callhandlers
                match model_name:
                    # case 'CameraModel':
                    #     pass
                    # case 'ImageModel':
                    #     pass
                    case 'InstrumentModel':
                        existing_match = next(
                            (
                                obj
                                for obj in self._db.values()
                                if getattr(obj, 'model_name', None) == 'InstrumentModel'
                                and getattr(obj, 'article_number', None) == data.get('article_number')
                                and getattr(obj, 'manufacturer', None) == data.get('manufacturer')
                                # and getattr(obj, 'manufacturer_id', None) == data.get('manufacturer_id')
                            ),
                            None,
                        )
                        if existing_match:
                            return None
                    case 'InstrumentTypeModel':
                        existing_match = next(
                            (
                                obj
                                for obj in self._db.values()
                                if getattr(obj, 'model_name', None) == 'InstrumentTypeModel'
                                and getattr(obj, 'name', None) == data.get('name')
                            ),
                            None,
                        )
                        if existing_match:
                            return None
                    # case 'LabelModel':
                    #     pass
                    case 'ManufacturerModel':
                        existing_match = next(
                            (
                                obj
                                for obj in self._db.values()
                                if getattr(obj, 'model_name', None) == 'ManufacturerModel'
                                and getattr(obj, 'name', None) == data.get('name')
                            ),
                            None,
                        )
                        if existing_match:
                            return None
                    case 'SurgeryTypeModel':
                        existing_match = next(
                            (
                                obj
                                for obj in self._db.values()
                                if getattr(obj, 'model_name', None) == 'SurgeryTypeModel'
                                and getattr(obj, 'name', None) == data.get('name')
                            ),
                            None,
                        )
                        if existing_match:
                            return None
                        
                self._db[model_id] = model_instance
                return model_instance
        except:
            import traceback
            traceback.print_exc()
            return None
        
    def fetch_all(self, serialize:bool=False) -> List[object]:
        """
        Fetch all entries from the database.
        """
        entries = []
        with self._db_lock:
            for entry_id in self._db:
                entry = self._db[entry_id]
                if serialize:
                    entries.append(entry.serialize())
                    continue
                entries.append(entry)
        return entries
        
    # TODO: Query optimization with indices
    def fetch_model_entries(self, model:type, serialize:bool=False) -> List[object]:
        entries = []
        with self._db_lock:
            for entry_id in self._db:
                entry = self._db[entry_id]
                if entry.model_name == model.__name__:
                    if serialize:
                        entries.append(entry.serialize())
                        continue
                    entries.append(entry)
        return entries
    
    def fetch_entry(self, id:HSDBAttribute, serialize:bool=False) -> object|None:
        with self._db_lock:
            entry = self._db.get(id)
            if serialize:
                return entry.serialize()
            return entry
        
    def print(self, limit:int=10) -> None:
        """
        Print the database.
        """
        counter = 0
        println()
        print('########################')
        print('Index database raw data:')
        print('------------------------')
        with self._db_lock:
            for entry_id in self._db:
                entry = self._db[entry_id]
                json_entry = json.dumps(entry.model.serialize(entry), indent=4)
                print(f'{EscapeColor.GREEN}{entry_id._value} {EscapeColor.GRAY}[{entry_id.key}]{EscapeColor.RESET}:')
                string_entry = str(json_entry).replace('{', '').replace('}', '').replace('"', '').replace(',', '').strip()
                string_entries = string_entry.split('\n')
                
                for sub_string_entry in string_entries:
                    sub_string_entries = sub_string_entry.strip().split(':')
                    if sub_string_entries[0] == 'id':
                        continue
                    print(f'    {EscapeColor.BLUE}{sub_string_entries[0]}: {EscapeColor.LIGHT_CYAN}{sub_string_entries[1]}{EscapeColor.RESET}')
                println()
                
                if limit > 0:
                    counter += 1
                    if counter == limit:
                        break
        
        if self.size > limit:
            print(f'... {self.size - limit} more entries')
        print('########################')
        println()
    
    def update_directly(self, id_data_pair:dict) -> object|None:
        """
        Update an entry directly in the database.
        Only for internal and testing use, skips all validation and parsing.
        """
        with self._db_lock:
            for entry_id in id_data_pair:
                entry = self._db.get(entry_id.value)
                if entry is not None:
                    continue
                
                self._db.update[entry_id.value] = id_data_pair[entry_id]