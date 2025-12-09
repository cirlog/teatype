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
import sys
import time

# Third-party imports
from teatype.comms.ipc.socket.protocol import SocketClientWorker, SocketEnvelope
from teatype.logging import *

host = 'localhost'
port = 9050
# Create client worker (reuses server name for demo simplicity)
client = SocketClientWorker('demo-server', host, port)
# Attempt to connect to server
if not client.connect():
    err('Demo client failed to connect to server')
    sys.exit(1)
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