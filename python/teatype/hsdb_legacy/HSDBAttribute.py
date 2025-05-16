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

# From package imports
from teatype.hsdb_legacy import HSDBRelation

class HSDBAttribute:
    # editable:bool
    # TODO: indexed:bool
    key:str
    # TODO: max_size:int
    # required:bool
    # relation:HSDBRelation
    # unique:bool
    value:any
    
    def __init__(self,
                 key:str,
                 editable:bool=True,
                 indexed:bool=False,
                 max_size:int=None,
                 relation:HSDBRelation=None,
                 required:bool=False,
                 searchable:bool=False,
                 unique:bool=False):
        self.key = key
        
        self.editable = editable
        self.indexed = indexed
        self.max_size = max_size
        self.editable = editable
        self.relation = relation
        self.required = required
        self.searchable = searchable
        self.unique = unique
        
    def setValue(self, value:any):
        self.value = value
        
    def getValue(self) -> any:
        return self.value