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
from teatype.logging import err, hint, log, warn

def socket_handler(endpoint:Optional[str]=None):
    """
    Decorator used by units to register socket handlers.
    """
    def decorator(function: Callable):
        setattr(function, '_socket_handler_target', endpoint or '*')
        return function
    return decorator

@dataclass
class SocketEndpoint:
    acknowledge_timeout:float=5.0
    auto_connect:bool=True
    auto_reconnect:bool=True
    connect_timeout:float=5.0
    host:str
    max_clients:int=5
    metadata:Dict[str,Any]=field(default_factory=dict)
    mode:Literal['client','server']
    name:str
    port:int
    queue_size:int=10

class SocketServiceManager:
    """
    High-level socket orchestration utilities.
    Coordinates socket clients and servers for Modulo units.
    """
    _client_configs:Dict[str,SocketEndpoint]
    _client_workers:Dict[str,SocketClientWorker]
    _handlers:Dict[str,List[Callable]]
    _lock:threading.RLock
    _server_configs:Dict[str,SocketEndpoint]
    _server_workers:Dict[str,SocketServerWorker]
    _shutdown_event:threading.Event
    _verbose:bool
    client_name: str
    
    def __init__(self,
                 client_name:Optional[str]=None,
                 owner:Optional[object]=None,
                 verbose_logging:Optional[bool] = False) -> None:
        self.client_name = client_name or 'teatype.socket.service'
        
        self._client_configs = {}
        self._server_configs = {}
        self._client_workers = {}
        self._server_workers = {}
        self._handlers = {}
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        self._verbose = verbose_logging

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
        endpoint = SocketEndpoint(name=name,
                                  host=host,
                                  port=port,
                                  mode='client',
                                  auto_connect=auto_connect,
                                  auto_reconnect=auto_reconnect,
                                  queue_size=queue_size,
                                  connect_timeout=connect_timeout,
                                  acknowledge_timeout=acknowledge_timeout)
        with self._lock:
            self._client_configs[name] = endpoint
        if auto_connect:
            self._connect_client(name)
        return endpoint

    def register_server(self,
                        name:str,
                        host:str,
                        port:int,
                        *,
                        max_clients:int=5) -> SocketEndpoint:
        endpoint = SocketEndpoint(name=name,
                                  host=host,
                                  port=port,
                                  mode='server',
                                  max_clients=max_clients)
        with self._lock:
            self._server_configs[name] = endpoint
        self._start_server(endpoint)
        return endpoint

    def register_handler(self, endpoint:str, handler:Callable) -> None:
        with self._lock:
            self._handlers.setdefault(endpoint, []).append(handler)
        if self._verbose:
            log(f'Registered socket handler for endpoint {endpoint}')

    def autowire(self, owner:object) -> None:
        for _, member in inspect.getmembers(owner, predicate=inspect.ismethod):
            endpoint = getattr(member, '_socket_handler_target', None)
            if endpoint:
                self.register_handler(endpoint, member)

    # Client control
    def send(self,
             receiver:str,
             header:Optional[Dict[str,Any]]=None,
             body:Any=None,
             *,
             block:bool=True) -> bool:
        worker = self._client_workers.get(receiver)
        if not worker:
            warn(f'No socket client named {receiver} is connected')
            return False
        envelope = SocketEnvelope(header=header or {}, body=body)
        envelope.normalize(receiver=receiver, source=self.client_name)
        return worker.emit(envelope, block=block)

    def disconnect_client(self, receiver:str, graceful:bool=True) -> None:
        worker = self._client_workers.get(receiver)
        if not worker:
            return
        worker.close(graceful=graceful)
        worker.join(timeout=2)
        with self._lock:
            self._client_workers.pop(receiver, None)

    def is_connected(self, receiver:str) -> bool:
        worker = self._client_workers.get(receiver)
        return bool(worker and worker.is_connected())

    # Server control
    def _start_server(self, endpoint:SocketEndpoint) -> None:
        def handler(payload: dict, address):
            envelope = SocketEnvelope(header=payload.get('header', {}),
                                      body=payload.get('body'))
            self._emit(endpoint.name, envelope, address)

        server = SocketServerWorker(name=endpoint.name,
                                    host=endpoint.host,
                                    port=endpoint.port,
                                    handler=handler,
                                    max_clients=endpoint.max_clients)
        server.start()
        with self._lock:
            self._server_workers[endpoint.name] = server

    # Internal
    def _connect_client(self, name:str) -> bool:
        endpoint = self._client_configs.get(name)
        if not endpoint:
            return False
        if name in self._client_workers:
            return True
        worker = SocketClientWorker(name=name,
                                    host=endpoint.host,
                                    port=endpoint.port,
                                    queue_size=endpoint.queue_size,
                                    connect_timeout=endpoint.connect_timeout,
                                    acknowledge_timeout=endpoint.acknowledge_timeout,
                                    on_disconnect=self._handle_client_disconnect)
        if not worker.connect():
            if endpoint.auto_reconnect:
                self._schedule_reconnect(name)
            return False
        worker.start()
        with self._lock:
            self._client_workers[name] = worker
        return True

    def _handle_client_disconnect(self, name:str, exc:Optional[BaseException]) -> None:
        with self._lock:
            self._client_workers.pop(name, None)
        endpoint = self._client_configs.get(name)
        if not endpoint or not endpoint.auto_reconnect or self._shutdown_event.is_set():
            return
        warn(f'Socket client {name} disconnected; scheduling reconnect')
        self._schedule_reconnect(name)

    def _schedule_reconnect(self, name:str) -> None:
        def worker() -> None:
            delay = 2.0
            while not self._shutdown_event.is_set():
                if self._connect_client(name):
                    hint(f'Socket client {name} reconnected')
                    return
                time.sleep(delay)
                delay = min(delay * 2, 30.0)
        threading.Thread(receiver=worker, daemon=True).start()

    def _emit(self,
              endpoint:str,
              envelope:SocketEnvelope,
              client_address:tuple[str,int]) -> None:
        handlers = self._handlers.get(endpoint, []) + self._handlers.get('*', [])
        if not handlers and self._verbose:
            warn(f'Received socket message for {endpoint} with no handlers registered')
            return
        for handler in handlers:
            try:
                handler(envelope, client_address=client_address, endpoint=endpoint)
            except Exception as exc:  # noqa: BLE001
                err(f'Socket handler failure on {endpoint}: {exc}', traceback=True)

    # Lifecycle
    def shutdown(self) -> None:
        self._shutdown_event.set()
        for name, worker in list(self._client_workers.items()):
            try:
                worker.close(graceful=True)
                worker.join(timeout=2)
            except Exception: # noqa: BLE001
                err(f'Unable to close socket client {name}', traceback=True)
        self._client_workers.clear()

        for name, server in list(self._server_workers.items()):
            try:
                server.stop()
                server.join(timeout=2)
            except Exception: # noqa: BLE001
                err(f'Unable to stop socket server {name}', traceback=True)
        self._server_workers.clear()
        log('Socket service manager shut down cleanly')
