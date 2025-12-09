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
from typing import Callable, Optional

def socket_handler(endpoint:Optional[str]=None):
    """
    Decorator used by units to register socket handlers.
    
    This decorator marks methods as socket message handlers for specific endpoints.
    When applied to a method, it tags the function with metadata that the
    SocketServiceManager can discover during autowiring.
    
    Args:
        endpoint: The endpoint name to handle. If None, defaults to '*' (all endpoints).
    
    Returns:
        The decorated function with added metadata.
    
    Example:
        @socket_handler('data_channel')
        def handle_data(self, envelope, **kwargs):
            pass
    """
    def decorator(function: Callable):
        # Store the endpoint target as metadata on the function object
        # This allows autowire() to discover which endpoints this handler services
        setattr(function, '_socket_handler_target', endpoint or '*')
        return function
    return decorator