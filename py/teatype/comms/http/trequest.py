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
import json as json_util
from enum import Enum
from typing import List
# Third-party imports
import aiohttp
import requests
import urllib3
from teatype.comms.http.tresponse import TResponse
from teatype.logging import *
from teatype.toolkit import stopwatch
from urllib.parse import urlparse

class _CRUD_METHOD(Enum):
    """
    Enumeration of CRUD HTTP methods.
    """
    DELETE='DELETE'
    GET='GET'
    PATCH='PATCH'
    POST='POST'
    PUT='PUT'
    
def _request(async_client:aiohttp.ClientSession,
             crud_method:str,
             data:any,
             force_json:bool,
             headers:dict,
             measure_time:bool,
             parse_json:bool,
             params:dict,
             timeout:float,
             url:str|List[str],
             verbose:bool=False,
             verify_ssl:bool=False) -> TResponse|aiohttp.ClientResponse|None:
    """
    Internal helper function to perform HTTP requests based on CRUD methods.

    Args:
        async_client (aiohttp.ClientSession, optional): Async HTTP session for asynchronous requests.
        crud_method (str): The CRUD method (DELETE, GET, PATCH, POST, PUT).
        data (any, optional): The data to include in the request body.
        force_json (bool, optional): Whether to force the request to use JSON format.
        headers (dict, optional): Headers to include in the request.
        measure_time (str, optional): Label to measure the time taken for the request.
        params (dict, optional): Query parameters to include in the request URL.
        parse_json (bool, optional): Whether to parse the response as JSON.
        timeout (float, optional): Timeout for the request in seconds.
        url (str): The URL to send the request to.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
        verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to True.

    Returns:
        TResponse or aiohttp.ClientResponse or None: The HTTP response object or None if an error occurs.
    """
    if not isinstance(url, str) and not isinstance(url, list):
        err('Invalid URL type, expected str or list')
        return None
    
    if isinstance(url, list):
        url = '/'.join(url) # Join the list of URLs into a single string
    
    # Parse the request URL to validate its structure
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        err(f'Invalid URL: {url}') # Log an error if URL is invalid
        return None

    request_label = f'{crud_method} {url}'
    # Start the stopwatch if a measure time is specified for performance tracking
    if measure_time:
        # Set the request data to an empty dictionary if not provided
        stopwatch(request_label)
        
    if data is not None and isinstance(data, dict):
        force_json = True
    if force_json:
        # If force_json is True, set the headers to accept JSON
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        # Convert data to JSON format if provided
        if data is not None:
            data = json_util.dumps(data)
            
    if not verify_ssl:
        urllib3.disable_warnings()
    
    url = url.strip() # Clean up the URL by stripping whitespace
    url = url.replace('0.0.0.0', 'localhost')

    # Determine whether to use synchronous requests or the provided async session
    call = requests if not async_client else async_client
    # Match the CRUD method to perform the corresponding HTTP request
    match crud_method:
        case _CRUD_METHOD.DELETE.value:
            # Perform a DELETE request
            # WARNING FIXME: SUPER DO NOT DO THIS IN PRODUCTION CODE, ADD SSL VERIFICATION FUNCTION VARIABLE, FOR NOW, DEFAULT
            response = call.delete(url, data=data, params=params, headers=headers, timeout=timeout, verify=verify_ssl)
        case _CRUD_METHOD.GET.value:
            if data:
                # Maybe construct a response instead?
                err('GET requests do not support request data')
                return None
            # Perform a GET request
            response = call.get(url, params=params, headers=headers, timeout=timeout, verify=verify_ssl)
        case _CRUD_METHOD.PATCH.value:
            # Perform a PATCH request
            response = call.patch(url, data=data, params=params, headers=headers, timeout=timeout, verify=verify_ssl)
        case _CRUD_METHOD.POST.value:
            # Perform a POST request
            response = call.post(url, data=data, params=params, headers=headers, timeout=timeout, verify=verify_ssl)
        case _CRUD_METHOD.PUT.value:
            # Perform a PUT request
            response = call.put(url, data=data, params=params, headers=headers, timeout=timeout, verify=verify_ssl)
        case _:
            err(f'Invalid CRUD method: {crud_method}') # Log an error for invalid CRUD methods
            return None

    if verbose:
        if not async_client:
            # Log the type of request and the target URL for debugging purposes
            log(f'Synchronous request: {request_label}')
        else:
            log(f'Asynchronous request: {request_label}')

    # Stop the stopwatch if a measure time was specified
    if measure_time:
        stopwatch()

    # Retrieve the response content based on the json flag
    tresponse = TResponse(response.content,
                          response.headers,
                          response.status_code,
                          parse_json)
    # If verbose logging is enabled, log the result of the request
    if verbose:
        if tresponse.status >= 400:
            err(f'Synchronous request failed: [{tresponse.status}] {tresponse.data}') # Log failure
        else:
            log(f'Synchronous request success: [{tresponse.status}] {tresponse.data}') # Log success
    return tresponse # Return the HTTP response object

