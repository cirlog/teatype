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

# Local imports

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
import sqlite3

# Third-party imports
from teatype.db.aux.oem.base_adapter import BaseAuxilliaryAdapter
from teatype.io import path
from teatype.logging import *
    
class AuxilliarySQLite3Adapter(BaseAuxilliaryAdapter):
    def __init__(self, database_path:str, read_only:bool=True):
        super().__init__(read_only=read_only)
        
        try:
            if read_only:
                uri = f'file:{database_path}?mode=ro'
                self.db_connection = sqlite3.connect(uri, uri=True)
            else:
                self.db_connection = sqlite3.connect(database_path)
                
            self.db_connection = sqlite3.connect(database_path)
            self.db_connection.row_factory = sqlite3.Row  # This allows accessing columns by name
            self.cursor = self.db_connection.cursor()
            
             # Performance PRAGMAs for read-heavy queries
            self.db_connection.execute('PRAGMA journal_mode = OFF;')
            self.db_connection.execute('PRAGMA synchronous = OFF;')
            self.db_connection.execute('PRAGMA temp_store = MEMORY;')
            self.db_connection.execute('PRAGMA mmap_size = 268435456;')  # 256MB memory map
            
            success(f'Successfully connected to the database at "{database_path}".')
        except sqlite3.Error as e:
            err(f'Database connection error: {e}')
            self.db_connection = None
            self.cursor = None

    def __del__(self):
        """
        Closes the database connection when the object is destroyed.
        """
        if self.db_connection:
            self.db_connection.close()
            
    @property
    def query(self):
        return BaseAuxilliaryAdapter._BaseAuxilliaryCursor(self.cursor)