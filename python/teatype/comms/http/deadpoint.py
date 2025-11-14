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
import random
from copy import deepcopy
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, Optional
# Third-party imports
from teatype.comms.http import TResponse
from teatype.logging import *
from teatype.io import probe

try:
    fastapi_support = probe.package('fastapi')
    if fastapi_support:
        from fastapi import Response
    
    # TODO: Change testmode to parameter that tells you what should happen instead of simple true/false
    class Deadpoint:
        _instance = None

        def __new__(cls, *args, **kwargs):
            """
            Ensures only one instance of the class exists.
            """
            if not cls._instance:
                cls._instance = super(Deadpoint, cls).__new__(cls, *args, **kwargs)
                cls._instance.fail_conditions = []
                cls._instance.predefined_responses = {}
                cls._instance.randomized_responses = {}
            return cls._instance

        def add_fail_condition(self, condition:Callable[[object],bool], response:dict) -> None:
            """
            Add a custom fail condition with a predefined response.
            """
            self.fail_conditions.append((condition, response))

        def add_predefined_response(self, path:str, response:dict) -> None:
            """
            Add a predefined response for a specific path.
            """
            self.predefined_responses[path] = response

        def add_randomized_response(self, path:str, response_options:list) -> None:
            """
            Add a list of randomized responses for a specific path.
            """
            self.randomized_responses[path] = response_options

        def check_fail_conditions(self, request) -> Optional[dict]:
            """
            Check if any fail conditions apply to the current request.
            """
            for condition, response in self.fail_conditions:
                if condition(request):
                    return response
            return None

        def get_randomized_response(self, path:str) -> Optional[dict]:
            """
            Get a randomized response for a given path if applicable.
            """
            if path in self.randomized_responses:
                return random.choice(self.randomized_responses[path])
            return None

        def simulate_endpoint(self, request, path:str) -> dict:
            """
            Simulate the endpoint logic with fail conditions, predefined responses, and randomized responses.
            """
            # Check if the request should fail
            fail_response = self.check_fail_conditions(request)
            if fail_response:
                return fail_response

            # Check if a predefined response exists for this path
            if path in self.predefined_responses:
                return self.predefined_responses[path]

            # Get a randomized response if available
            randomized_response = self.get_randomized_response(path)
            if randomized_response:
                return randomized_response

            # Default response if nothing matches
            return {'message': f'Default response for {path}'}
    
    def deadpoint(response_data:Optional[Dict[str,Any]]=None,
                  response_headers:Optional[Dict[str,str]]=None,
                  response_status:Optional[int]=None,
                  fast_api_response:bool=False):
        """
        Decorator that checks for 'testmode' query parameter and delegates
        the request to the EndpointSimulator with the specified response and status code.
        
        Args:
            response (Optional[Dict[str, Any]]): The predefined response to return in test mode.
            status (Optional[int]): The HTTP status code to return in test mode.
            
        Returns:
            Callable: The decorated function.
        """
        def decorator(function:Callable):
            def _testmode_response():
                pass
            
            if iscoroutinefunction(function):
                @wraps(function)
                async def async_wrapper(
                    caller:object,
                    initial_request,
                    initial_response,
                    *args,
                    **kwargs
                ):
                    testmode = initial_request.query_params.get('testmode', 'false').lower() == 'true'
                    if testmode:
                        payload = {
                            'content': deepcopy(response_data) if response_data is not None else Deadpoint().simulate_endpoint(initial_request, initial_request.url.path),
                            'headers': deepcopy(response_headers) if response_headers is not None else {},
                            'status_code': response_status if response_status is not None else 200
                        }
                        payload['headers'].setdefault('Content-Type', 'application/json')
                        tresponse = TResponse(**payload)
                        if fast_api_response and fastapi_support:
                            return tresponse.fastapi
                        return tresponse
                    # real call (async)
                    return await function(caller, initial_request, initial_response, *args, **kwargs)
                return async_wrapper
            else:
                @wraps(function)
                def sync_wrapper(
                    caller:object,
                    initial_request,
                    initial_response,
                    *args,
                    **kwargs
                ):
                    testmode = initial_request.query_params.get('testmode', 'false').lower() == 'true'
                    if testmode:
                        payload = {
                            'content': deepcopy(response_data) if response_data is not None else Deadpoint().simulate_endpoint(initial_request, initial_request.url.path),
                            'headers': deepcopy(response_headers) if response_headers is not None else {},
                            'status_code': response_status if response_status is not None else 200
                        }
                        payload['headers'].setdefault('Content-Type', 'application/json')
                        tresponse = TResponse(**payload)
                        if fast_api_response and fastapi_support:
                            return tresponse.fastapi
                        return tresponse
                    # real call (sync)
                    return function(caller, initial_request, initial_response, *args, **kwargs)
                return sync_wrapper
        return decorator
except ImportError:
    fastapi_support = None