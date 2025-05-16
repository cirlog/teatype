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
import threading

# From system imports
from typing import List

class IndexDatabase:
    _compute_index:dict # For all compute values for easy modification
    _compute_index_lock:threading.Lock
    _db:dict # For all raw data
    _db_lock:threading.Lock
    _indexed_fields:dict # For all indexed fields for faster query lookups
    _indexed_fields_lock:threading.Lock
    _model_index:dict # For all model references for faster model query lookups
    _model_index_lock:threading.Lock
    _relational_index:dict # For all relations between models parsed dynamically from the model definitions
    _relational_index_lock:threading.Lock
    models:List[type] # For all models
    
    def __init__(self, models:List[type]):
        self.models = models
        
        self._compute_index = dict()
        self._compute_index_lock = threading.Lock()
        
        self._db = dict()
        self._db_lock = threading.Lock()
        
        self._indexed_fields = dict()
        self._indexed_fields_lock = threading.Lock()
        
        self._model_index = dict()
        self._model_index_lock = threading.Lock()
        
        self._relational_index = dict()
        self._relational_index_lock = threading.Lock()
                
    def create_entry(self, model:type, data:dict, overwrite_path:str=None) -> object|None:
        try:
            with self._db_lock:
                # TODO: Validation
                model_instance = model(**data)
                model_name = model_instance.model_name
                with self._model_index_lock:
                    if model_name not in self._model_index:
                        self._model_index[model_name] = {}
                        
                model_id = model_instance.id
                if model_id in self._db:
                    return None
                
                # Model.create(overwrite_path, model_instance)
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
        
    # TODO: Query optimization with indices
    def get_entries(self, model:type, serialize:bool=False) -> List[object]:
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
    
    def get_entry(self, model_id:str, serialize:bool=False) -> object|None:
        with self._db_lock:
            entry = self._db.get(model_id)
            if serialize:
                return entry.serialize()
            return entry
        
    def query(self) -> None:
        pass