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
from typing import List, Set

# Third-party imports
from teatype.db.hsdb.indices.BaseIndex import BaseIndex

class ModelIndex(BaseIndex):
    """
    Index for fast model-type lookups.
    
    Structure:
        primary_index = {
            "ModelName1": {entry_id1, entry_id2, ...},
            "ModelName2": {entry_id3, entry_id4, ...},
            ...
        }
    
    Provides O(1) lookups for "find all entries of model type X".
    """
    
    def __init__(self,
                 cache_entries:bool=False,
                 max_size:int=None) -> None:
        super().__init__(cache_entries=cache_entries, max_size=max_size)
    
    def register_model(self, model_name:str) -> None:
        """
        Pre-register a model type in the index.
        
        Args:
            model_name: Name of the model class to register
        """
        with self.transaction_lock:
            if model_name not in self.primary_index:
                self.primary_index[model_name] = set()
    
    def register_models(self, models:List[type]) -> None:
        """
        Pre-register multiple model types in the index.
        
        Args:
            models: List of model classes to register
        """
        with self.transaction_lock:
            for model in models:
                model_name = model.__name__
                if model_name not in self.primary_index:
                    self.primary_index[model_name] = set()
    
    def add_entry(self, model_name:str, entry_id:str) -> None:
        """
        Add an entry ID to the model index.
        
        Args:
            model_name: Name of the model class
            entry_id: The entry ID to add
        """
        with self.transaction_lock:
            if model_name not in self.primary_index:
                self.primary_index[model_name] = set()
            self.primary_index[model_name].add(entry_id)
    
    def remove_entry(self, model_name:str, entry_id:str) -> None:
        """
        Remove an entry ID from the model index.
        
        Args:
            model_name: Name of the model class
            entry_id: The entry ID to remove
        """
        with self.transaction_lock:
            if model_name in self.primary_index:
                self.primary_index[model_name].discard(entry_id)
    
    def lookup(self, model_name:str) -> Set[str]:
        """
        Fast O(1) lookup of all entry IDs for a given model type.
        
        Args:
            model_name: Name of the model class
            
        Returns:
            Set of entry IDs for the model type
        """
        with self.transaction_lock:
            return self.primary_index.get(model_name, set()).copy()
    
    def count(self, model_name:str) -> int:
        """
        Get the count of entries for a model type.
        
        Args:
            model_name: Name of the model class
            
        Returns:
            Number of entries for the model
        """
        with self.transaction_lock:
            return len(self.primary_index.get(model_name, set()))
    
    def has_model(self, model_name:str) -> bool:
        """
        Check if a model type is registered in the index.
        
        Args:
            model_name: Name of the model class
            
        Returns:
            True if the model is registered
        """
        with self.transaction_lock:
            return model_name in self.primary_index
    
    def get_all_models(self) -> List[str]:
        """
        Get list of all registered model names.
        
        Returns:
            List of model names
        """
        with self.transaction_lock:
            return list(self.primary_index.keys())
    
    def clear_model(self, model_name:str) -> None:
        """
        Clear all entries for a specific model.
        
        Args:
            model_name: Name of the model class
        """
        with self.transaction_lock:
            if model_name in self.primary_index:
                self.primary_index[model_name] = set()
