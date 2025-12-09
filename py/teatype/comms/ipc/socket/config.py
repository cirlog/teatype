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

# Acknowledgment byte sequence sent by server to confirm receipt of size probe
ACKNOWLEDGE_MESSAGE = b'OK'

# Default size for socket read operations (4KB chunks)
DEFAULT_CHUNK_SIZE = 4096

# Default timeout in seconds for queue.get() operations
DEFAULT_QUEUE_TIMEOUT = 1.0