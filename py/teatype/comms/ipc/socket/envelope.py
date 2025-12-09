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

"""
@startuml
    actor Unit
    participant SocketUnit
    participant SocketServiceManager as Manager
    participant SocketClientWorker as Client
    participant FrameBuilder
    participant RemoteServer as Server

    Unit -> SocketUnit: send_socket_message(receiver, header, body)
    SocketUnit -> Manager: send()
    Manager -> Client: emit(envelope)
    Client -> FrameBuilder: size_probe(envelope,len(payload))
    FrameBuilder --> Client: pickled probe
    Client -> Server: send probe
    Server --> Client: ACK (OK)
    Client -> Server: send payload bytes
    note right of Client: handles retries/logging\nand reconnection failures
@enduml

@startuml
    participant RemoteClient as Client
    participant SocketServerWorker as Server
    participant SocketSession as Session
    participant SocketServiceManager as Manager
    participant Handler
    note over Server,Session: Server created via\nregister_socket_server()

    Client -> Server: connect + size_probe
    Server -> Session: spawn session thread
    Session -> Client: ACK (OK)
    Client -> Session: payload bytes
    Session -> Session: pickle.loads → message
    Session -> Manager: handler(payload, address)
    Manager -> Handler: call @socket_handler(...)
    Handler --> Manager: business logic
    Session -> Client: optional close_signal()
@enduml
"""

# Standard-library imports
import pickle
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Third-party imports
from teatype.toolkit import generate_id

@dataclass
class SocketEnvelope:
    """
    Serializable container following the header/body contract.
    
    This class provides a standardized way to package data for socket communication.
    It separates metadata (header) from the actual payload (body), allowing for
    flexible message routing and processing.
    
    Attributes:
        header: Dictionary containing metadata such as receiver, source, method,
                content type, status, and unique message ID.
        body: The actual payload data that can be of any type.
    """
    # Dictionary to store metadata about the message (routing, status, ID, etc.)
    header:Dict[str,Any]=field(default_factory=dict)
    # The actual data payload, can be any Python object
    body:Any=None

    def normalize(self, receiver:str, source:Optional[str]=None) -> None:
        """
        Populate header with default values if not already set.
        
        This method ensures all required header fields exist with sensible defaults,
        making the envelope ready for transmission. It uses setdefault to avoid
        overwriting existing values.
        
        Args:
            receiver: The intended recipient identifier for this message.
            source: Optional sender identifier. If provided, will be added to header.
        """
        # Set the receiver field - identifies who should process this message
        self.header.setdefault('receiver', receiver)
        # Only set source if explicitly provided by caller
        if source:
            # Set the source field - identifies where this message originated from
            self.header.setdefault('source', source)
        # Set default method to 'payload' indicating a data transfer message
        self.header.setdefault('method', 'payload')
        # Set default content type to 'bytes' indicating binary data
        self.header.setdefault('content', 'bytes')
        # Set initial status to 'pending' indicating message hasn't been processed yet
        self.header.setdefault('status', 'pending')
        # Generate a unique 16-character ID for tracking this message
        self.header.setdefault('id', generate_id(truncate=16))

    @property
    def id(self) -> str:
        """
        Retrieve the unique identifier for this envelope.
        
        This property provides convenient access to the message ID stored in the
        header without requiring direct dictionary access.
        
        Returns:
            The message ID string, or None if no ID has been set.
        """
        # Extract and return the 'id' value from the header dictionary
        return self.header.get('id')

    def serialize(self) -> bytes:
        """
        Convert the envelope to bytes for transmission over a socket.
        
        This method uses pickle to serialize both the header and body into a single
        byte stream that can be sent over a network socket. The resulting bytes can
        be deserialized on the receiving end to reconstruct the envelope.
        
        Returns:
            Serialized byte representation of the envelope containing both header and body.
        """
        # Create a dictionary with header and body, then pickle it to bytes
        return pickle.dumps({'header': self.header, 'body': self.body})