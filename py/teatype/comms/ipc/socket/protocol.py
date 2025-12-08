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
from teatype.logging import err, hint, log, warn
from teatype.toolkit import generate_id

ACKNOWLEDGE_MESSAGE = b'OK'
DEFAULT_CHUNK_SIZE = 4096
_DEFAULT_QUEUE_TIMEOUT = 1.0

class FrameBuilder:
    """
    Constructs the framing messages required by the protocol.
    """
    @staticmethod
    def size_probe(envelope:SocketEnvelope, payload_length:int) -> bytes:
        probe = {
            'header': {
                'content': 'bytes',
                'method': 'size_of',
                'id': envelope.request_id,
                'status': 'pending',
                'receiver': envelope.header['receiver']
            },
            'body': payload_length
        }
        return pickle.dumps(probe)

    @staticmethod
    def close_signal(receiver: str) -> bytes:
        payload = {
            'header': {
                'content': 'string',
                'method': 'close_socket',
                'id': generate_id(truncate=12),
                'status': 'closing',
                'receiver': receiver
            },
            'body': 'Closing connection'
        }
        return pickle.dumps(payload)

class SocketClientWorker(threading.Thread):
    """
    Asynchronous writer
    """
    name: str
    host: str
    port: int
    connect_timeout: float
    acknowledge_timeout: float
    _outbox: queue.Queue[Any]
    _queue_timeout: float
    _socket: Optional[socket.socket]
    _stop_event: threading.Event
    _connected: bool
    _disconnect_callback: Optional[Callable[[str,Optional[BaseException]],None]]
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
        super().__init__(daemon=True)
        self.name = name
        self.host = host
        self.port = port
        self.connect_timeout = connect_timeout
        self.acknowledge_timeout = acknowledge_timeout
        self._outbox:queue.Queue[Any] = queue.Queue(maxsize=queue_size)
        self._queue_timeout = queue_timeout
        self._socket:Optional[socket.socket] = None
        self._stop_event = threading.Event()
        self._connected = False
        self._disconnect_callback = on_disconnect
        self._close_requested = False

    # Public API ------------------------------------------------------------
    def connect(self) -> bool:
        try:
            self._socket = socket.create_connection((self.host, self.port), timeout=self.connect_timeout)
            self._socket.settimeout(self.acknowledge_timeout)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._connected = True
            log(f'Socket client [{self.name}] connected to {self.host}:{self.port}')
            return True
        except OSError as exc:
            warn(f'Socket client [{self.name}] failed to connect: {exc}')
            self._connected = False
            self._socket = None
            return False

    def emit(self, envelope: SocketEnvelope, block: bool = True) -> bool:
        if not self._connected:
            warn(f'Socket client [{self.name}] is not connected; dropping message')
            return False
        try:
            self._outbox.put(envelope, block=block, timeout=self._queue_timeout if block else None)
            return True
        except queue.Full:
            warn(f'Socket client [{self.name}] queue is full; message rejected')
            return False

    def close(self, graceful: bool = True) -> None:
        if graceful and self._connected:
            try:
                self._outbox.put_nowait(FrameBuilder.close_signal(self.name))
            except queue.Full:
                warn(f'Socket client [{self.name}] close signal dropped (queue full)')
                self._close_socket_immediately()
        else:
            self._close_socket_immediately()
        self._stop_event.set()

    def is_connected(self) -> bool:
        return self._connected

    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                payload = self._outbox.get(timeout=self._queue_timeout)
            except queue.Empty:
                if not self._check_connection_state():
                    break
                continue

            if isinstance(payload, bytes):
                # Close signal already serialized by FrameBuilder
                self._send_raw(payload)
                break

            if not isinstance(payload, SocketEnvelope):
                warn(f'Socket client [{self.name}] received unsupported payload type {type(payload)}')
                continue

            try:
                payload.normalize(receiver=self.name)
                serialized_payload = payload.dumps()
                probe = FrameBuilder.size_probe(payload, len(serialized_payload))
                self._send_raw(probe)
                ack = self._safe_recv()
                if ack != ACKNOWLEDGE_MESSAGE:
                    raise ConnectionError(f'Unexpected ACK {ack!r}')
                self._send_raw(serialized_payload)
                log(f'Socket client [{self.name}] shipped request {payload.request_id}')
            except Exception as exc:  # noqa: BLE001
                err(f'Socket client [{self.name}] send failure: {exc}', traceback=True)
                break

        self._close_socket_immediately()
        if self._disconnect_callback:
            self._disconnect_callback(self.name, None)

    # Internals
    def _send_raw(self, data: bytes) -> None:
        if not self._socket:
            raise ConnectionError('Socket is not connected')
        self._socket.sendall(data)

    def _safe_recv(self) -> bytes:
        if not self._socket:
            raise ConnectionError('Socket is not connected')
        return self._socket.recv(DEFAULT_CHUNK_SIZE)

    def _check_connection_state(self) -> bool:
        if not self._socket or not self._connected:
            return False
        try:
            self._socket.recv(1, socket.MSG_PEEK | socket.MSG_DONTWAIT)
        except BlockingIOError:
            return True
        except OSError:
            warn(f'Socket client [{self.name}] connection closed by peer')
            return False
        return True

    def _close_socket_immediately(self) -> None:
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                self._socket.close()
        self._connected = False
        self._socket = None


