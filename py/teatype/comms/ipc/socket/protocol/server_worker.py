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
import socket
import threading
from threading import RLock
from typing import Callable, Tuple

# Third-party imports
from teatype.comms.ipc.socket.protocol.session import SocketSession
from teatype.logging import *

class SocketServerWorker(threading.Thread):
    """
    TCP server that accepts inbound client connections and dispatches messages.
    
    Listens on a configured host:port and spawns a SocketSession thread for
    each accepted client connection. Manages the lifecycle of all active sessions
    and provides a handler callback interface for processing received messages.
    """
    def __init__(self,
                 name:str,
                 host:str,
                 port:int,
                 handler:Callable[[dict,Tuple[str,int]],None],
                 max_clients:int=5,
                 backlog:int=5):
        """
        Initialize the socket server worker.
        
        Args:
            name: Server identifier for logging
            host: Local interface to bind (use '0.0.0.0' for all interfaces)
            port: Local port number to listen on
            handler: Callback function to process received messages
            max_clients: Maximum concurrent client sessions (unused currently)
            backlog: TCP listen backlog queue size
        """
        # Initialize as daemon thread
        super().__init__(daemon=True)
        self.name = name
        self.host = host
        self.port = port
        # Store message handler callback
        self._handler = handler
        self._max_clients = max_clients
        # Create TCP socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow immediate reuse of address (prevents "Address already in use" errors)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to specified host and port
        self._server_socket.bind((self.host, self.port))
        # Start listening with specified backlog queue size
        self._server_socket.listen(backlog)
        # Event for coordinating server shutdown
        self.stop_event = threading.Event()
        # Track all active client sessions
        self._sessions: set[SocketSession] = set()
        # Lock to protect sessions set from concurrent access
        self._lock = RLock()
        log(f'Socket server [{self.name}] listening on {self.host}:{self.port}')

    def run(self) -> None:
        """
        Main server loop that accepts incoming client connections.
        
        Continuously accepts new connections and spawns a SocketSession thread
        for each client. Runs until stop_event is set.
        """
        # Continue accepting connections until shutdown
        while not self.stop_event.is_set():
            try:
                # Block waiting for next client connection
                client_socket, address = self._server_socket.accept()
                # Create session thread to handle this client
                session = SocketSession(self, client_socket, address)
                # Start session thread
                session.start()
                # Add to active sessions set (thread-safe)
                with self._lock:
                    self._sessions.add(session)
                log(f'Socket server [{self.name}] accepted connection from {address}')
            except OSError:
                # Check if error due to shutdown
                if self.stop_event.is_set():
                    # Normal shutdown path
                    break
                # Unexpected error during accept
                err(f'Socket server [{self.name}] failed to accept connection', traceback=True)

    def stop(self) -> None:
        """
        Initiate server shutdown and close all client connections.
        
        Stops accepting new connections, signals all active sessions to terminate,
        and cleans up resources.
        """
        # Signal main accept loop to terminate
        self.stop_event.set()
        try:
            # Shutdown server socket to unblock accept()
            self._server_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            # May fail if already closed - ignore
            pass
        finally:
            # Close server socket
            self._server_socket.close()
        # Stop all active client sessions
        with self._lock:
            # Create list copy to avoid modification during iteration
            for session in list(self._sessions):
                session.stop()
            # Clear sessions set
            self._sessions.clear()
        log(f'Socket server [{self.name}] stopped')

    def dispatch(self, message: dict, address: Tuple[str, int]) -> None:
        """
        Invoke the registered handler callback with a received message.
        
        Args:
            message: Deserialized message dictionary from client
            address: Source address tuple (host, port) of the sender
        """
        try:
            # Invoke user-provided handler
            self._handler(message, address)
        except Exception as exc:  # noqa: BLE001
            # Handler raised exception - log but don't crash session
            err(f'Socket server [{self.name}] handler failure: {exc}', traceback=True)