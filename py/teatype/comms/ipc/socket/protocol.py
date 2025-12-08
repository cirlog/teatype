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
from __future__ import annotations
import argparse
import pickle
import queue
import socket
import threading
import time
from threading import RLock
from typing import Any, Callable, Optional, Tuple

# Third-party imports
from teatype.comms.ipc.socket.envelope import SocketEnvelope
from teatype.logging import *
from teatype.toolkit import generate_id

# Acknowledgment byte sequence sent by server to confirm receipt of size probe
ACKNOWLEDGE_MESSAGE = b'OK'
# Default size for socket read operations (4KB chunks)
DEFAULT_CHUNK_SIZE = 4096
# Default timeout in seconds for queue.get() operations
_DEFAULT_QUEUE_TIMEOUT = 1.0

class FrameBuilder:
    """
    Utility class for constructing protocol-level framing messages.
    
    This class provides static methods to build control frames used in the
    socket communication protocol, including size probes and connection
    termination signals.
    """
    @staticmethod
    def size_probe(envelope:SocketEnvelope, payload_length:int) -> bytes:
        """
        Create a size probe frame to notify the receiver of incoming payload size.
        
        Args:
            envelope: The original envelope being sent
            payload_length: Size of the serialized payload in bytes
            
        Returns:
            Pickled bytes representing the size probe frame
        """
        # Construct a control frame with the payload size in the body
        probe = {
            'header': {
                'content': 'bytes', # Indicates content type
                'method': 'size_of', # Method identifier for size probe
                'id': envelope.id, # Preserve original envelope ID for tracking
                'status': 'pending', # Indicate awaiting acknowledgment
                'receiver': envelope.header['receiver'] # Target receiver name
            },
            'body': payload_length # Actual size information
        }
        # Serialize the probe using pickle for transmission
        return pickle.dumps(probe)

    @staticmethod
    def close_signal(receiver: str) -> bytes:
        """
        Create a graceful connection termination signal.
        
        Args:
            receiver: Name of the connection endpoint to close
            
        Returns:
            Pickled bytes representing the close signal frame
        """
        # Construct a control frame indicating connection closure
        payload = {
            'header': {
                'content': 'string', # Content type for text message
                'method': 'close_socket', # Method identifier for close operation
                'id': generate_id(truncate=12), # Generate unique ID for this frame
                'status': 'closing', # Indicate connection termination state
                'receiver': receiver # Target receiver name
            },
            'body': 'Closing connection' # Human-readable message
        }
        # Serialize the close signal using pickle
        return pickle.dumps(payload)

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
                 queue_timeout:float=_DEFAULT_QUEUE_TIMEOUT,
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

class SocketSession(threading.Thread):
    """
    Manages a single inbound client connection for the server.
    
    Each accepted client connection spawns a dedicated session thread that
    handles the receive loop, frame parsing, and payload dispatching for that
    specific client.
    """
    def __init__(self,
                 server: 'SocketServerWorker',
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

class SocketServerWorker(threading.Thread):
    """
    TCP server that accepts inbound client connections and dispatches messages.
    
    Listens on a configured host:port and spawns a SocketSession thread for
    each accepted client connection. Manages the lifecycle of all active sessions
    and provides a handler callback interface for processing received messages.
    """
    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 handler: Callable[[dict, Tuple[str, int]], None],
                 max_clients: int = 5,
                 backlog: int = 5):
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

def _demo_main() -> None:
    """
    Command-line entry point for running demo server or client.
    
    Parses command-line arguments to determine which demo mode to run
    and with what configuration.
    """
    # Set up argument parser
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

# Module can be run standalone for demonstration purposes
if __name__ == '__main__':
    _demo_main()