def sync_request(crud_method:str,
                 url:str,
                 data:any=None,
                 headers:dict={},
                 params:dict=None,
                 force_json:bool=False,
                 measure_time:bool=False,
                 parse_json:bool=True,
                 timeout:float=10.0,
                 verbose:bool=False,
                 verify_ssl:bool=True) -> TResponse:
    """
    Perform a synchronous HTTP request based on the specified CRUD method.
    This exists as a wrapper function to call the internal _request function and it allows
    dynamic selection of the CRUD method to use for testing or debugging purposes.
    
    Args:
        crud_method (str): The CRUD method (DELETE, GET, PATCH, POST, PUT).
        url (str): The URL to send the request to.
        headers (dict, optional): Headers to include in the request. Defaults to an empty dictionary.
        params (dict, optional): Query parameters to include in the request URL. Defaults to None.
        force_json (bool, optional): Whether to force the request to use JSON format. Defaults to False.
        measure_time (str, optional): Label to measure the time taken for the request. Defaults to None.
        parse_json (bool, optional): Whether to parse the response as JSON. Defaults to False.
        timeout (float, optional): Timeout for the request in seconds. Defaults to 10.0.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

    Returns:
        TResponse or aiohttp.ClientResponse or None: The HTTP response object or None if an error occurs.
    """
    # Call the internal _request function with the provided parameters to perform the synchronous request
    return _request(async_client=None,
                    crud_method=crud_method,
                    url=url,
                    data=data,
                    headers=headers,
                    params=params,
                    force_json=force_json,
                    measure_time=measure_time,
                    parse_json=parse_json,
                    timeout=timeout,
                    verbose=verbose)

def get(url:str,
        headers:dict={},
        params:dict=None,
        measure_time:bool=False,
        parse_json:bool=True,
        timeout:float=10.0,
        verbose:bool=False,
        verify_ssl:bool=True) -> TResponse:
    """
    Perform a synchronous GET request.
    
    Args:
        url (str): The URL to send the request to.
        headers (dict, optional): Headers to include in the request. Defaults to an empty dictionary.
        params (dict, optional): Query parameters to include in the request URL. Defaults to None.
        measure_time (str, optional): Label to measure the time taken for the request. Defaults to None.
        parse_json (bool, optional): Whether to parse the response as JSON. Defaults to False.
        timeout (float, optional): Timeout for the request in seconds. Defaults to 10.0.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

    Returns:
        TResponse or aiohttp.ClientResponse or None: The HTTP response object or None if an error occurs.
    """
    return sync_request(_CRUD_METHOD.GET.value,
                        url=url,
                        data=None,
                        headers=headers,
                        params=params,
                        force_json=False,
                        measure_time=measure_time,
                        parse_json=parse_json,
                        timeout=timeout,
                        verbose=verbose)

def post(url:str,
         data:any=None,
         headers:dict={},
         params:dict=None,
         force_json:bool=False,
         measure_time:bool=False,
         parse_json:bool=True,
         timeout:float=10.0,
         verbose:bool=False,
         verify_ssl:bool=True) -> TResponse:
    """
    Perform a synchronous POST request.
    
    Args:
        url (str): The URL to send the request to.
        headers (dict, optional): Headers to include in the request. Defaults to an empty dictionary.
        params (dict, optional): Query parameters to include in the request URL. Defaults to None.
        force_json (bool, optional): Whether to force the request to use JSON format. Defaults to False.
        measure_time (str, optional): Label to measure the time taken for the request. Defaults to None.
        parse_json (bool, optional): Whether to parse the response as JSON. Defaults to False.
        timeout (float, optional): Timeout for the request in seconds. Defaults to 10.0.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

    Returns:
        TResponse or aiohttp.ClientResponse or None: The HTTP response object or None if an error occurs.
    """
    return sync_request(_CRUD_METHOD.POST.value,
                        url=url,
                        data=data,
                        headers=headers,
                        params=params,
                        force_json=force_json,
                        measure_time=measure_time,
                        parse_json=parse_json,
                        timeout=timeout,
                        verbose=verbose)

