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
import inspect
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional

# Third-party imports
from teatype.comms.ipc.socket.envelope import SocketEnvelope
from teatype.comms.ipc.socket.protocol import SocketClientWorker, SocketServerWorker
from teatype.logging import *

def socket_handler(endpoint:Optional[str]=None):
    """
    Decorator used by units to register socket handlers.
    
    This decorator marks methods as socket message handlers for specific endpoints.
    When applied to a method, it tags the function with metadata that the
    SocketServiceManager can discover during autowiring.
    
    Args:
        endpoint: The endpoint name to handle. If None, defaults to '*' (all endpoints).
    
    Returns:
        The decorated function with added metadata.
    
    Example:
        @socket_handler('data_channel')
        def handle_data(self, envelope, **kwargs):
            pass
    """
    def decorator(function: Callable):
        # Store the endpoint target as metadata on the function object
        # This allows autowire() to discover which endpoints this handler services
        setattr(function, '_socket_handler_target', endpoint or '*')
        return function
    return decorator

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

class SocketServiceManager:
    """
    High-level socket orchestration utilities.
    Coordinates socket clients and servers for Modulo units.
    
    This manager provides a unified interface for managing multiple socket
    connections (both client and server) within an application. It handles
    automatic reconnection, message routing, and handler registration.
    
    Thread-safe operations are guaranteed through internal locking mechanisms.
    """
    _client_configs:Dict[str,SocketEndpoint] # Maps client names to their configurations
    _client_workers:Dict[str,SocketClientWorker] # Active client worker instances
    _handlers:Dict[str,List[Callable]] # Maps endpoint names to handler functions
    _lock:threading.RLock # Reentrant lock for thread-safe access to shared state
    _server_configs:Dict[str,SocketEndpoint] # Maps server names to their configurations
    _server_workers:Dict[str,SocketServerWorker] # Active server worker instances
    _shutdown_event:threading.Event # Signals when the manager is shutting down
    _verbose:bool # Controls detailed logging output
    client_name: str # Identifier for this service manager instance
    
    def __init__(self,
                 client_name:Optional[str]=None,
                 owner:Optional[object]=None,
                 verbose_logging:Optional[bool] = False) -> None:
        """
        Initialize the socket service manager.
        
        Args:
            client_name: Identifier for this manager, used in message source fields.
            owner: Object to scan for @socket_handler decorated methods.
            verbose_logging: Enable detailed debug logging if True.
        """
        # Set the client name for identifying this manager in message metadata
        self.client_name = client_name or 'teatype.socket.service'
        
        # Initialize empty dictionaries for tracking configurations and workers
        self._client_configs = {}
        self._server_configs = {}
        self._client_workers = {}
        self._server_workers = {}
        self._handlers = {}
        
        # Create a reentrant lock to allow the same thread to acquire multiple times
        self._lock = threading.RLock()
        
        # Event flag to coordinate graceful shutdown across all threads
        self._shutdown_event = threading.Event()
        
        # Store verbosity preference for conditional logging
        self._verbose = verbose_logging

        # If an owner object is provided, automatically discover and register handlers
        if owner:
            self.autowire(owner)

    # Registration
    def register_client(self,
                        name:str,
                        host:str,
                        port:int,
                        *,
                        auto_connect:bool=True,
                        auto_reconnect:bool=True,
                        queue_size:int=10,
                        connect_timeout:float=5.0,
                        acknowledge_timeout:float=5.0) -> SocketEndpoint:
        """
        Register a new socket client endpoint.
        
        Creates a client configuration and optionally initiates an immediate
        connection. The client will automatically handle reconnection if configured.
        
        Args:
            name: Unique identifier for this client.
            host: Target server hostname or IP address.
            port: Target server port number.
            auto_connect: Connect immediately if True.
            auto_reconnect: Enable automatic reconnection on disconnect if True.
            queue_size: Maximum messages to queue before blocking.
            connect_timeout: Seconds to wait for connection before failing.
            acknowledge_timeout: Seconds to wait for message acknowledgment.
        
        Returns:
            The created SocketEndpoint configuration object.
        """
        # Create the endpoint configuration with all provided parameters
        endpoint = SocketEndpoint(name=name,
                                  host=host,
                                  port=port,
                                  mode='client',
                                  auto_connect=auto_connect,
                                  auto_reconnect=auto_reconnect,
                                  queue_size=queue_size,
                                  connect_timeout=connect_timeout,
                                  acknowledge_timeout=acknowledge_timeout)
        
        # Store the configuration in a thread-safe manner
        with self._lock:
            self._client_configs[name] = endpoint
        
        # If auto_connect is enabled, immediately attempt connection
        if auto_connect:
            self._connect_client(name)
        
        return endpoint

    def register_server(self,
                        name:str,
                        host:str,
                        port:int,
                        *,
                        max_clients:int=5) -> SocketEndpoint:
        """
        Register and start a new socket server endpoint.
        
        Creates a server configuration and immediately starts listening for
        incoming connections on the specified host and port.
        
        Args:
            name: Unique identifier for this server.
            host: Interface to bind to ('0.0.0.0' for all interfaces).
            port: Port number to listen on.
            max_clients: Maximum number of simultaneous client connections.
        
        Returns:
            The created SocketEndpoint configuration object.
        """
        # Create the server endpoint configuration
        endpoint = SocketEndpoint(name=name,
                                  host=host,
                                  port=port,
                                  mode='server',
                                  max_clients=max_clients)
        
        # Store the configuration atomically
        with self._lock:
            self._server_configs[name] = endpoint
        
        # Immediately start the server worker thread
        self._start_server(endpoint)
        return endpoint

    def register_handler(self, endpoint:str, handler:Callable) -> None:
        """
        Register a callback function to handle messages for an endpoint.
        
        Handlers are invoked when messages arrive for the specified endpoint.
        Multiple handlers can be registered for the same endpoint and all will
        be called in registration order.
        
        Args:
            endpoint: Endpoint name to handle, or '*' for all endpoints.
            handler: Callable that accepts (envelope, client_address, endpoint).
        """
        # Add the handler to the endpoint's handler list, creating the list if needed
        with self._lock:
            self._handlers.setdefault(endpoint, []).append(handler)
        
        # Log registration if verbose mode is enabled
        if self._verbose:
            log(f'Registered socket handler for endpoint {endpoint}')

    def autowire(self, owner:object) -> None:
        """
        Automatically discover and register handler methods on an object.
        
        Scans the owner object for methods decorated with @socket_handler
        and registers them as message handlers for their designated endpoints.
        
        Args:
            owner: Object to scan for decorated handler methods.
        """
        # Iterate through all methods of the owner object
        for _, member in inspect.getmembers(owner, predicate=inspect.ismethod):
            # Check if the method has the socket handler decorator metadata
            endpoint = getattr(member, '_socket_handler_target', None)
            if endpoint:
                # Register the method as a handler for the discovered endpoint
                self.register_handler(endpoint, member)

    # Client control
    def send(self,
             receiver:str,
             header:Optional[Dict[str,Any]]=None,
             body:Any=None,
             *,
             block:bool=True) -> bool:
        """
        Send a message to a connected client endpoint.
        
        Constructs a SocketEnvelope with the provided data and sends it through
        the specified client worker. The message is automatically normalized
        with source and receiver metadata.
        
        Args:
            receiver: Name of the registered client to send through.
            header: Optional dictionary of message metadata.
            body: Message payload (any serializable data).
            block: If True, blocks until message is queued; if False, fails immediately if queue is full.
        
        Returns:
            True if message was successfully queued, False otherwise.
        """
        # Look up the worker instance for the named receiver
        worker = self._client_workers.get(receiver)
        if not worker:
            # Log warning and fail if no worker exists with that name
            warn(f'No socket client named {receiver} is connected')
            return False
        
        # Construct the message envelope with header and body
        envelope = SocketEnvelope(header=header or {}, body=body)
        
        # Populate metadata fields with source and receiver information
        envelope.normalize(receiver=receiver, source=self.client_name)
        
        # Delegate actual transmission to the worker's emit method
        return worker.emit(envelope, block=block)

    def disconnect_client(self, receiver:str, graceful:bool=True) -> None:
        """
        Disconnect and remove a client worker.
        
        Closes the connection to the specified client and removes it from
        the active workers. Auto-reconnect will not trigger after manual disconnect.
        
        Args:
            receiver: Name of the client to disconnect.
            graceful: If True, flushes pending messages before closing.
        """
        # Retrieve the worker instance
        worker = self._client_workers.get(receiver)
        if not worker:
            return
        
        # Close the connection (gracefully if requested)
        worker.close(graceful=graceful)
        
        # Wait up to 2 seconds for the worker thread to terminate
        worker.join(timeout=2)
        
        # Remove the worker from the active workers dictionary
        with self._lock:
            self._client_workers.pop(receiver, None)

    def is_connected(self, receiver:str) -> bool:
        """
        Check if a client is currently connected.
        
        Args:
            receiver: Name of the client to check.
        
        Returns:
            True if the client exists and is connected, False otherwise.
        """
        # Look up the worker and check its connection status
        worker = self._client_workers.get(receiver)
        return bool(worker and worker.is_connected())

    # Server control
    def _start_server(self, endpoint:SocketEndpoint) -> None:
        """
        Internal method to create and start a server worker.
        
        Creates a handler function that wraps incoming messages into envelopes
        and routes them to registered handlers, then starts the server thread.
        
        Args:
            endpoint: Server configuration to instantiate.
        """
        # Define a closure that handles incoming messages from clients
        def handler(payload: dict, address):
            # Extract header and body from the raw payload dictionary
            envelope = SocketEnvelope(header=payload.get('header', {}),
                                      body=payload.get('body'))
            # Route the envelope to registered handlers
            self._emit(endpoint.name, envelope, address)

        # Create the server worker with the configured parameters
        server = SocketServerWorker(name=endpoint.name,
                                    host=endpoint.host,
                                    port=endpoint.port,
                                    handler=handler,
                                    max_clients=endpoint.max_clients)
        
        # Start the server's listening thread
        server.start()
        
        # Store the server worker instance for lifecycle management
        with self._lock:
            self._server_workers[endpoint.name] = server

    # Internal
    def _connect_client(self, name:str) -> bool:
        """
        Internal method to establish a client connection.
        
        Creates a new client worker instance and attempts to connect to the
        remote endpoint. On failure, schedules reconnection if configured.
        
        Args:
            name: Name of the client configuration to connect.
        
        Returns:
            True if connection succeeded, False otherwise.
        """
        # Retrieve the endpoint configuration
        endpoint = self._client_configs.get(name)
        if not endpoint:
            return False
        
        # If a worker already exists for this client, consider it connected
        if name in self._client_workers:
            return True
        
        # Create a new client worker with the endpoint's configuration
        worker = SocketClientWorker(name=name,
                                    host=endpoint.host,
                                    port=endpoint.port,
                                    queue_size=endpoint.queue_size,
                                    connect_timeout=endpoint.connect_timeout,
                                    acknowledge_timeout=endpoint.acknowledge_timeout,
                                    on_disconnect=self._handle_client_disconnect)
        
        # Attempt to establish the connection
        if not worker.connect():
            # If connection fails and auto-reconnect is enabled, schedule retry
            if endpoint.auto_reconnect:
                self._schedule_reconnect(name)
            return False
        
        # Start the worker's message processing thread
        worker.start()
        
        # Register the worker as active
        with self._lock:
            self._client_workers[name] = worker
        
        return True

    def _handle_client_disconnect(self, name:str, exc:Optional[BaseException]) -> None:
        """
        Callback invoked when a client connection is lost.
        
        Removes the disconnected worker and schedules reconnection if
        auto-reconnect is enabled and the manager isn't shutting down.
        
        Args:
            name: Name of the disconnected client.
            exc: Exception that caused the disconnect, if any.
        """
        # Remove the disconnected worker from the active workers
        with self._lock:
            self._client_workers.pop(name, None)
        
        # Retrieve the endpoint configuration
        endpoint = self._client_configs.get(name)
        
        # Don't reconnect if no config exists, auto-reconnect is disabled, or shutting down
        if not endpoint or not endpoint.auto_reconnect or self._shutdown_event.is_set():
            return
        
        # Log the disconnection and intent to reconnect
        warn(f'Socket client {name} disconnected; scheduling reconnect')
        
        # Schedule an automatic reconnection attempt
        self._schedule_reconnect(name)

    def _schedule_reconnect(self, name:str) -> None:
        """
        Schedule automatic reconnection attempts with exponential backoff.
        
        Spawns a daemon thread that repeatedly attempts to reconnect the
        client with increasing delays (2s, 4s, 8s, ..., up to 30s) until
        successful or the manager shuts down.
        
        Args:
            name: Name of the client to reconnect.
        """
        def worker() -> None:
            # Start with a 2-second delay between attempts
            delay = 2.0
            
            # Continue attempting until shutdown or successful connection
            while not self._shutdown_event.is_set():
                # Attempt to connect the client
                if self._connect_client(name):
                    # Log success and exit the reconnection loop
                    hint(f'Socket client {name} reconnected')
                    return
                
                # Wait before next attempt
                time.sleep(delay)
                
                # Double the delay for next attempt, capping at 30 seconds
                delay = min(delay * 2, 30.0)
        
        # Start the reconnection worker as a daemon thread (dies with main thread)
        threading.Thread(target=worker, daemon=True).start()

    def _emit(self,
              endpoint:str,
              envelope:SocketEnvelope,
              client_address:tuple[str,int]) -> None:
        """
        Route an incoming message to registered handlers.
        
        Finds all handlers registered for the specific endpoint plus wildcard
        handlers, then invokes each with the envelope and metadata. Exceptions
        in handlers are caught and logged without affecting other handlers.
        
        Args:
            endpoint: Name of the endpoint that received the message.
            envelope: The message envelope containing header and body.
            client_address: (host, port) tuple of the sending client.
        """
        # Collect handlers for this specific endpoint and wildcard handlers
        handlers = self._handlers.get(endpoint, []) + self._handlers.get('*', [])
        
        # Log if no handlers are available (only in verbose mode)
        if not handlers and self._verbose:
            warn(f'Received socket message for {endpoint} with no handlers registered')
            return
        
        # Invoke each registered handler
        for handler in handlers:
            try:
                # Call the handler with envelope and contextual metadata
                handler(envelope, client_address=client_address, endpoint=endpoint)
            except Exception as exc:  # noqa: BLE001
                # Log handler errors without interrupting other handlers
                err(f'Socket handler failure on {endpoint}: {exc}', traceback=True)

    # Lifecycle
    def shutdown(self) -> None:
        """
        Gracefully shut down all socket connections.
        
        Signals shutdown to prevent reconnection attempts, then closes all
        active client and server workers. Waits briefly for threads to terminate
        cleanly before clearing all state.
        """
        # Signal all background threads to stop (prevents reconnection loops)
        self._shutdown_event.set()
        
        # Close all active client workers
        for name, worker in list(self._client_workers.items()):
            try:
                # Request graceful shutdown to flush pending messages
                worker.close(graceful=True)
                # Wait up to 2 seconds for worker thread to exit
                worker.join(timeout=2)
            except Exception: # noqa: BLE001
                # Log errors but continue shutting down other workers
                err(f'Unable to close socket client {name}', traceback=True)
        
        # Clear the client workers dictionary
        self._client_workers.clear()

        # Stop all active server workers
        for name, server in list(self._server_workers.items()):
            try:
                # Signal the server to stop accepting connections
                server.stop()
                # Wait up to 2 seconds for server thread to exit
                server.join(timeout=2)
            except Exception: # noqa: BLE001
                # Log errors but continue shutting down other servers
                err(f'Unable to stop socket server {name}', traceback=True)
        
        # Clear the server workers dictionary
        self._server_workers.clear()
        
        # Log successful shutdown completion
        log('Socket service manager shut down cleanly')
