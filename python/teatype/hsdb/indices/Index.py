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
import threading

# From package imports
from teatype.hsdb import HSDBField

class Index:
    primary_index:dict
    primary_index_key:str
    primary_index_transaction_lock:threading.Lock
    
    def __init__(self,
                 cache_entries:bool=False,
                 primary_index_key:str='id',
                 max_size:int=None) -> None:
        self.primary_index_key = primary_index_key
        
        self.primary_index = dict()
        self.primary_index_transaction_lock = threading.Lock()
    
    def __contains__(self, entry_id:str) -> bool:
        with self.primary_index_transaction_lock:
            return entry_id in self.primary_index

    def __copy__(self):
        new_index = Index(self.index_name)
        new_index.primary_index = self.primary_index.copy()
        return new_index

    def __deepcopy__(self, memo):
        new_index = Index(self.index_name)
        new_index.primary_index = {key: value.copy() for key, value in self.primary_index.items()}
        return new_index

    def __delitem__(self, entry_id:str) -> None:
        with self.primary_index_transaction_lock:
            self.remove(entry_id)

    def __eq__(self, other):
        with self.primary_index_transaction_lock:
            if not isinstance(other, Index):
                return NotImplemented
            return self.index_name == other.index_name and self.primary_index == other.primary_index

    def __hash__(self):
        with self.primary_index_transaction_lock:
            return hash((self.index_name, frozenset(self.primary_index.items())))

    def __getitem__(self, entry_id:str) -> dict | None:
        with self.primary_index_transaction_lock:
            return self.fetch(entry_id)

    def __iter__(self):
        with self.primary_index_transaction_lock:
            return iter(self.primary_index.items())

    def __len__(self) -> int:
        with self.primary_index_transaction_lock:
            return len(self.primary_index)

    def __ne__(self, other):
        if not isinstance(other, Index):
            return NotImplemented
        return not self.__eq__(other)

    def __next__(self):
        with self.primary_index_transaction_lock:
            return next(iter(self.primary_index.items()))

    def __reversed__(self):
        with self.primary_index_transaction_lock:
            return reversed(self.primary_index.items())

    def __setitem__(self, entry_id:str, entry_data: dict) -> None:
        with self.primary_index_transaction_lock:
            self.add(entry_id, entry_data)
        
    def add(self, entry_id:str, entry_data:dict) -> None:
        """
        Add an entry to the index.
        """
        with self.primary_index_transaction_lock:
            self.primary_index[entry_id] = entry_data
        
    def clear(self) -> None:
        """
        Clear the entire index.
        """
        self.primary_index.clear()
        
    def fetch(self, entry_id:HSDBField) -> dict|None:
        """
        Fetch an entry from the index by its ID.
        """
        with self.primary_index_transaction_lock:
            if entry_id not in self.primary_index:
                raise KeyError(f'Entry with ID {entry_id} does not exist in the index.')
            return self.primary_index.get(entry_id)
        
    def fetch_all(self) -> dict:
        """
        Get all entries in the index.
        """
        with self.primary_index_transaction_lock:
            return self.primary_index
    
    def remove(self, entry_id:str) -> None:
        """
        Delete an entry from the index by its ID.
        """
        with self.primary_index_transaction_lock:
            if self.fetch(entry_id):
                del self.primary_index[entry_id]
                
    def update(self, entry_id:str, entry_data:dict) -> None:
        """
        Update an entry in the index.
        """
        with self.primary_index_transaction_lock:
            if entry_id in self.primary_index:
                raise KeyError(f'Entry with ID {entry_id} does not exist in the index.')
            self.primary_index[entry_id].update(entry_data)