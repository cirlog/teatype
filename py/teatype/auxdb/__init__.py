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
# Copyright (c) 2024-2025 enamentis GmbH. All rights reserved.
#
# This software module is the proprietary property of enamentis GmbH.
# Unauthorized copying, modification, distribution, or use of this software
# is strictly prohibited unless explicitly authorized in writing.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THIS SOFTWARE.
# 
# For more details, check the LICENSE file in the root directory of this repository.

# System imports
import sqlite3

# From package imports
from teatype.io import path
from teatype.logging import *
    
class AuxilliaryOEM:
    def __init__(self, database_file=None, readonly:bool=True):
        """
        Initializes the database connection.
        """
        try:
            if readonly:
                uri = f'file:{database_file}?mode=ro'
                self.db_connection = sqlite3.connect(uri, uri=True)
            else:
                self.db_connection = sqlite3.connect(database_file)
                
            self.db_connection = sqlite3.connect(database_file)
            self.db_connection.row_factory = sqlite3.Row  # This allows accessing columns by name
            self.cursor = self.db_connection.cursor()
            
             # Performance PRAGMAs for read-heavy queries
            self.db_connection.execute("PRAGMA journal_mode = OFF;")
            self.db_connection.execute("PRAGMA synchronous = OFF;")
            self.db_connection.execute("PRAGMA temp_store = MEMORY;")
            self.db_connection.execute("PRAGMA mmap_size = 268435456;")  # 256MB memory map
            
            print(f'Successfully connected to the database at "{database_file}".')
        except sqlite3.Error as e:
            print(f'Database connection error: {e}')
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
        return AuxilliaryOEM._AuxilliaryCursor(self.cursor)

    class _AuxilliaryCursor:
        def __init__(self, cursor):
            self.cursor = cursor