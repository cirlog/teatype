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

# Third-party imports
from teatype.comms.ipc.socket.service import socket_handler
from teatype.logging import *
from teatype.modulo.units.socket import SocketUnit

class DemoSocketUnit(SocketUnit):
    """
    Minimal runnable example showcasing multiple endpoints and handlers.
    """
    LOOPBACK_HOST='127.0.0.1'
    LOOPBACK_PORT=12345

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