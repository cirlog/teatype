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
from pprint import pprint
# Third-party imports
import pytest
from teatype.comms import http

##############
# Unit tests #
##############

# http

def test_tresponse():
    # Unit tests
    tresponse = http.TResponse(
        content={'key': 'value'},
        headers={'Content-Type': 'application/json'},
        status_code=200
    )
    assert tresponse.data == {'key': 'value'}
    assert tresponse.content == {'key': 'value'}
    assert tresponse.headers == {'Content-Type': 'application/json'}
    assert tresponse.status == 200
    assert tresponse.status_code == 200

# celery

# redis

#####################
# Integration tests #
#####################