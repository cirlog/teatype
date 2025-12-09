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
import threading
import time
from typing import Any, Dict, Optional

# Third-party imports
from teatype.comms.ipc.socket.service import SocketEndpoint, SocketServiceManager, socket_handler
from teatype.logging import *
from teatype.modulo.units.core import CoreUnit

class SocketUnit(CoreUnit):
	"""
    Base unit that wires Modulo components into the socket service layer.
    """
	socket_service:Optional[SocketServiceManager]

	def __init__(self,
                 name:str,
                 *,
                 verbose_logging:Optional[bool]=False,
                 auto_setup:bool=True) -> None:
		super().__init__(name=name, verbose_logging=verbose_logging)
  
		self.socket_service = None
  
		if auto_setup:
			self._setup_socket_infrastructure()

	#################
	# Infrastructure #
	#################

	def _setup_socket_infrastructure(self) -> None:
		"""
        Instantiate the socket service manager and autowire handlers.
        """
		try:
			self.socket_service = SocketServiceManager(client_name=self.designation,
													   owner=self,
													   verbose_logging=self._verbose_logging)
		except Exception:
			err('Socket infrastructure setup failed.', traceback=True)

	def _terminate_socket_infrastructure(self) -> None:
		"""
        Shutdown the socket service manager if it exists.
        """
		if self.socket_service:
			try:
				self.socket_service.shutdown()
			except Exception:
				err('Socket infrastructure termination failed.', traceback=True)
			finally:
				self.socket_service = None

	#########################
	# Socket service helpers #
	#########################

	def _require_socket_service(self) -> SocketServiceManager:
		if not self.socket_service:
			raise RuntimeError('Socket service manager is not initialized')
		return self.socket_service

	def register_socket_client(self,
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
        Proxy helper for registering outbound client endpoints.
        """
		service = self._require_socket_service()
		return service.register_client(name=name,
									   host=host,
									   port=port,
									   auto_connect=auto_connect,
									   auto_reconnect=auto_reconnect,
									   queue_size=queue_size,
									   connect_timeout=connect_timeout,
									   acknowledge_timeout=acknowledge_timeout)

	def register_socket_server(self,
							   name:str,
							   host:str,
							   port:int,
							   *,
							   max_clients:int=5) -> SocketEndpoint:
		"""
        Proxy helper for registering inbound server endpoints.
        """
		service = self._require_socket_service()
		return service.register_server(name=name,
									   host=host,
									   port=port,
									   max_clients=max_clients)

	def send_socket_message(self,
							receiver:str,
							*,
							header:Optional[Dict[str,Any]]=None,
							body:Any=None,
							block:bool=True) -> bool:
		"""
        Send an envelope through a registered client endpoint.
        """
		service = self._require_socket_service()
		return service.send(receiver=receiver,
							header=header,
							body=body,
							block=block)

	def disconnect_socket_client(self, receiver:str, graceful:bool=True) -> None:
		"""
        Disconnect a client worker by name.
        """
		service = self._require_socket_service()
		service.disconnect_client(receiver, graceful=graceful)

	def is_socket_client_connected(self, receiver:str) -> bool:
		"""
        Check if a named client worker is connected.
        """
		service = self._require_socket_service()
		return service.is_connected(receiver)

	##############
	# Lifecycle  #
	##############

	def shutdown(self, force:bool=False) -> None:
		"""
        Gracefully shutdown the unit and socket infrastructure.
        """
		if not force and self._shutdown_in_progress:
			hint('Socket shutdown already in progress')
			return

		self._shutdown_in_progress = True
		try:
			hint('Commencing socket shutdown procedure ...')
			self._terminate_socket_infrastructure()
		except Exception:
			err('Socket shutdown failed', traceback=True)

if __name__ == '__main__':
    class DemoSocketUnit(SocketUnit):
        """
        Minimal runnable example showcasing multiple endpoints and handlers.
        """
        LOOPBACK_HOST='127.0.0.1'
        LOOPBACK_PORT=28110

        def on_loop_start(self) -> None:
            """
            Register demo endpoints and kick off sample traffic.
            """
            super().on_loop_start()

            # Inbound endpoints: expose two logical channels to show multi-handler wiring
            self.register_socket_server(name='loopback-server',
                                        host=self.LOOPBACK_HOST,
                                        port=self.LOOPBACK_PORT,
                                        max_clients=2)
            self.register_socket_server(name='diagnostics',
                                        host=self.LOOPBACK_HOST,
                                        port=self.LOOPBACK_PORT + 1,
                                        max_clients=1)

            # Outbound endpoint that auto-connects to our own loopback server
            self.register_socket_client(name='loopback-client',
                                        host=self.LOOPBACK_HOST,
                                        port=self.LOOPBACK_PORT,
                                        queue_size=32,
                                        auto_reconnect=False,
                                        acknowledge_timeout=2.0)

            # Demonstrate a client config that is registered but not auto-connected yet
            self.register_socket_client(name='analytics-uplink',
                                        host='192.168.1.50',
                                        port=29000,
                                        auto_connect=False,
                                        auto_reconnect=True)

            # Give sockets a moment to negotiate, then fire demo payloads
            threading.Timer(1.0, self._send_demo_messages).start()

        def on_loop_run(self) -> None:
            """
            Idle loop; real units would poll work or react to queues.
            """
            time.sleep(0.25)

        def _send_demo_messages(self) -> None:
            """
            Emit a couple of envelopes through the loopback client.
            """
            payloads = [
                {'sequence': 1, 'message': 'Hello over TCP'},
                {'sequence': 2, 'message': 'Binary-safe payload', 'meta': {'priority': 'high'}},
            ]
            for body in payloads:
                self.send_socket_message('loopback-client', body=body)

        @socket_handler('loopback-server')
        def handle_loopback(self, envelope, *, client_address, endpoint):  # type: ignore[override]
            """Receive loopback traffic from the demo server endpoint."""
            hint(f"[{endpoint}] {client_address} -> {envelope.body}")
            if envelope.body.get('sequence') == 2:
                # Schedule shutdown once we prove round-trip delivery works
                threading.Timer(0.5, lambda: self.shutdown(force=True)).start()

	demo = DemoSocketUnit.create(name='demo-socket-unit', verbose_logging=True)
	try:
		demo.start()
		demo.join()
	except KeyboardInterrupt:
		demo.shutdown(force=True)
