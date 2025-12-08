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
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Third-party imports
from teatype.toolkit import generate_id

@dataclass
class SocketEnvelope:
    """
    Serializable container following the header/body contract.
    """
    header:Dict[str,Any]=field(default_factory=dict)
    body:Any=None

    def normalize(self, receiver:str, source:Optional[str]=None) -> None:
        self.header.setdefault('receiver', receiver)
        if source:
            self.header.setdefault('source', source)
        self.header.setdefault('method', 'payload')
        self.header.setdefault('content', 'bytes')
        self.header.setdefault('status', 'pending')
        self.header.setdefault('id', generate_id(truncate=16))

    @property
    def request_id(self) -> str:
        return self.header['id']

    def dump(self) -> bytes:
        return pickle.dumps({'header': self.header, 'body': self.body})