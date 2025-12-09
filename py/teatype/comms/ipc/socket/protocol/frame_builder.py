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
import pickle

# Third-party imports
from teatype.comms.ipc.socket.envelope import SocketEnvelope
from teatype.logging import *
from teatype.toolkit import generate_id

class FrameBuilder:
    """
    Utility class for constructing protocol-level framing messages.
    
    This class provides static methods to build control frames used in the
    socket communication protocol, including size probes and connection
    termination signals.
    """
    @staticmethod
    def size_probe(envelope:SocketEnvelope, payload_length:int) -> bytes:
        """
        Create a size probe frame to notify the receiver of incoming payload size.
        
        Args:
            envelope: The original envelope being sent
            payload_length: Size of the serialized payload in bytes
            
        Returns:
            Pickled bytes representing the size probe frame
        """
        # Construct a control frame with the payload size in the body
        probe = {
            'header': {
                'content': 'bytes', # Indicates content type
                'method': 'size_of', # Method identifier for size probe
                'id': envelope.id, # Preserve original envelope ID for tracking
                'status': 'pending', # Indicate awaiting acknowledgment
                'receiver': envelope.header['receiver'] # Target receiver name
            },
            'body': payload_length # Actual size information
        }
        # Serialize the probe using pickle for transmission
        return pickle.dumps(probe)

    @staticmethod
    def close_signal(receiver: str) -> bytes:
        """
        Create a graceful connection termination signal.
        
        Args:
            receiver: Name of the connection endpoint to close
            
        Returns:
            Pickled bytes representing the close signal frame
        """
        # Construct a control frame indicating connection closure
        payload = {
            'header': {
                'content': 'string', # Content type for text message
                'method': 'close_socket', # Method identifier for close operation
                'id': generate_id(truncate=12), # Generate unique ID for this frame
                'status': 'closing', # Indicate connection termination state
                'receiver': receiver # Target receiver name
            },
            'body': 'Closing connection' # Human-readable message
        }
        # Serialize the close signal using pickle
        return pickle.dumps(payload)