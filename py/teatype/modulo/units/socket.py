from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from teatype.comms.ipc.socket import SocketServiceManager, socket_handler
from teatype.logging import err, hint, log, warn
from teatype.modulo.units.core import CoreUnit

@dataclass(frozen=True)
class SocketClientConfig:
	"""
    Declarative client definition consumed by SocketServiceManager.
    """
	name: str
	host: str
	port: int
	queue_size: int = 10
	connect_timeout: float = 5.0
	acknowledge_timeout: float = 5.0
	auto_connect: bool = True
	auto_reconnect: bool = True

@dataclass(frozen=True)
class SocketServerConfig:
	"""
    Declarative server definition consumed by SocketServiceManager.
    """
	name: str
	host: str
	port: int
	max_clients: int = 5

SocketClientConfigLike = Union[SocketClientConfig, Dict[str, Any]]
SocketServerConfigLike = Union[SocketServerConfig, Dict[str, Any]]

def _coerce_client(config: SocketClientConfigLike) -> SocketClientConfig:
	return config if isinstance(config, SocketClientConfig) else SocketClientConfig(**config)

def _coerce_server(config: SocketServerConfigLike) -> SocketServerConfig:
	return config if isinstance(config, SocketServerConfig) else SocketServerConfig(**config)

class SocketUnit(CoreUnit):
	"""
    Modulo unit responsible for coordinating the socket protocol stack.
    """

	def __init__(self,
				 name: str,
				 *,
				 server: Optional[SocketServerConfigLike] = None,
				 clients: Optional[Iterable[SocketClientConfigLike]] = None,
				 enable_default_server: bool = True,
				 server_host: str = '127.0.0.1',
				 server_port: int = 9050,
				 server_max_clients: int = 5,
				 verbose_logging: Optional[bool] = False) -> None:
		super().__init__(name=name, verbose_logging=verbose_logging)
		self.loop_idle_time = 0.5
		self._socket_service = SocketServiceManager(client_name=self.designation,
													owner=self,
													verbose_logging=verbose_logging)
		default_server = SocketServerConfig(name=f'{self.name}-socket',
											host=server_host,
											port=server_port,
											max_clients=server_max_clients)
		self._server_config: Optional[SocketServerConfig] = None
		if server:
			self._server_config = _coerce_server(server)
		elif enable_default_server:
			self._server_config = default_server
		self._client_configs: List[SocketClientConfig] = [
			_coerce_client(config) for config in (clients or [])
		]

	# Lifecycle
	def on_loop_start(self) -> None:
		hint('Bootstrapping socket endpoints ...')
		self._status = 'initializing'
		self._register_declared_endpoints()
		self._status = 'ready'

	def on_loop_run(self) -> None:
		self.loop_idle_time = 1.0
		if self._status != 'ready':
			self._status = 'ready'

	def on_loop_end(self) -> None:
		self._socket_service.shutdown()

	def shutdown(self, force: bool = False) -> None:
		if not force and self._shutdown_in_progress:
			return
		self._shutdown_in_progress = True
		hint('Shutting down socket unit ...')

	# Registration helpers
	def register_server(self, config: SocketServerConfigLike) -> SocketServerConfig:
		server = _coerce_server(config)
		self._server_config = server
		self._socket_service.register_server(name=server.name,
											 host=server.host,
											 port=server.port,
											 max_clients=server.max_clients)
		return server

	def register_client(self, config: SocketClientConfigLike) -> SocketClientConfig:
		client = _coerce_client(config)
		self._client_configs.append(client)
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
		if self._server_config:
			self.register_server(self._server_config)
		for client in list(self._client_configs):
			self.register_client(client)

	# Client helpers
	def send(self,
			 endpoint: str,
			 *,
			 header: Optional[Dict[str, Any]] = None,
			 body: Any = None,
			 block: bool = True) -> bool:
		return self._socket_service.send(endpoint,
										 header=header,
										 body=body,
										 block=block)

	def disconnect(self, endpoint: str, graceful: bool = True) -> None:
		self._socket_service.disconnect_client(endpoint, graceful=graceful)

	def is_connected(self, endpoint: str) -> bool:
		return self._socket_service.is_connected(endpoint)

	# Default handler
	@socket_handler('*')
	def _log_inbound_payload(self,
							 envelope,
							 *,
							 client_address,
							 endpoint: str) -> None:
		body_preview = envelope.body if isinstance(envelope.body, dict) else str(envelope.body)
		log(f'[socket] Endpoint={endpoint} Sender={client_address} Body={body_preview}')

class _DemoSocketUnit(SocketUnit):
	"""
    Loopback-friendly socket unit used by the CLI demo entrypoint.
    """

	LOOPBACK_ENDPOINT = 'loopback'

	def __init__(self, host: str, port: int) -> None:
		loopback_client = SocketClientConfig(name=self.LOOPBACK_ENDPOINT,
											 host=host,
											 port=port,
											 auto_connect=True,
											 auto_reconnect=True)
		super().__init__(name='demo-socket-unit',
						 server_host=host,
						 server_port=port,
						 clients=[loopback_client],
						 verbose_logging=True)
		self._loopback_endpoint = loopback_client.name

	@socket_handler(LOOPBACK_ENDPOINT)
	def _handle_loopback(self, envelope, *, client_address, endpoint):
		hint(f'[loopback] {client_address} -> {endpoint}: {envelope.body}')

	def ping(self, payload: Optional[Dict[str, Any]] = None) -> None:
		payload = payload or {'message': 'ping', 'timestamp': time.time()}
		if not self.send(self._loopback_endpoint, body=payload):
			warn('Loopback client is not connected; ping dropped')

def _demo_main() -> None:
	parser = argparse.ArgumentParser(description='SocketUnit loopback harness')
	parser.add_argument('--host', default='127.0.0.1', help='Server bind address')
	parser.add_argument('--port', type=int, default=9050, help='Server bind port')
	parser.add_argument('--interval', type=float, default=2.0, help='Loopback ping interval seconds')
	args = parser.parse_args()

	unit = _DemoSocketUnit(host=args.host, port=args.port)
	unit.start()
	hint('Demo SocketUnit started. Press Ctrl+C to stop.')
	try:
		while unit.is_alive():
			time.sleep(max(args.interval, 0.1))
			unit.ping()
	except KeyboardInterrupt:
		hint('Interrupt received; stopping demo SocketUnit ...')
	finally:
		unit.shutdown(force=True)
		unit.join(timeout=2)

if __name__ == '__main__':
	_demo_main()

__all__ = ['SocketUnit']
