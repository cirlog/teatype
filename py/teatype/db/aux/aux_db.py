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

# Third-party imports
from teatype.db.aux.oem import *
from teatype.logging import *
from teatype.modulo.units.application import ApplicationUnit
    
class AuxilliaryDB(ApplicationUnit):
    oem:object
    
    def __init__(self, oem_name:str, read_only:bool=False):
        if oem_name not in self.available_oems:
            raise ValueError(f'OEM `{oem_name}` is not supported for AuxilliaryDB')
        self.db = self.available_oems.get(oem_name)
        
        self.on_start()

    def __del__(self):
        self.on_shutdown()
    
    ##############
    # Properties #
    ##############
    
    @property
    def available_oems(self):
        return {
            'sqlite3': AuxilliarySQLite3Adapter
        }

    @property
    def query(self):
        pass
    
    #########
    # Hooks #
    #########
    
    def on_start(self):
        warn('No implementation for on_start hook in `AuxilliaryDB`')
    
    def on_shutdown(self):
        warn('No implementation for on_start hook in `AuxilliaryDB`')

if __name__ == '__main__':
    aux_db = AuxilliaryDB('sqlite3')