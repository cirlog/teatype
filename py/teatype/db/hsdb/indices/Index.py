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
from typing import Dict

# Third-party imports
from teatype.db.hsdb.HSDBField import HSDBField
from teatype.db.hsdb.indices.BaseIndex import BaseIndex
from teatype.db.hsdb.toolbox import transmute_id

class Index(BaseIndex):
    """
    Index that extends BaseIndex with support for HSDBField types.
    Automatically converts HSDBField objects to strings using transmute_id.
    """
    primary_index_key:str
    
    def __init__(self,
                 cache_entries:bool=False,
                 primary_index_key:str='id',
                 max_size:int=None) -> None:
        super().__init__(cache_entries=cache_entries, max_size=max_size)
        self.primary_index_key = primary_index_key
    
    # Override methods to add transmute_id support for HSDBField types
    
    def __contains__(self, entry_id:HSDBField|str) -> bool:
        return super().__contains__(transmute_id(entry_id))

    def __delitem__(self, entry_id:HSDBField|str) -> None:
        super().__delitem__(transmute_id(entry_id))

    def __getitem__(self, entry_id:HSDBField|str) -> dict | None:
        return super().__getitem__(transmute_id(entry_id))

    def __setitem__(self, entry_id:HSDBField|str, entry_data: dict) -> None:
        super().__setitem__(transmute_id(entry_id), entry_data)
        
    def add(self, entry_id:HSDBField|str, entry_data:dict) -> None:
        """
        Add an entry to the index (supports HSDBField and str).
        """
        super().add(transmute_id(entry_id), entry_data)
        
    def fetch(self, entry_id:HSDBField|str) -> dict|None:
        """
        Fetch an entry from the index by its ID (supports HSDBField and str).
        """
        return super().fetch(transmute_id(entry_id))
    
    def remove(self, entry_id:HSDBField|str) -> None:
        """
        Delete an entry from the index by its ID (supports HSDBField and str).
        """
        super().remove(transmute_id(entry_id))
                
    def update(self, entry_data:Dict[HSDBField|str, any]) -> None:
        """
        Update or add entries in the index (supports HSDBField and str keys).
        """
        # Transmute all keys before passing to parent
        transmuted_data = {transmute_id(k): v for k, v in entry_data.items()}
        super().update(transmuted_data)