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
from typing import Any, Dict, Optional

# Third-party imports
from teatype.comms.ipc.socket.service import SocketEndpoint, SocketServiceManager
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