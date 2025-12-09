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
    actor Caller as C
    participant SocketServiceManager as SSM
    participant SocketClientWorker as SCW
    participant FrameBuilder as FB
    participant SocketServerWorker as SSW
    participant SocketSession as Session
    participant Handler as H
    #
    C -> SSM: send()
    SSM -> SCW: emit(envelope)
    SCW -> FB: size_probe()
    FB --> SCW: probe bytes
    SCW -> SSW: send probe
    SSW -> Session: spawn session
    Session -> SCW: ACK (OK)
    SCW -> SSW: send payload
    Session -> Session: deserialize
    Session -> SSM: handler(payload, addr)
    SSM -> H: invoke handler()
    H --> SSM: return
    Session -> SCW: optional close_signal()
@enduml
"""

if __name__ == '__main__':
    from teatype.logging import *
    
    def _demo_server(host: str, port: int) -> None:
        """
        Run a demonstration socket server that logs received payloads.
        
        Creates and starts a SocketServerWorker with a simple logging handler.
        Runs until interrupted by Ctrl+C.
        
        Args:
            host: Host interface to bind
            port: Port number to listen on
        """
        def handler(message: dict, address: Tuple[str, int]) -> None:
            """Simple handler that logs received messages."""
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

    def _demo_client(host: str, port: int) -> None:
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
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind/connect')
    parser.add_argument('--port', type=int, default=9050, help='Port to bind/connect')
    args = parser.parse_args()

    # Run appropriate demo based on role
    if args.role == 'server':
        _demo_server(args.host, args.port)
    else:
        _demo_client(args.host, args.port)