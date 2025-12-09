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
from teatype.modulo.units.backend import BackendUnit
from teatype.modulo.units.core import CoreUnit
from teatype.modulo.units.service import ServiceUnit
from teatype.modulo.units.socket import SocketUnit

class ApplicationUnit(CoreUnit):
    """
    Composite powerful application unit consisting of backend, service and socket units.
    """
    def __init__(self,
                 name:str,
                 *,
                 backend_host:str='127.0.0.1',
                 backend_port:int=8080):
        self.backend = BackendUnit.create(name=name, host=backend_host, port=backend_port)
        self.service = ServiceUnit.create(name=name)
        self.socket = SocketUnit.create(name=name)
        
    ##############
    # Public API #
    ##############

    def start(self):
        # Start backend and service threads if needed
        self.backend.start()
        self.socket.start()
        self.service.start()
    
    def join(self):
        self.backend.join()
        self.socket.join()
        self.service.join()
    
    def broadcast_message(self, *args, **kwargs):
        return self.service.broadcast(*args, **kwargs)
    
    def dispatch_command(self, *args, **kwargs):
        return self.service.dispatch(*args, **kwargs)