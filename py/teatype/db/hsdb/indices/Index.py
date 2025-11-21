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

# Standard-library imports
import threading
# Third-party imports
from teatype.db.hsdb.HSDBField import HSDBField
from teatype.db.hsdb.util import transmute_id

class Index:
    primary_index:dict
    primary_index_key:str
    transaction_lock:threading.Lock
    
    def __init__(self,
                 cache_entries:bool=False,
                 primary_index_key:str='id',
                 max_size:int=None) -> None:
        self.primary_index_key = primary_index_key
        
        self.primary_index = dict()
        self.transaction_lock = threading.Lock()
        
    ##################
    # Dunder Methods #
    ##################
    
    def __contains__(self, entry_id:HSDBField|str) -> bool:
        entry_id = transmute_id(entry_id)
        with self.transaction_lock:
            return entry_id in self.primary_index

    def __copy__(self):
        new_index = Index(self.index_name)
        new_index.primary_index = self.primary_index.copy()
        return new_index

    def __deepcopy__(self, memo):
        new_index = Index(self.index_name)
        new_index.primary_index = {key: value.copy() for key, value in self.primary_index.items()}
        return new_index

    def __delitem__(self, entry_id:HSDBField|str) -> None:
        entry_id = transmute_id(entry_id)
        with self.transaction_lock:
            self.remove(entry_id)

    def __eq__(self, other):
        with self.transaction_lock:
            if not isinstance(other, Index):
                return NotImplemented
            return self.index_name == other.index_name and self.primary_index == other.primary_index

    def __hash__(self):
        with self.transaction_lock:
            return hash((self.index_name, frozenset(self.primary_index.items())))

    def __getitem__(self, entry_id:HSDBField|str) -> dict | None:
        return self.fetch(entry_id)

    def __iter__(self):
        with self.transaction_lock:
            return iter(self.primary_index.values())

    def __len__(self) -> int:
        with self.transaction_lock:
            return len(self.primary_index.keys())

    def __ne__(self, other):
        if not isinstance(other, Index):
            return NotImplemented
        return not self.__eq__(other)

    def __next__(self):
        with self.transaction_lock:
            return next(iter(self.primary_index.items()))

    def __reversed__(self):
        with self.transaction_lock:
            return reversed(self.primary_index.items())

    def __setitem__(self, entry_id:HSDBField|str, entry_data: dict) -> None:
        self.add(entry_id, entry_data)
    
    ##############
    # Properties #
    ##############
    
    @property
    def keys(self) -> list:
        """
        Get all keys in the index.
        """
        with self.transaction_lock:
            return list(self.primary_index.keys())
    
    @property
    def items(self) -> dict:
        """
        Get all items in the index.
        """
        with self.transaction_lock:
            return self.primary_index.items()
    
    @property 
    def values(self) -> dict:
        """
        Get all values in the index.
        """
        with self.transaction_lock:
            return self.primary_index.values()
        
    #################
    # Index Methods #
    #################
        
    def add(self, entry_id:HSDBField|str, entry_data:dict) -> None:
        """
        Add an entry to the index.
        """
        entry_id = transmute_id(entry_id)
        with self.transaction_lock:
            if entry_id in self.primary_index:
                raise KeyError(f'Entry with ID {entry_id} already exists in the index.')
            self.primary_index[entry_id] = entry_data
        
    def clear(self) -> None:
        """
        Clear the entire index.
        """
        self.primary_index.clear()
        
    def fetch(self, entry_id:HSDBField|str) -> dict|None:
        """
        Fetch an entry from the index by its ID.
        """
        entry_id = transmute_id(entry_id)
        with self.transaction_lock:
            if entry_id not in self.primary_index:
                raise KeyError(f'Entry with ID {entry_id} does not exist in the index.')
            return self.primary_index.get(entry_id)
        
    def fetch_all(self) -> dict:
        """
        Get all entries in the index.
        """
        with self.transaction_lock:
            return self.primary_index
    
    def remove(self, entry_id:HSDBField|str) -> None:
        """
        Delete an entry from the index by its ID.
        """
        entry_id = transmute_id(entry_id)
        with self.transaction_lock:
            if self.fetch(entry_id):
                del self.primary_index[entry_id]
            else:
                raise KeyError(f'Entry with ID {entry_id} does not exist in the index.')
                
    def update(self, entry_data:dict) -> None:
        """
        Update an entry in the index.
        """
        with self.transaction_lock:
            for entry_id in entry_data:
                entry = entry_data[entry_id]
                transmuted_id = transmute_id(entry_id)
                
                if transmuted_id in self.primary_index:
                    raise KeyError(f'Entry with ID {transmuted_id} does not exist in the index.')
                
                self.primary_index.update({transmuted_id: entry})