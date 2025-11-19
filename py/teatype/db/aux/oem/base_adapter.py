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

# Local imports

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

# Third-party imports
from teatype.logging import *
    
class BaseAuxilliaryAdapter:
    class _BaseAuxilliaryCursor:
        cursor:object
        
        def __init__(self, cursor:object):
            self.cursor = cursor
        
    _cursor:_BaseAuxilliaryCursor
    db_connection:object
        
    def __init__(self, cursor:object=None, read_only:bool=True):
        self.read_only = read_only
        
        self._cursor = cursor
        self.db_connection = None
       
    @property 
    def cursor(self):
        return self._cursor.cursor