class SocketSession(threading.Thread):
    """
    Manages one inbound client connection for the SocketServerWorker.
    """
    def __init__(self,
                 server: 'SocketServerWorker',
                 connection: socket.socket,
                 address: Tuple[str, int]):
        super().__init__(daemon=True)
        self._server = server
        self._connection = connection
        self._address = address
        self._stop_event = threading.Event()

    def run(self) -> None:
        try:
            while not self._server.stop_event.is_set():
                control_frame = self._receive_frame()
                if control_frame is None:
                    break
                method = control_frame['header'].get('method')
                if method == 'close_socket':
                    hint(f'Client {self._address} requested close on {self._server.name}')
                    break
                if method != 'size_of':
                    warn(f'Client {self._address} sent unsupported method {method}')
                    continue
                expected_bytes = int(control_frame['body'])
                self._connection.sendall(ACKNOWLEDGE_MESSAGE)
                payload = self._receive_exact(expected_bytes)
                if payload is None:
                    break
                try:
                    message = pickle.loads(payload)
                except Exception as exc:  # noqa: BLE001
                    err(f'Failed to deserialize payload from {self._address}: {exc}', traceback=True)
                    continue
                self._server.dispatch(message, self._address)
        except ConnectionError as exc:
            warn(f'Connection to {self._address} dropped: {exc}')
        finally:
            self._teardown()

    def stop(self) -> None:
        self._stop_event.set()
        self._teardown()

    def _receive_frame(self) -> Optional[dict]:
        buffer = bytearray()
        while not self._server.stop_event.is_set():
            chunk = self._connection.recv(DEFAULT_CHUNK_SIZE)
            if not chunk:
                return None
            buffer.extend(chunk)
            try:
                return pickle.loads(buffer)
            except (EOFError, pickle.UnpicklingError):
                continue

    def _receive_exact(self, expected_bytes: int) -> Optional[bytes]:
        buffer = bytearray()
        while len(buffer) < expected_bytes and not self._server.stop_event.is_set():
            chunk = self._connection.recv(min(DEFAULT_CHUNK_SIZE, expected_bytes - len(buffer)))
            if not chunk:
                return None
            buffer.extend(chunk)
        return bytes(buffer)

    def _teardown(self) -> None:
        try:
            self._connection.close()
        except OSError:
            pass

class SocketServerWorker(threading.Thread):
    """
    Listens for inbound socket clients and dispatches reconstructed envelopes.
    """
    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 handler: Callable[[dict, Tuple[str, int]], None],
                 max_clients: int = 5,
                 backlog: int = 5):
        super().__init__(daemon=True)
        self.name = name
        self.host = host
        self.port = port
        self._handler = handler
        self._max_clients = max_clients
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(backlog)
        self.stop_event = threading.Event()
        self._sessions: set[SocketSession] = set()
        self._lock = RLock()
        log(f'Socket server [{self.name}] listening on {self.host}:{self.port}')

    def run(self) -> None:
        while not self.stop_event.is_set():
            try:
                client_socket, address = self._server_socket.accept()
                session = SocketSession(self, client_socket, address)
                session.start()
                with self._lock:
                    self._sessions.add(session)
                log(f'Socket server [{self.name}] accepted connection from {address}')
            except OSError:
                if self.stop_event.is_set():
                    break
                err(f'Socket server [{self.name}] failed to accept connection', traceback=True)

    def stop(self) -> None:
        self.stop_event.set()
        try:
            self._server_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            self._server_socket.close()
        with self._lock:
            for session in list(self._sessions):
                session.stop()
            self._sessions.clear()
        log(f'Socket server [{self.name}] stopped')

    def dispatch(self, message: dict, address: Tuple[str, int]) -> None:
        try:
            self._handler(message, address)
        except Exception as exc:  # noqa: BLE001
            err(f'Socket server [{self.name}] handler failure: {exc}', traceback=True)

def _demo_server(host: str, port: int) -> None:
    """
    Run a demo SocketServerWorker that logs inbound payloads.
    """

    def handler(message: dict, address: Tuple[str, int]) -> None:
        log(f'[server] Received payload from {address}: {message}')

    server = SocketServerWorker('demo-server', host, port, handler)
    server.start()
    log(f'Demo server ready on {host}:{port}. Press Ctrl+C to stop.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log('Stopping demo server ...')
    finally:
        server.stop()
        server.join(timeout=2)

def _demo_client(host: str, port: int) -> None:
    """
    Run a demo SocketClientWorker that sends a sample envelope.
    """

    client = SocketClientWorker('demo-server', host, port)
    if not client.connect():
        err('Demo client failed to connect to server')
        return
    client.start()

    envelope = SocketEnvelope(
        header={'receiver': 'demo-server', 'method': 'payload'},
        body={'message': 'Hello from SocketClientWorker!', 'timestamp': time.time()}
    )
    client.emit(envelope)
    time.sleep(1)
    client.close(graceful=True)
    client.join(timeout=2)
    log('Demo client finished')

def _demo_main() -> None:
    parser = argparse.ArgumentParser(description='Socket protocol demo runner')
    parser.add_argument('role', choices=['server', 'client'], help='Which demo to run')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind/connect')
    parser.add_argument('--port', type=int, default=9050, help='Port to bind/connect')
    args = parser.parse_args()

    if args.role == 'server':
        _demo_server(args.host, args.port)
    else:
        _demo_client(args.host, args.port)

if __name__ == '__main__':
    _demo_main()
