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
from typing import List

# From package imports
from teatype.hsdb.indices import BaseIndex

"""
Following structure for different relation types:
    one-to-one:
        primary_index: {
            relation_name: {
                primary_key[str]: secondary_key[str]
            }
        }
        reverse_index: {
            relation_name: {
                secondary_key[str]: primary_key[str]
            }
        }
        
    many-to-one:
        primary_index: {
            relation_name: {
                primary_key[str]: secondary_key[str]
            }
        }
        reverse_index: {
            relation_name: {
                secondary_key[str]: [primary_key[str]]
            }
        }
    
    many-to-many:
        primary_index: {
            relation_name: {
                primary_keys: [primary_key[str]],
                secondary_keys: [secondary_key[str]]
            }
        }
        reverse_index: None

Info:
    relation_name consists of <primary_model>_<relation_type>_<secondary_model>
"""
class RelationalIndex(BaseIndex):
    reverse_index:dict
    
    def __init__(self,
                 cache_entries:bool=False,
                 max_size:int=None) -> None:
        super().__init__(cache_entries, max_size)
        
        self.reverse_index = dict()
        
    def add(self,
            relation_name:str,
            reverse_relation_name:str,
            relation_type:str,
            primary_keys:str,
            secondary_keys:List[str]=[]) -> None:
        """
        Add an entry to the index.
        """
        with self.transaction_lock:
            if relation_name not in self.primary_index:
                self.primary_index[relation_name] = {}
                
            if relation_type == 'one-to-one' or relation_type == 'many-to-one':
                if reverse_relation_name not in self.reverse_index:
                    self.reverse_index[reverse_relation_name] = {}
                    
                primary_key = primary_keys[0]
                secondary_key = secondary_keys[0]
                if relation_type == 'one-to-one':
                    self.primary_index[relation_name][primary_key] = secondary_key
                    self.reverse_index[reverse_relation_name][secondary_key] = primary_key
                else:
                    
                    self.primary_index[relation_name][primary_key] = secondary_key
                    if secondary_key not in self.reverse_index[reverse_relation_name]:
                        self.reverse_index[reverse_relation_name][secondary_key] = []
                    self.reverse_index[reverse_relation_name][secondary_key].append(primary_key)
            else:
                self.primary_index[relation_name]['primary_keys'] = [primary_keys]
                self.primary_index[relation_name]['secondary_keys'] = secondary_keys
        
    def clear(self, relation_name:str=None, reverse_lookup:bool=False) -> None:
        """
        Clear the entire index.
        """
        if reverse_lookup:
            target_index = self.reverse_index[relation_name]
        else:
            target_index = self.primary_index[relation_name]
        
        with self.transaction_lock:
            if relation_name is None:
                target_index.clear()
            else:
                target_index[relation_name].clear()
        
    def fetch(self, relation_name:str, target_id:str, reverse_lookup:bool=False) -> dict|None:
        """
        Fetch an entry from the index by its ID.
        """
        if reverse_lookup:
            target_index = self.reverse_index[relation_name]
        else:
            target_index = self.primary_index[relation_name]
        
        with self.transaction_lock:
            return target_index.get(target_id)
        
    def fetch_all(self, relation_name:str, reverse_lookup:bool=False) -> dict:
        """
        Get all entries in the index.
        """
        if reverse_lookup:
            target_index = self.reverse_index[relation_name]
        else:
            target_index = self.primary_index[relation_name]
            
        with self.transaction_lock:
            if relation_name is None:
                return target_index
            return target_index[relation_name]
    
    def remove(self, relation_name:str, target_id:str, reverse_lookup:bool=False) -> dict|None:
        """
        Delete an entry from the index by its ID.
        """
        if reverse_lookup:
            target_index = self.reverse_index[relation_name]
        else:
            target_index = self.primary_index[relation_name]
            
        with self.transaction_lock:
            if self.fetch(relation_name, target_id, reverse_lookup) is None:
                raise KeyError(f'Entry with ID {target_id} does not exist in the index.')
            del target_index[relation_name][target_id]