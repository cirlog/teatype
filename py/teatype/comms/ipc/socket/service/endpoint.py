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
from dataclasses import dataclass, field
from typing import Any, Dict, Literal

@dataclass
class SocketEndpoint:
    """
    Configuration container for a socket endpoint.
    
    Holds all necessary connection parameters and behavioral settings for
    both client and server socket endpoints. Used by SocketServiceManager
    to initialize and manage socket workers.
    
    Attributes:
        name: Unique identifier for this endpoint.
        host: IP address or hostname to connect to (client) or bind to (server).
        port: TCP port number.
        mode: Operating mode - 'client' for outgoing connections, 'server' for incoming.
        auto_connect: If True, client connects immediately upon registration.
        auto_reconnect: If True, client automatically reconnects after disconnection.
        queue_size: Maximum number of queued messages for client workers.
        max_clients: Maximum concurrent connections for server workers.
        connect_timeout: Seconds to wait for connection establishment.
        acknowledgement_timeout: Seconds to wait for message acknowledgment.
        metadata: Additional key-value data for application-specific use.
    """
    name:str
    host:str
    port:int
    mode:Literal['client','server']='client'
    auto_connect:bool=True
    auto_reconnect:bool=True
    queue_size:int=10
    max_clients:int=5
    connect_timeout:float=5.0
    acknowledgement_timeout:float=5.0
    metadata:Dict[str,Any]=field(default_factory=dict)