def put(url:str,
        data:any=None,
        headers:dict={},
        params:dict=None,
        force_json:bool=False,
        measure_time:bool=False,
        parse_json:bool=True,
        timeout:float=10.0,
        verbose:bool=False,
        verify_ssl:bool=True) -> TResponse:
    """
    Perform a synchronous PUT request.
    
    Args:
        url (str): The URL to send the request to.
        headers (dict, optional): Headers to include in the request. Defaults to an empty dictionary.
        params (dict, optional): Query parameters to include in the request URL. Defaults to None.
        force_json (bool, optional): Whether to force the request to use JSON format. Defaults to False.
        measure_time (str, optional): Label to measure the time taken for the request. Defaults to None.
        parse_json (bool, optional): Whether to parse the response as JSON. Defaults to False.
        timeout (float, optional): Timeout for the request in seconds. Defaults to 10.0.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

    Returns:
        TResponse or aiohttp.ClientResponse or None: The HTTP response object or None if an error occurs.
    """
    return sync_request(_CRUD_METHOD.PUT.value,
                        url=url,
                        data=data,
                        headers=headers,
                        params=params,
                        force_json=force_json,
                        measure_time=measure_time,
                        parse_json=parse_json,
                        timeout=timeout,
                        verbose=verbose)
    
def patch(url:str,
          data:any=None,
          headers:dict={},
          params:dict=None,
          force_json:bool=False,
          measure_time:bool=False,
          parse_json:bool=True,
          timeout:float=10.0,
          verbose:bool=False,
          verify_ssl:bool=True) -> TResponse:
    """
    Perform a synchronous PATCH request.
    
    Args:
        url (str): The URL to send the request to.
        headers (dict, optional): Headers to include in the request. Defaults to an empty dictionary.
        params (dict, optional): Query parameters to include in the request URL. Defaults to None.
        force_json (bool, optional): Whether to force the request to use JSON format. Defaults to False.
        measure_time (str, optional): Label to measure the time taken for the request. Defaults to None.
        parse_json (bool, optional): Whether to parse the response as JSON. Defaults to False.
        timeout (float, optional): Timeout for the request in seconds. Defaults to 10.0.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

    Returns:
        TResponse or aiohttp.ClientResponse or None: The HTTP response object or None if an error occurs.
    """
    return sync_request(_CRUD_METHOD.PATCH.value,
                        url=url,
                        data=data,
                        headers=headers,
                        params=params,
                        force_json=force_json,
                        measure_time=measure_time,
                        parse_json=parse_json,
                        timeout=timeout,
                        verbose=verbose)

def delete(url:str,
           data:any=None,
           headers:dict={},
           params:dict=None,
           force_json:bool=False,
           measure_time:bool=False,
           parse_json:bool=True,
           timeout:float=10.0,
           verbose:bool=False,
           verify_ssl:bool=True) -> TResponse:
    """
    Perform a synchronous DELETE request.
    
    Args:
        url (str): The URL to send the request to.
        headers (dict, optional): Headers to include in the request. Defaults to an empty dictionary.
        params (dict, optional): Query parameters to include in the request URL. Defaults to None.
        force_json (bool, optional): Whether to force the request to use JSON format. Defaults to False.
        measure_time (str, optional): Label to measure the time taken for the request. Defaults to None.
        parse_json (bool, optional): Whether to parse the response as JSON. Defaults to False.
        timeout (float, optional): Timeout for the request in seconds. Defaults to 10.0.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

    Returns:
        TResponse or aiohttp.ClientResponse or None: The HTTP response object or None if an error occurs.
    """
    return sync_request(_CRUD_METHOD.DELETE.value,
                        url=url,
                        data=data,
                        headers=headers,
                        params=params,
                        force_json=force_json,
                        measure_time=measure_time,
                        parse_json=parse_json,
                        timeout=timeout,
                        verbose=verbose)

async def async_request(url:str,
                        crud_method:str,
                        data:any=None,
                        force_json:bool=True,
                        headers:dict={},
                        measure_time:bool=False,
                        params:dict=None,
                        timeout:float=10.0,
                        verbose:bool=False,
                        verify_ssl:bool=True) -> aiohttp.ClientResponse:
    """
    Perform an asynchronous HTTP request based on the specified CRUD method.
    """
    async with aiohttp.ClientSession() as session:
        async with _request(
            async_client=session,
            crud_method=crud_method,
            data=data,
            force_json=force_json,
            headers=headers,
            measure_time=measure_time,
            params=params,
            timeout=timeout,
            url=url,
            verbose=verbose,
            verify_ssl=verify_ssl
        ) as response:
            return response

def async_get(url:str,
              # Convenient placements
              params:dict=None,
              headers:dict={},
              # Ordered placements
              force_json:bool=True,
              measure_time:bool=False,
              timeout:float=10.0,
              verbose:bool=False,
              verify_ssl:bool=True) -> aiohttp.ClientResponse:
    """
    Perform an asynchronous GET request.
    """
    # Call the internal _async_request function with the provided parameters to perform the asynchronous GET request
    return async_request(crud_method=_CRUD_METHOD.GET.value,
                         url=url,
                         data=None,
                         params=params,
                         force_json=force_json,
                         measure_time=measure_time,
                         verbose=verbose,
                         headers=headers,
                         timeout=timeout,
                         verify_ssl=verify_ssl)