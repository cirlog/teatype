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

# Standard library imports
from enum import Enum

class RedisChannel(Enum):
    ALERTS='channel:alerts' # System alerts and critical notifications
    COMMANDS='channel:commands' # Commands sent to modulos for execution
    COMMS='channel:comms' # Bi-directional communication channel for modulo that enforce request-response patterns
    NOTIFICATIONS='channel:notifications' # General notifications and informational messages
    SYSTEM_STATUS='channel:status:system' # System-wide status updates
    UNIT_STATUS='channel:status:unit' # Status updates specific to individual modulo