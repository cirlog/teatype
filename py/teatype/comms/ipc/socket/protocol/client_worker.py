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
import queue
import socket
import threading
from typing import Any, Callable, Optional

# Third-party imports
from teatype.comms.ipc.socket.envelope import SocketEnvelope
from teatype.comms.ipc.socket.config import ACKNOWLEDGE_MESSAGE, DEFAULT_CHUNK_SIZE, DEFAULT_QUEUE_TIMEOUT
from teatype.comms.ipc.socket.protocol.frame_builder import FrameBuilder
from teatype.logging import *

class SocketClientWorker(threading.Thread):
    """
    Asynchronous socket client worker that manages outbound connections.
    
    This thread-based worker handles a single persistent connection to a server,
    processing outbound messages from a queue and managing reconnection logic.
    Messages are sent using a two-phase protocol: size probe followed by payload.
    """
    # Client identifier name
    name: str
    # Target server hostname
    host: str
    # Target server port number
    port: int
    # Timeout for initial connection attempt
    connect_timeout: float
    # Timeout for waiting on acknowledgment messages
    acknowledge_timeout: float
    # Thread-safe queue holding outbound messages
    _outbox: queue.Queue[Any]
    # Timeout for queue.get() operations
    _queue_timeout: float
    # Active socket connection (None when disconnected)
    _socket: Optional[socket.socket]
    # Event to signal thread shutdown
    _stop_event: threading.Event
    # Boolean tracking current connection state
    _connected: bool
    # Optional callback invoked on disconnection
    _disconnect_callback: Optional[Callable[[str,Optional[BaseException]],None]]
    # Flag indicating if close was explicitly requested
    _close_requested: bool
    
    def __init__(self,
                 name:str,
                 host:str,
                 port:int,
                 queue_size:int=10,
                 queue_timeout:float=DEFAULT_QUEUE_TIMEOUT,
                 connect_timeout:float=5.0,
                 acknowledge_timeout:float=5.0,
                 on_disconnect:Optional[Callable[[str,Optional[BaseException]],None]]=None):
        """
        Initialize the socket client worker.
        
        Args:
            name: Identifier for this client instance
            host: Server hostname or IP address
            port: Server port number
            queue_size: Maximum number of queued outbound messages
            queue_timeout: Timeout in seconds for queue operations
            connect_timeout: Socket connection timeout in seconds
            acknowledge_timeout: Timeout for receiving ACK from server
            on_disconnect: Optional callback executed when disconnected
        """
        # Initialize as daemon thread (terminates with main program)
        super().__init__(daemon=True)
        self.name = name
        self.host = host
        self.port = port
        self.connect_timeout = connect_timeout
        self.acknowledge_timeout = acknowledge_timeout
        # Create bounded queue for outbound messages to prevent memory overflow
        self._outbox:queue.Queue[Any] = queue.Queue(maxsize=queue_size)
        self._queue_timeout = queue_timeout
        # Socket starts as None until connection is established
        self._socket:Optional[socket.socket] = None
        # Create event for coordinating thread shutdown
        self._stop_event = threading.Event()
        # Track connection state
        self._connected = False
        self._disconnect_callback = on_disconnect
        self._close_requested = False

    # Public API
    def connect(self) -> bool:
        """
        Establish TCP connection to the configured server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create blocking TCP socket with connection timeout
            self._socket = socket.create_connection((self.host, self.port), timeout=self.connect_timeout)
            # Set socket timeout for subsequent recv operations (waiting for ACK)
            self._socket.settimeout(self.acknowledge_timeout)
            # Disable Nagle's algorithm to reduce latency for small messages
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            # Mark connection as established
            self._connected = True
            log(f'Socket client [{self.name}] connected to {self.host}:{self.port}')
            return True
        except OSError as exc:
            # Connection failed (host unreachable, timeout, etc.)
            warn(f'Socket client [{self.name}] failed to connect: {exc}')
            self._connected = False
            self._socket = None
            return False

    def emit(self, envelope: SocketEnvelope, block: bool = True) -> bool:
        """
        Queue an envelope for transmission to the server.
        
        Args:
            envelope: Message envelope to send
            block: Whether to block if queue is full
            
        Returns:
            True if message was queued, False if rejected
        """
        # Verify connection before accepting messages
        if not self._connected:
            warn(f'Socket client [{self.name}] is not connected; dropping message')
            return False
        try:
            # Attempt to add envelope to outbound queue
            self._outbox.put(envelope, block=block, timeout=self._queue_timeout if block else None)
            return True
        except queue.Full:
            # Queue at capacity - reject message to prevent blocking caller
            warn(f'Socket client [{self.name}] queue is full; message rejected')
            return False

    def close(self, graceful: bool = True) -> None:
        """
        Initiate client shutdown and connection closure.
        
        Args:
            graceful: If True, send close signal before disconnecting
        """
        # If graceful shutdown requested and connection is active
        if graceful and self._connected:
            try:
                # Queue a close signal frame for the server
                self._outbox.put_nowait(FrameBuilder.close_signal(self.name))
            except queue.Full:
                # Queue full - fall back to immediate closure
                warn(f'Socket client [{self.name}] close signal dropped (queue full)')
                self._close_socket_immediately()
        else:
            # Immediate ungraceful shutdown
            self._close_socket_immediately()
        # Signal the worker thread to terminate
        self._stop_event.set()

    def is_connected(self) -> bool:
        """
        Check current connection status.
        
        Returns:
            True if connected to server, False otherwise
        """
        return self._connected

    def run(self) -> None:
        """
        Main worker thread loop that processes outbound messages.
        
        Continuously retrieves messages from the queue and sends them using
        the two-phase protocol: size probe + acknowledgment + payload.
        """
        # Continue processing until stop event is set
        while not self._stop_event.is_set():
            try:
                # Wait for next outbound message with timeout
                payload = self._outbox.get(timeout=self._queue_timeout)
            except queue.Empty:
                # No messages available - check if connection is still alive
                if not self._check_connection_state():
                    # Connection lost - terminate worker
                    break
                # Connection OK - continue waiting for messages
                continue

            # Check if payload is a pre-serialized close signal
            if isinstance(payload, bytes):
                # Close signal already serialized by FrameBuilder
                self._send_raw(payload)
                # Exit loop after sending close signal
                break

            # Validate payload type
            if not isinstance(payload, SocketEnvelope):
                warn(f'Socket client [{self.name}] received unsupported payload type {type(payload)}')
                continue

            try:
                # Ensure envelope has proper receiver metadata
                payload.normalize(receiver=self.name)
                # Serialize envelope to bytes
                serialized_payload = payload.serialize()
                # Phase 1: Send size probe to notify server of incoming payload size
                probe = FrameBuilder.size_probe(payload, len(serialized_payload))
                self._send_raw(probe)
                # Phase 2: Wait for acknowledgment from server
                ack = self._safe_recv()
                if ack != ACKNOWLEDGE_MESSAGE:
                    # Server sent unexpected response - abort
                    raise ConnectionError(f'Unexpected ACK {ack!r}')
                # Phase 3: Send actual payload data
                self._send_raw(serialized_payload)
                log(f'Socket client [{self.name}] shipped request {payload.id}')
            except Exception as exc:  # noqa: BLE001
                # Any error during send terminates the connection
                err(f'Socket client [{self.name}] send failure: {exc}', traceback=True)
                break

        # Clean up socket resources before thread exits
        self._close_socket_immediately()
        # Notify callback of disconnection if registered
        if self._disconnect_callback:
            self._disconnect_callback(self.name, None)

    # Internals
    def _send_raw(self, data: bytes) -> None:
        """
        Send raw bytes over the socket with blocking I/O.
        
        Args:
            data: Byte data to transmit
            
        Raises:
            ConnectionError: If socket is not connected
        """
        # Verify socket is available
        if not self._socket:
            raise ConnectionError('Socket is not connected')
        # Send all data (blocks until complete or error)
        self._socket.sendall(data)

    def _safe_recv(self) -> bytes:
        """
        Receive data from socket with error checking.
        
        Returns:
            Received byte data
            
        Raises:
            ConnectionError: If socket is not connected
        """
        # Verify socket is available
        if not self._socket:
            raise ConnectionError('Socket is not connected')
        # Read up to DEFAULT_CHUNK_SIZE bytes (blocks until data available)
        return self._socket.recv(DEFAULT_CHUNK_SIZE)

    def _check_connection_state(self) -> bool:
        """
        Non-blocking check to verify socket connection is still alive.
        
        Uses MSG_PEEK and MSG_DONTWAIT flags to check for data without blocking
        or consuming it from the receive buffer.
        
        Returns:
            True if connection is alive, False if closed or broken
        """
        # Verify socket exists and connected flag is set
        if not self._socket or not self._connected:
            return False
        try:
            # Attempt to peek at 1 byte without blocking or consuming it
            self._socket.recv(1, socket.MSG_PEEK | socket.MSG_DONTWAIT)
        except BlockingIOError:
            # No data available but connection is alive
            return True
        except OSError:
            # Connection closed by peer or other error
            warn(f'Socket client [{self.name}] connection closed by peer')
            return False
        # If recv() returns normally, connection is alive
        return True

    def _close_socket_immediately(self) -> None:
        """
        Forcefully close the socket connection and clean up resources.
        
        Attempts graceful shutdown first, then closes the socket handle.
        Updates connection state flags.
        """
        if self._socket:
            try:
                # Attempt graceful shutdown (disable send/receive)
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                # Shutdown may fail if already closed - ignore
                pass
            finally:
                # Close socket handle and release OS resources
                self._socket.close()
        # Update state flags
        self._connected = False
        self._socket = None