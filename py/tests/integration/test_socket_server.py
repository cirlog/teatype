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
import time
from typing import Tuple

# Third-party imports
from teatype.comms.ipc.socket.protocol import SocketServerWorker
from teatype.logging import *

def handler(message:dict, address:Tuple[str,int]) -> None:
    """
    Simple handler that logs received messages.
    """
    log(f'[server] Received payload from {address}: {message}')
    println()

println()
# Create and start server worker
host = 'localhost'
port = 9051
server = SocketServerWorker('demo-server', host, port, handler)
server.start()
println()
hint(f'Demo server ready on {host}:{port}. Press Ctrl+C to stop.', include_symbol=True, use_prefix=False)
try:
    # Keep main thread alive
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # User requested shutdown
    warn('Stopping demo server ...', include_symbol=True, use_prefix=False)
finally:
    # Clean shutdown
    server.stop()
    # Wait for server thread to terminate
    server.join(timeout=2)
println()