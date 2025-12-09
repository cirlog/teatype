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
from teatype.db.hsdb import HybridStorage
from teatype.modulo.units.application import ApplicationUnit

class HSDB(ApplicationUnit):
    """
    The main Hybdrid Storage Database application unit. Only one instance should be created per deployment.
    All other HSDB components (like IndexDatabase, RawFileHandler, etc.) should be accessed via this unit.
    All HSDB operations are channeled through this application unit.
    """
    def __init__(self, 
                 host:str='127.0.0.1', 
                 port=9876,
                 *,
                 cold_mode:bool=False) -> None:
        super().__init__('HybridStorageDatabase', backend_host=host, backend_port=port)
        
        self.hybrid_storage = HybridStorage(cold_mode=cold_mode)
        
if __name__ == '__main__':
    hsdb = HSDB(cold_mode=True)