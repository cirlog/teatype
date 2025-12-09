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
import pickle
import socket
import threading
from typing import Optional, Tuple

# Third-party imports
from teatype.comms.ipc.socket.protocol import SocketServerWorker
from teatype.comms.ipc.socket.config import ACKNOWLEDGE_MESSAGE, DEFAULT_CHUNK_SIZE
from teatype.logging import *

class SocketSession(threading.Thread):
    """
    Manages a single inbound client connection for the server.
    
    Each accepted client connection spawns a dedicated session thread that
    handles the receive loop, frame parsing, and payload dispatching for that
    specific client.
    """
    def __init__(self,
                 server:'SocketServerWorker',
                 connection: socket.socket,
                 address: Tuple[str, int]):
        """
        Initialize a new client session.
        
        Args:
            server: Parent server worker managing this session
            connection: Accepted socket connection to the client
            address: Client address tuple (host, port)
        """
        # Initialize as daemon thread
        super().__init__(daemon=True)
        # Store reference to parent server
        self._server = server
        # Store client socket and address
        self._connection = connection
        self._address = address
        # Event for coordinating session shutdown
        self._stop_event = threading.Event()

    def run(self) -> None:
        """
        Main session loop that receives and processes client messages.
        
        Implements the server side of the two-phase protocol:
        1. Receive control frame (size probe or close signal)
        2. Send acknowledgment if size probe
        3. Receive exact payload bytes
        4. Deserialize and dispatch to handler
        """
        try:
            # Continue processing until server signals shutdown
            while not self._server.stop_event.is_set():
                # Phase 1: Read control frame from client
                control_frame = self._receive_frame()
                if control_frame is None:
                    # Connection closed or error - terminate session
                    break
                # Extract method from frame header
                method = control_frame['header'].get('method')
                # Handle graceful close request from client
                if method == 'close_socket':
                    hint(f'Client {self._address} requested close on {self._server.name}')
                    break
                # Validate method is a size probe
                if method != 'size_of':
                    warn(f'Client {self._address} sent unsupported method {method}')
                    continue
                # Extract expected payload size from frame body
                expected_bytes = int(control_frame['body'])
                # Phase 2: Send acknowledgment to client
                self._connection.sendall(ACKNOWLEDGE_MESSAGE)
                # Phase 3: Receive exact number of payload bytes
                payload = self._receive_exact(expected_bytes)
                if payload is None:
                    # Connection closed during payload transfer
                    break
                try:
                    # Phase 4: Deserialize payload from pickle format
                    message = pickle.loads(payload)
                except Exception as exc: # noqa: BLE001
                    # Deserialization failed - log and continue with next message
                    err(f'Failed to deserialize payload from {self._address}: {exc}', traceback=True)
                    continue
                # Dispatch deserialized message to server handler
                self._server.dispatch(message, self._address)
        except ConnectionError as exc:
            # Network error during communication
            warn(f'Connection to {self._address} dropped: {exc}')
        finally:
            # Always clean up connection resources
            self._teardown()

    def stop(self) -> None:
        """
        Signal session to terminate and clean up resources.
        """
        # Set stop event to interrupt receive loop
        self._stop_event.set()
        # Close socket connection
        self._teardown()

    def _receive_frame(self) -> Optional[dict]:
        """
        Receive and deserialize a control frame from the client.
        
        Reads chunks until a complete pickled object is received. Handles
        partial frames by accumulating data across multiple recv() calls.
        
        Returns:
            Deserialized control frame dictionary, or None if connection closed
        """
        # Accumulator for incoming bytes
        buffer = bytearray()
        # Continue reading until complete frame or shutdown
        while not self._server.stop_event.is_set():
            # Read next chunk of data
            chunk = self._connection.recv(DEFAULT_CHUNK_SIZE)
            if not chunk:
                # Empty recv indicates connection closed
                return None
            # Append to buffer
            buffer.extend(chunk)
            try:
                # Attempt to deserialize accumulated data
                return pickle.loads(buffer)
            except (EOFError, pickle.UnpicklingError):
                # Incomplete frame - continue reading more data
                continue

    def _receive_exact(self, expected_bytes: int) -> Optional[bytes]:
        """
        Receive exactly the specified number of bytes from the client.
        
        Handles partial reads by accumulating data until the exact byte count
        is reached. Adjusts chunk size to avoid over-reading.
        
        Args:
            expected_bytes: Exact number of bytes to receive
            
        Returns:
            Complete payload bytes, or None if connection closed
        """
        # Accumulator for payload bytes
        buffer = bytearray()
        # Continue until we have all expected bytes or shutdown
        while len(buffer) < expected_bytes and not self._server.stop_event.is_set():
            # Calculate remaining bytes needed
            remaining = expected_bytes - len(buffer)
            # Read next chunk (limited to remaining bytes needed)
            chunk = self._connection.recv(min(DEFAULT_CHUNK_SIZE, remaining))
            if not chunk:
                # Connection closed before complete payload received
                return None
            # Append to buffer
            buffer.extend(chunk)
        # Convert to immutable bytes
        return bytes(buffer)

    def _teardown(self) -> None:
        """
        Close the client connection and release resources.
        """
        try:
            # Close socket connection
            self._connection.close()
        except OSError:
            # Ignore errors if already closed
            pass