# Copyright (C) 2024-2025 Burak Günaydin
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

# Package imports
from teatype.modulo.base_units import ServiceUnit

# TODO: on first import, deploys, installs and launches the engine in the background (launches itself somehow)
#       then, on subsequent imports, connects to the already running engine instance
#       and provides a client interface to interact with it
#       this way, the engine is only started once and can be reused across multiple scripts or sessions
#       communicate via redis messages
class BaseAIEngine(ServiceUnit):
    def __init__(self):
        super().__init__(name='ai-engine')