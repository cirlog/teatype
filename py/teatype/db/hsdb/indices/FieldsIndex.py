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
from typing import Any, Set

# Third-party imports
from teatype.db.hsdb.indices.BaseIndex import BaseIndex

class FieldsIndex(BaseIndex):
    """
    Index for fast field-value lookups.
    
    Structure:
        primary_index = {
            "ModelName.field_name": {
                value1: {entry_id1, entry_id2, ...},
                value2: {entry_id3, ...},
                ...
            },
            ...
        }
    
    Provides O(1) lookups for "find all entries where field X equals value Y".
    """
    
    def __init__(self,
                 cache_entries:bool=False,
                 max_size:int=None) -> None:
        super().__init__(cache_entries=cache_entries, max_size=max_size)
    
    def _get_index_key(self, model_name:str, field_name:str) -> str:
        """Generate the composite key for model.field indexing."""
        return f'{model_name}.{field_name}'
    
    def add_entry(self, model_name:str, field_name:str, value:Any, entry_id:str) -> None:
        """
        Add an entry ID to the index for a specific field value.
        
        Args:
            model_name: Name of the model class
            field_name: Name of the indexed field
            value: The field value to index
            entry_id: The entry ID to associate with this value
        """
        index_key = self._get_index_key(model_name, field_name)
        with self.transaction_lock:
            if index_key not in self.primary_index:
                self.primary_index[index_key] = {}
            if value not in self.primary_index[index_key]:
                self.primary_index[index_key][value] = set()
            self.primary_index[index_key][value].add(entry_id)
    
    def remove_entry(self, model_name:str, field_name:str, value:Any, entry_id:str) -> None:
        """
        Remove an entry ID from the index for a specific field value.
        
        Args:
            model_name: Name of the model class
            field_name: Name of the indexed field
            value: The field value
            entry_id: The entry ID to remove
        """
        index_key = self._get_index_key(model_name, field_name)
        with self.transaction_lock:
            if index_key in self.primary_index and value in self.primary_index[index_key]:
                self.primary_index[index_key][value].discard(entry_id)
                # Clean up empty sets
                if not self.primary_index[index_key][value]:
                    del self.primary_index[index_key][value]
                # Clean up empty field indices
                if not self.primary_index[index_key]:
                    del self.primary_index[index_key]
    
    def update_entry(self, model_name:str, field_name:str, old_value:Any, new_value:Any, entry_id:str) -> None:
        """
        Update an entry in the index when a field value changes.
        
        Args:
            model_name: Name of the model class
            field_name: Name of the indexed field
            old_value: The previous field value
            new_value: The new field value
            entry_id: The entry ID being updated
        """
        if old_value != new_value:
            self.remove_entry(model_name, field_name, old_value, entry_id)
            self.add_entry(model_name, field_name, new_value, entry_id)
    
    def lookup(self, model_name:str, field_name:str, value:Any) -> Set[str]:
        """
        Fast O(1) lookup of entry IDs by indexed field value.
        
        Args:
            model_name: Name of the model class
            field_name: Name of the indexed field
            value: The value to search for
            
        Returns:
            Set of entry IDs that have the given value for the field
        """
        index_key = self._get_index_key(model_name, field_name)
        with self.transaction_lock:
            if index_key in self.primary_index:
                return self.primary_index[index_key].get(value, set()).copy()
        return set()
    
    def lookup_field_values(self, model_name:str, field_name:str) -> dict:
        """
        Get all indexed values for a specific field.
        
        Args:
            model_name: Name of the model class
            field_name: Name of the indexed field
            
        Returns:
            Dict of value -> set of entry IDs
        """
        index_key = self._get_index_key(model_name, field_name)
        with self.transaction_lock:
            if index_key in self.primary_index:
                return {k: v.copy() for k, v in self.primary_index[index_key].items()}
        return {}
    
    def has_field_index(self, model_name:str, field_name:str) -> bool:
        """
        Check if a field has any indexed values.
        
        Args:
            model_name: Name of the model class
            field_name: Name of the field
            
        Returns:
            True if the field has indexed values
        """
        index_key = self._get_index_key(model_name, field_name)
        with self.transaction_lock:
            return index_key in self.primary_index and bool(self.primary_index[index_key])
    
    def clear_field(self, model_name:str, field_name:str) -> None:
        """
        Clear all indexed values for a specific field.
        
        Args:
            model_name: Name of the model class
            field_name: Name of the field
        """
        index_key = self._get_index_key(model_name, field_name)
        with self.transaction_lock:
            if index_key in self.primary_index:
                del self.primary_index[index_key]
    
    def clear_model(self, model_name:str) -> None:
        """
        Clear all indexed fields for a specific model.
        
        Args:
            model_name: Name of the model class
        """
        prefix = f'{model_name}.'
        with self.transaction_lock:
            keys_to_delete = [k for k in self.primary_index if k.startswith(prefix)]
            for key in keys_to_delete:
                del self.primary_index[key]
