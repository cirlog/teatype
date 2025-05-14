# Copyright (c) 2024-2025 enamentis GmbH. All rights reserved.
#
# This software module is the proprietary property of enamentis GmbH.
# Unauthorized copying, modification, distribution, or use of this software
# is strictly prohibited unless explicitly authorized in writing.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THIS SOFTWARE.
# 
# For more details, check the LICENSE file in the root directory of this repository.

# System imports
import random

# From system imports
from functools import wraps
from typing import Callable, Dict, Optional

# From package imports
from teatype.io import probe
from teatype.logging import err

try:
    fastapi_support = probe.package('fastapi')
    # From package imports
    from fastapi import Request, Response
except:
    fastapi_support = None

# TODO: Generalize so that you don't need fastapi support
# TODO: Change testmode to parameter that tells you what should happen instead of simple true/false
class Deadpoint:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of the class exists.
        """
        if not fastapi_support:
            err('FastAPI not installed, skipping middleware registration.')
            return
        
        if not cls._instance:
            cls._instance = super(Deadpoint, cls).__new__(cls, *args, **kwargs)
            cls._instance.fail_conditions = []
            cls._instance.predefined_responses = {}
            cls._instance.randomized_responses = {}
        return cls._instance

    def add_fail_condition(self, condition:Callable[[Request],bool], response:dict) -> None:
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

    def check_fail_conditions(self, request:Request) -> Optional[dict]:
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

    def simulate_endpoint(self, request:Request, path:str) -> dict:
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

def deadpoint(response:Dict[str,any]=None, status:int=None):
    """ 
    A decorator that checks for 'testmode' query param and delegates 
    the request to the EndpointSimulator with the specified response and status code.
    """
    def decorator(callable:Callable):
        @wraps(callable)
        def wrapper(caller:object,
                          initial_request:Request,
                          initial_response:Response,
                          *args,
                          **kwargs):
            try:
                # Access the 'testmode' query parameter directly from the request, so that it can
                # be omitted in the call signature of the route handler
                testmode = initial_request.query_params.get('testmode', 'false').lower() == 'true'
                
                # Check if testmode is enabled in the query parameters
                if testmode:
                    if response is None:
                        # Delegate the request to the singleton instance of the endpoint simulator
                        response.content = Deadpoint().simulate_endpoint(initial_request, initial_request.url.path)
                    else:
                        response.content = response
                    # Set the response status code
                    response.status_code = status
                    # Modify the response body
                    response.headers['Content-Type'] = 'application/json'
                    return response
                # If not testmode, proceed with the actual callable
                # Ensure to pass all necessary arguments (request, response)
                return callable(caller, initial_request, initial_response, *args, **kwargs)
            except:
                import traceback
                traceback.print_exc()
        return wrapper
    return decorator