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
from collections import deque
from datetime import datetime

# Third-party imports
from teatype.enum import XTerm

MAX_HISTORY_SIZE = 10000

LEVEL_COLORS = {
    'DEBUG': XTerm.GRAY,
    'ERROR': XTerm.RED,
    'HINT': XTerm.CYAN,
    'INFO': None,
    'ITERATE': XTerm.GRAY,
    'ROUTINE': XTerm.LIGHT_BLUE,
    'SCHEDULE': XTerm.MAGENTA,
    'SUCCESS': XTerm.GREEN,
    'WARN': XTerm.YELLOW,
}

class History:
    """
    Thread-safe, size-capped and printed log of everything a Tracer does.
    """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._log = deque(maxlen=MAX_HISTORY_SIZE)
    
    def __str__(self) -> str:
        with self._lock:
            return '\n'.join(self._log)
    
    def push(self, message:str, level:str='INFO') -> None:
        timestamp = f'{XTerm.GRAY}[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]{XTerm.RESET}'
        color = LEVEL_COLORS.get(level)
        entry = f'{timestamp} {color}{level} - {message}{XTerm.RESET}' if color else f'{timestamp} {level} - {message}'
        
        with self._lock:
            self._log.append(entry)
        print(entry)
    
    def size(self) -> int:
        with self._lock:
            return len(self._log)