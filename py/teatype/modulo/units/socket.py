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
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Union

# Third-party imports
from teatype.comms.ipc.socket import SocketServiceManager, socket_handler
from teatype.logging import *
from teatype.modulo.units.core import CoreUnit

@dataclass(frozen=True)
class SocketClientConfig:
    """
    Declarative client definition consumed by SocketServiceManager.
    
    Attributes:
        name: Unique identifier for this client connection
        host: Target server hostname or IP address
        port: Target server port number
        queue_size: Maximum number of queued outbound messages
        connect_timeout: Seconds to wait when establishing connection
        acknowledge_timeout: Seconds to wait for server acknowledgment
        auto_connect: Whether to automatically connect on registration
        auto_reconnect: Whether to automatically reconnect on disconnect
    """
    name:str
    host:str
    port:int
    queue_size:int=10
    connect_timeout:float=5.0
    acknowledge_timeout:float=5.0
    auto_connect:bool=True
    auto_reconnect:bool=True

@dataclass(frozen=True)
class SocketServerConfig:
    """
    Declarative server definition consumed by SocketServiceManager.
    
    Attributes:
        name: Unique identifier for this server instance
        host: Server bind address (e.g., '0.0.0.0' or '127.0.0.1')
        port: Server listening port number
        max_clients: Maximum concurrent client connections allowed
    """
    name:str
    host:str
    port:int
    max_clients:int=5

# Type aliases allowing either config objects or raw dictionaries
SocketClientConfigLike=Union[SocketClientConfig,Dict[str,Any]]
SocketServerConfigLike=Union[SocketServerConfig,Dict[str,Any]]

def _coerce_client(config:SocketClientConfigLike) -> SocketClientConfig:
    """
    Convert dictionary or pass-through SocketClientConfig to canonical form.
    """
    return config if isinstance(config, SocketClientConfig) else SocketClientConfig(**config)

def _coerce_server(config:SocketServerConfigLike) -> SocketServerConfig:
    """
    Convert dictionary or pass-through SocketServerConfig to canonical form.
    """
    return config if isinstance(config, SocketServerConfig) else SocketServerConfig(**config)

