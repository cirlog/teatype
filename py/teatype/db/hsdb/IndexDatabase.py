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
import threading
from typing import Dict, List, Set

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
    _db:Index # For all raw data
    _indexed_fields:Dict[str, Dict[any, Set[str]]] # For all indexed fields for faster query lookups
    _model_index:Dict[str, Set[str]] # For all model references for faster model query lookups
    _relational_index:RelationalIndex # For all relations between models parsed dynamically from the model definitions
    models:List[type] # For all models
    
    # Thread locks for concurrent access
    _indexed_fields_lock:threading.Lock
    _model_index_lock:threading.Lock
    
    def __init__(self,
                 models:List[type]):
        self.models = models
        
        self._db = Index(cache_entries=False, 
                         primary_index_key='id',
                         max_size=None)
        
        # Initialize model index: maps model_name -> set of entry IDs
        self._model_index = {}
        self._model_index_lock = threading.Lock()
        
        # Initialize indexed fields: maps "ModelName.field_name" -> { value -> set of IDs }
        self._indexed_fields = {}
        self._indexed_fields_lock = threading.Lock()
        
        self._relational_index = RelationalIndex()
        
        # Pre-register models in the model index
        for model in models:
            self._model_index[model.__name__] = set()
        
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
    
    def get_indexed_fields_for_model(self, model:type) -> Dict[str, any]:
        """
        Get all indexed fields for a given model.
        Returns a dict of field_name -> HSDBAttribute for fields with indexed=True.
        """
        from teatype.db.hsdb import HSDBAttribute
        indexed = {}
        for attr_name in dir(model):
            attr = getattr(model, attr_name, None)
            if isinstance(attr, HSDBAttribute) and attr.indexed:
                indexed[attr_name] = attr
        return indexed
    
    def _add_to_model_index(self, model_name:str, entry_id:str) -> None:
        """Add an entry ID to the model index."""
        with self._model_index_lock:
            if model_name not in self._model_index:
                self._model_index[model_name] = set()
            self._model_index[model_name].add(entry_id)
    
    def _remove_from_model_index(self, model_name:str, entry_id:str) -> None:
        """Remove an entry ID from the model index."""
        with self._model_index_lock:
            if model_name in self._model_index:
                self._model_index[model_name].discard(entry_id)
    
    def _add_to_field_index(self, model_name:str, field_name:str, value:any, entry_id:str) -> None:
        """Add an entry to the field index for fast lookups."""
        index_key = f'{model_name}.{field_name}'
        with self._indexed_fields_lock:
            if index_key not in self._indexed_fields:
                self._indexed_fields[index_key] = {}
            if value not in self._indexed_fields[index_key]:
                self._indexed_fields[index_key][value] = set()
            self._indexed_fields[index_key][value].add(entry_id)
    
    def _remove_from_field_index(self, model_name:str, field_name:str, value:any, entry_id:str) -> None:
        """Remove an entry from the field index."""
        index_key = f'{model_name}.{field_name}'
        with self._indexed_fields_lock:
            if index_key in self._indexed_fields and value in self._indexed_fields[index_key]:
                self._indexed_fields[index_key][value].discard(entry_id)
                # Clean up empty sets
                if not self._indexed_fields[index_key][value]:
                    del self._indexed_fields[index_key][value]
    
    def _update_field_index(self, model_name:str, field_name:str, old_value:any, new_value:any, entry_id:str) -> None:
        """Update an entry in the field index when a value changes."""
        if old_value != new_value:
            self._remove_from_field_index(model_name, field_name, old_value, entry_id)
            self._add_to_field_index(model_name, field_name, new_value, entry_id)
    
    def lookup_by_field(self, model_name:str, field_name:str, value:any) -> Set[str]:
        """
        Fast O(1) lookup of entry IDs by indexed field value.
        Returns a set of entry IDs that have the given value for the field.
        """
        index_key = f'{model_name}.{field_name}'
        with self._indexed_fields_lock:
            if index_key in self._indexed_fields:
                return self._indexed_fields[index_key].get(value, set()).copy()
        return set()
    
    def lookup_by_model(self, model_name:str) -> Set[str]:
        """
        Fast O(1) lookup of all entry IDs for a given model type.
        """
        with self._model_index_lock:
            return self._model_index.get(model_name, set()).copy()
        
    ##################
    # ORM Operations #
    ##################
                
    def create_entry(self, model:type, data:dict, parse:bool=False) -> object|None:
        """
        Create a new entry in the database.
        
        Return codes:
            - 200: Success
            - 409: Conflict (Entry already exists)
            - 500: Internal Server Error
        """
        try:
            if parse:
                data = {
                    **data.get('base_data', {}),
                    **data.get('data', {})
                }
            
            # Create model instance
            model_instance = model(data)
            model_name = model_instance.model_name
            model_id = str(model_instance.id)
            
            # Check if entry already exists
            if model_id in self._db:
                return self._db.fetch(model_id), 409
            
            # Add to primary index
            self._db.add(model_id, model_instance)
            
            # Add to model index for O(1) model lookups
            self._add_to_model_index(model_name, model_id)
            
            # Add indexed fields to field index
            self._index_entry_fields(model_instance)
            
            return model_instance, 200
        except Exception as e:
            err(f'Could not create index database entry: {e}', traceback=True)
            return None, 500
    
    def _index_entry_fields(self, entry:object) -> None:
        """Index all indexed fields for an entry."""
        from teatype.db.hsdb import HSDBAttribute
        model_name = entry.model_name
        
        # Get cached attributes for this model
        if entry.__class__ in entry._attribute_cache:
            for attr_name, attr in entry._attribute_cache[entry.__class__].items():
                if isinstance(attr, HSDBAttribute) and attr.indexed:
                    try:
                        value = getattr(entry, attr_name)
                        if hasattr(value, '_value'):
                            value = value._value
                        self._add_to_field_index(model_name, attr_name, value, str(entry.id))
                    except:
                        pass
    
    def _unindex_entry_fields(self, entry:object) -> None:
        """Remove all indexed fields for an entry from indices."""
        from teatype.db.hsdb import HSDBAttribute
        model_name = entry.model_name
        
        if entry.__class__ in entry._attribute_cache:
            for attr_name, attr in entry._attribute_cache[entry.__class__].items():
                if isinstance(attr, HSDBAttribute) and attr.indexed:
                    try:
                        value = getattr(entry, attr_name)
                        if hasattr(value, '_value'):
                            value = value._value
                        self._remove_from_field_index(model_name, attr_name, value, str(entry.id))
                    except:
                        pass
    
    def update_entry(self, entry_id:str, data:dict) -> object|None:
        """
        Update an existing entry in the database.
        
        Return codes:
            - 200: Success
            - 404: Not Found
            - 500: Internal Server Error
        """
        try:
            entry_id = str(entry_id)
            if entry_id not in self._db:
                return None, 404
            
            entry = self._db.fetch(entry_id)
            
            # Remove old indexed field values
            self._unindex_entry_fields(entry)
            
            # Update the entry
            entry.update(data)
            
            # Re-index with new values
            self._index_entry_fields(entry)
            
            return entry, 200
        except Exception as e:
            err(f'Could not update index database entry: {e}', traceback=True)
            return None, 500
    
    def delete_entry(self, entry_id:str) -> bool:
        """
        Delete an entry from the database.
        
        Return codes:
            - 200: Success
            - 404: Not Found
            - 500: Internal Server Error
        """
        try:
            entry_id = str(entry_id)
            if entry_id not in self._db:
                return None, 404
            
            entry = self._db.fetch(entry_id)
            model_name = entry.model_name
            
            # Remove from field indices
            self._unindex_entry_fields(entry)
            
            # Remove from model index
            self._remove_from_model_index(model_name, entry_id)
            
            # Remove from primary index
            self._db.remove(entry_id)
            
            return True, 200
        except Exception as e:
            err(f'Could not delete index database entry: {e}', traceback=True)
            return False, 500
        
    def fetch_all(self, serialize:bool=False, include_relations:bool=False, expand_relations:bool=False) -> List[object]:
        """
        Fetch all entries from the database.
        
        Args:
            serialize: Whether to serialize entries to dicts
            include_relations: Whether to include relation IDs in serialization
            expand_relations: Whether to expand relations to full objects (implies include_relations)
        """
        entries = []
        for entry_id in self._db:
            entry = self._db.fetch(entry_id)
            if serialize:
                entry = entry.model.serialize(entry, 
                                              include_relations=include_relations,
                                              expand_relations=expand_relations)
            entries.append(entry)
        return entries
        
    def fetch_model_entries(self, model:type, serialize:bool=False, 
                           include_relations:bool=False, expand_relations:bool=False) -> List[object]:
        """
        Fetch all entries for a specific model type.
        Uses model index for O(1) lookup of entry IDs.
        
        Args:
            model: The model class to fetch entries for
            serialize: Whether to serialize entries to dicts
            include_relations: Whether to include relation IDs in serialization
            expand_relations: Whether to expand relations to full objects
        """
        entries = []
        model_name = model.__name__
        
        # Use model index for fast lookup
        entry_ids = self.lookup_by_model(model_name)
        for entry_id in entry_ids:
            try:
                entry = self._db.fetch(entry_id)
                if serialize:
                    entry = entry.model.serialize(entry,
                                                  include_relations=include_relations,
                                                  expand_relations=expand_relations)
                entries.append(entry)
            except KeyError:
                # Entry was deleted, remove from model index
                self._remove_from_model_index(model_name, entry_id)
        return entries
    
    def fetch_entry(self, id, serialize:bool=False, 
                   include_relations:bool=False, expand_relations:bool=False) -> object|None:
        """
        Fetch a single entry by ID.
        
        Args:
            id: The entry ID
            serialize: Whether to serialize the entry to a dict
            include_relations: Whether to include relation IDs in serialization
            expand_relations: Whether to expand relations to full objects
        """
        entry = self._db.fetch(str(id))
        if serialize:
            return entry.model.serialize(entry,
                                         include_relations=include_relations,
                                         expand_relations=expand_relations)
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
        Update or add entries directly in the database.
        Also updates model and field indices.
        Only for internal and testing use, skips validation.
        """
        for entry_id, entry in id_data_pair.items():
            entry_id = str(entry_id)
            is_new = entry_id not in self._db
            
            if not is_new:
                # Remove old indices before update
                old_entry = self._db.fetch(entry_id)
                self._unindex_entry_fields(old_entry)
            
            self._db.update({entry_id: entry})
            
            # Update indices
            if hasattr(entry, 'model_name'):
                self._add_to_model_index(entry.model_name, entry_id)
                self._index_entry_fields(entry)