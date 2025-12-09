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
    actor Unit
    participant SocketUnit
    participant SocketServiceManager as Manager
    participant SocketClientWorker as Client
    participant FrameBuilder
    participant RemoteServer as Server

    Unit -> SocketUnit: send_socket_message(receiver, header, body)
    SocketUnit -> Manager: send()
    Manager -> Client: emit(envelope)
    Client -> FrameBuilder: size_probe(envelope,len(payload))
    FrameBuilder --> Client: pickled probe
    Client -> Server: send probe
    Server --> Client: ACK (OK)
    Client -> Server: send payload bytes
    note right of Client: handles retries/logging\nand reconnection failures
@enduml
"""

"""
@startuml
    participant RemoteClient as Client
    participant SocketServerWorker as Server
    participant SocketSession as Session
    participant SocketServiceManager as Manager
    participant Handler
    note over Server,Session: Server created via\nregister_socket_server()

    Client -> Server: connect + size_probe
    Server -> Session: spawn session thread
    Session -> Client: ACK (OK)
    Client -> Session: payload bytes
    Session -> Session: pickle.loads → message
    Session -> Manager: handler(payload, address)
    Manager -> Handler: call @socket_handler(...)
    Handler --> Manager: business logic
    Session -> Client: optional close_signal()
@enduml
"""

# From local imports
from .config import *
from .envelope import SocketEnvelope