class SocketUnit(CoreUnit):
    """
    Modulo unit responsible for coordinating the socket protocol stack.
    
    This unit manages both server and client socket endpoints, handling
    connection lifecycle, message routing, and graceful shutdown. It wraps
    SocketServiceManager with a declarative configuration interface.
    """
    def __init__(self,
                 name:str,
                 *,
                 server:Optional[SocketServerConfigLike]=None,
                 clients:Optional[Iterable[SocketClientConfigLike]]=None,
                 enable_default_server:bool=True,
                 server_host:str='127.0.0.1',
                 server_port:int=9050,
                 server_max_clients:int=5,
                 verbose_logging:Optional[bool]=False) -> None:
        """
        Initialize the SocketUnit with server and client configurations.
        
        Args:
            name: Unit identifier used in logging and designation
            server: Optional explicit server configuration (overrides defaults)
            clients: Optional iterable of client configurations to register
            enable_default_server: Whether to create a default server if none provided
            server_host: Default server bind address
            server_port: Default server listening port
            server_max_clients: Default maximum concurrent clients
            verbose_logging: Enable detailed debug logging
        """
        # Initialize parent CoreUnit with name and logging preferences
        super().__init__(name=name, verbose_logging=verbose_logging)
        # Set loop idle time to control polling frequency
        self.loop_idle_time = 0.5
        # Create underlying socket service manager with this unit as owner
        self._socket_service = SocketServiceManager(client_name=self.designation,
                                                    owner=self,
                                                    verbose_logging=verbose_logging)
        # Build default server configuration from individual parameters
        default_server = SocketServerConfig(name=f'{self.name}-socket',
                                            host=server_host,
                                            port=server_port,
                                            max_clients=server_max_clients)
        # Determine which server config to use: explicit, default, or none
        self._server_config: Optional[SocketServerConfig] = None
        if server:
            # Use explicitly provided server configuration
            self._server_config = _coerce_server(server)
        elif enable_default_server:
            # Fall back to default server configuration
            self._server_config = default_server
        # Convert all client configurations to canonical SocketClientConfig objects
        self._client_configs: List[SocketClientConfig] = [
            _coerce_client(config) for config in (clients or [])
        ]

    # Lifecycle
    def on_loop_start(self) -> None:
        """
        Called when unit lifecycle loop begins; registers all endpoints.
        """
        hint('Bootstrapping socket endpoints ...')
        # Mark unit as initializing during setup phase
        self._status = 'initializing'
        # Register all declared servers and clients with the service manager
        self._register_declared_endpoints()
        # Mark unit as ready after successful registration
        self._status = 'ready'

    def on_loop_run(self) -> None:
        """
        Called repeatedly during unit lifecycle; maintains ready state.
        """
        # Increase idle time to reduce CPU usage during normal operation
        self.loop_idle_time = 1.0
        # Ensure status is set to ready if it was changed externally
        if self._status != 'ready':
            self._status = 'ready'

    def on_loop_end(self) -> None:
        """
        Called when unit lifecycle loop terminates; cleanly shuts down sockets.
        """
        # Shutdown all active connections and listening sockets
        self._socket_service.shutdown()

    def shutdown(self, force:bool=False) -> None:
        """
        Initiate graceful or forced shutdown of the socket unit.
        
        Args:
            force: If True, bypass shutdown-in-progress check
        """
        # Prevent duplicate shutdown calls unless force is specified
        if not force and self._shutdown_in_progress:
            return
        # Mark shutdown as in progress to block duplicate attempts
        self._shutdown_in_progress = True
        hint('Shutting down socket unit ...')

    # Registration helpers
    def register_server(self, config:SocketServerConfigLike) -> SocketServerConfig:
        """
        Register a new server endpoint with the socket service.
        
        Args:
            config: Server configuration as object or dictionary
        
        Returns:
            Canonical SocketServerConfig object
        """
        # Convert config to canonical form
        server = _coerce_server(config)
        # Store server config for potential re-registration
        self._server_config = server
        # Register server with underlying service manager
        self._socket_service.register_server(name=server.name,
                                             host=server.host,
                                             port=server.port,
                                             max_clients=server.max_clients)
        return server

    def register_client(self, config:SocketClientConfigLike) -> SocketClientConfig:
        """
        Register a new client endpoint with the socket service.
        
        Args:
            config: Client configuration as object or dictionary
        
        Returns:
            Canonical SocketClientConfig object
        """
        # Convert config to canonical form
        client = _coerce_client(config)
        # Append to tracked client configs for lifecycle management
        self._client_configs.append(client)
        # Register client with underlying service manager including all timeouts
        self._socket_service.register_client(name=client.name,
                                             host=client.host,
                                             port=client.port,
                                             auto_connect=client.auto_connect,
                                             auto_reconnect=client.auto_reconnect,
                                             queue_size=client.queue_size,
                                             connect_timeout=client.connect_timeout,
                                             acknowledge_timeout=client.acknowledge_timeout)
        return client

    def _register_declared_endpoints(self) -> None:
        """
        Register all server and client endpoints declared during initialization.
        """
        # Register server first if one was configured
        if self._server_config:
            self.register_server(self._server_config)
        # Register each client endpoint in sequence
        for client in list(self._client_configs):
            self.register_client(client)

    # Client helpers
    def send(self,
             endpoint:str,
             *,
             header:Optional[Dict[str,Any]]=None,
             body:Any=None,
             block:bool=True) -> bool:
        """
        Send a message to a registered client endpoint.
        
        Args:
            endpoint: Name of the target client endpoint
            header: Optional message header metadata
            body: Message payload (any serializable type)
            block: Whether to block until message is queued
        
        Returns:
            True if message was successfully queued, False otherwise
        """
        # Delegate to underlying service manager's send implementation
        return self._socket_service.send(endpoint,
                                         header=header,
                                         body=body,
                                         block=block)

    def disconnect(self, endpoint:str, graceful:bool=True) -> None:
        """
        Disconnect a client endpoint.
        
        Args:
            endpoint: Name of the client endpoint to disconnect
            graceful: Whether to allow pending messages to flush before disconnect
        """
        # Delegate to underlying service manager's disconnect implementation
        self._socket_service.disconnect_client(endpoint, graceful=graceful)

    def is_connected(self, endpoint:str) -> bool:
        """
        Check if a client endpoint is currently connected.
        
        Args:
            endpoint: Name of the client endpoint to check
        
        Returns:
            True if endpoint is connected, False otherwise
        """
        # Query connection status from underlying service manager
        return self._socket_service.is_connected(endpoint)

    # Default handler
    @socket_handler('*')
    def _log_inbound_payload(self,
                             envelope,
                             *,
                             client_address,
                             endpoint:str) -> None:
        """
        Default wildcard handler that logs all inbound socket messages.
        
        Args:
            envelope: Message envelope containing header and body
            client_address: Source address of the sending client
            endpoint: Name of the endpoint that received the message
        """
        # Format body for logging: preserve dict structure, stringify others
        body_preview = envelope.body if isinstance(envelope.body, dict) else str(envelope.body)
        # Log message metadata and body preview
        log(f'[socket] Endpoint={endpoint} Sender={client_address} Body={body_preview}')

