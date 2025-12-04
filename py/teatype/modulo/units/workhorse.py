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

# Third-party imports
from teatype.modulo.units.core import CoreUnit

class WorkhorseUnit(CoreUnit):
    """
    Lightweight one-shot worker unit for specialized tasks within the Teatype Modulo framework.
    """
    def __init__(self, name:str) -> None:
        """
        Initialize the workhorse unit.
        
        Args:
            name: Name of the workhorse unit
        """
        super().__init__(name=name)