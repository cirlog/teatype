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

"""
@startuml
skinparam packageStyle rectangle
package "Socket Service" {
    class SocketServiceManager {
        +register_client()
        +register_server()
        +register_handler()
        +send()
        +disconnect_client()
        +is_connected()
        +shutdown()
        -_connect_client()
        -_start_server()
        -_emit()
        -_schedule_reconnect()
    }

    class SocketEndpoint {
        name
        host
        port
        mode
        auto_connect
        auto_reconnect
        queue_size
        max_clients
        connect_timeout
        acknowledgement_timeout
        metadata
    }

    class SocketClientWorker
    class SocketServerWorker
}

SocketServiceManager "1" o-- "*" SocketEndpoint : _client_configs/_server_configs
SocketServiceManager "1" o-- "*" SocketClientWorker : _client_workers
SocketServiceManager "1" o-- "*" SocketServerWorker : _server_workers
SocketServiceManager ..> SocketEnvelope : creates
SocketServiceManager ..> "handler functions" : _handlers\n(endpoint→callable)
@enduml
"""

# From local imports
from .endpoint import SocketEndpoint
from .handler import socket_handler
from .service_manager import SocketServiceManager