class _DemoSocketUnit(SocketUnit):
    """
    Loopback-friendly socket unit used by the CLI demo entrypoint.
    
    Creates both a server and a client that connects back to itself,
    demonstrating bidirectional socket communication in a single process.
    """

    # Constant endpoint name for the loopback connection
    LOOPBACK_ENDPOINT='loopback'

    def __init__(self, host:str, port:int) -> None:
        """
        Initialize demo unit with loopback client configuration.
        
        Args:
            host: Server bind address and client connection target
            port: Server listening port and client connection target
        """
        # Create client config that connects to the same host:port as server
        loopback_client = SocketClientConfig(name=self.LOOPBACK_ENDPOINT,
                                             host=host,
                                             port=port,
                                             auto_connect=True,
                                             auto_reconnect=True)
        # Initialize parent with matching server and client configurations
        super().__init__(name='demo-socket-unit',
                         server_host=host,
                         server_port=port,
                         clients=[loopback_client],
                         verbose_logging=True)
        # Store endpoint name for convenient access in ping method
        self._loopback_endpoint = loopback_client.name

    @socket_handler(LOOPBACK_ENDPOINT)
    def _handle_loopback(self, envelope, *, client_address, endpoint):
        """
        Handler specifically for loopback endpoint messages.
        
        Args:
            envelope: Received message envelope
            client_address: Source address (will be localhost)
            endpoint: Endpoint name (will be LOOPBACK_ENDPOINT)
        """
        # Log loopback message with address, endpoint, and body
        hint(f'[loopback] {client_address} -> {endpoint}: {envelope.body}')

    def ping(self, payload:Optional[Dict[str,Any]]=None) -> None:
        """
        Send a ping message through the loopback connection.
        
        Args:
            payload: Optional custom payload; defaults to timestamp message
        """
        # Create default payload with timestamp if none provided
        payload = payload or {'message': 'ping', 'timestamp': time.time()}
        # Attempt to send payload to loopback endpoint
        if not self.send(self._loopback_endpoint, body=payload):
            # Warn if send failed due to disconnected client
            warn('Loopback client is not connected; ping dropped')

def _demo_main() -> None:
    """
    CLI entrypoint demonstrating SocketUnit loopback functionality.
    
    Starts a demo unit with server and self-connecting client, then
    periodically sends ping messages through the loopback connection.
    """
    # Parse command-line arguments for demo configuration
    parser = argparse.ArgumentParser(description='SocketUnit loopback harness')
    parser.add_argument('--host', default='127.0.0.1', help='Server bind address')
    parser.add_argument('--port', type=int, default=9050, help='Server bind port')
    parser.add_argument('--interval', type=float, default=2.0, help='Loopback ping interval seconds')
    args = parser.parse_args()

    # Create and start the demo socket unit
    unit = _DemoSocketUnit(host=args.host, port=args.port)
    unit.start()
    hint('Demo SocketUnit started. Press Ctrl+C to stop.')
    try:
        # Main loop: periodically ping while unit is alive
        while unit.is_alive():
            # Sleep for specified interval (minimum 0.1s to avoid tight loop)
            time.sleep(max(args.interval, 0.1))
            # Send ping through loopback connection
            unit.ping()
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        hint('Interrupt received; stopping demo SocketUnit ...')
    finally:
        # Ensure unit is shutdown and joined regardless of exit path
        unit.shutdown(force=True)
        # Wait up to 2 seconds for clean thread termination
        unit.join(timeout=2)

# Module entrypoint for direct execution
if __name__ == '__main__':
    _demo_main()

# Export only the main SocketUnit class as public API
__all__ = ['SocketUnit']
