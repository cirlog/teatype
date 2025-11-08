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
import time
from pprint import pprint

# Third-party imports
import pytest
from teatype.modulo import Launchpad

##########
# PyTest #
##########

@pytest.mark.skip()
def test_redis_toolkit():
    launch_pad = Launchpad()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass