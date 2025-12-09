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

if __name__ == '__main__':
    import argparse
    import time
    from typing import Tuple
    from teatype.logging import *
    from teatype.comms.ipc.socket.protocol import SocketServerWorker, SocketClientWorker, SocketEnvelope
    
    def _demo_server(host:str, port:int) -> None:
        """
        Run a demonstration socket server that logs received payloads.
        
        Creates and starts a SocketServerWorker with a simple logging handler.
        Runs until interrupted by Ctrl+C.
        
        Args:
            host: Host interface to bind
            port: Port number to listen on
        """
        def handler(message:dict, address:Tuple[str,int]) -> None:
            """
            Simple handler that logs received messages.
            """
            log(f'[server] Received payload from {address}: {message}')

        # Create and start server worker
        server = SocketServerWorker('demo-server', host, port, handler)
        server.start()
        log(f'Demo server ready on {host}:{port}. Press Ctrl+C to stop.')
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # User requested shutdown
            log('Stopping demo server ...')
        finally:
            # Clean shutdown
            server.stop()
            # Wait for server thread to terminate
            server.join(timeout=2)

    def _demo_client(host:str, port:int) -> None:
        """
        Run a demonstration socket client that sends a sample message.
        
        Creates a SocketClientWorker, connects to the server, sends one test
        envelope, and performs graceful shutdown.
        
        Args:
            host: Server hostname to connect to
            port: Server port to connect to
        """
        # Create client worker (reuses server name for demo simplicity)
        client = SocketClientWorker('demo-server', host, port)
        # Attempt to connect to server
        if not client.connect():
            err('Demo client failed to connect to server')
            return
        # Start client worker thread
        client.start()

        # Create sample envelope with test payload
        envelope = SocketEnvelope(
            header={'receiver': 'demo-server', 'method': 'payload'},
            body={'message': 'Hello from SocketClientWorker!', 'timestamp': time.time()}
        )
        # Queue envelope for transmission
        client.emit(envelope)
        # Wait for message to be sent
        time.sleep(1)
        # Initiate graceful shutdown
        client.close(graceful=True)
        # Wait for client thread to terminate
        client.join(timeout=2)
        log('Demo client finished')

    parser = argparse.ArgumentParser(description='Socket protocol demo runner')
    parser.add_argument('role', choices=['server', 'client'], help='Which demo to run')
    args = parser.parse_args()

    # Run appropriate demo based on role
    if args.role == 'server':
        _demo_server('localhost', 9050)
    else:
        _demo_client('localhost', 9051)