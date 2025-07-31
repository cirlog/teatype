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

# From package imports
from rest_framework import status
from rest_framework.response import Response

# Content type for JSON responses
CONTENT_TYPE = 'application/json'

# 2XX responses
def Accepted(data:object):
    """
    Return a response with HTTP 202 Accepted status.
    """
    return Response(data, status.HTTP_202_ACCEPTED, content_type=CONTENT_TYPE)

def Created(data:object):
    """
    Return a response with HTTP 201 Created status.
    """
    return Response(data, status.HTTP_201_CREATED, content_type=CONTENT_TYPE)

def EmptySuccess():
    """
    Return a response with HTTP 204 No Content status.
    """
    return Response(status=status.HTTP_204_NO_CONTENT, content_type=CONTENT_TYPE)

def Success(data:object):
    """
    Return a response with HTTP 200 OK status.
    """
    return Response(data, status.HTTP_200_OK, content_type=CONTENT_TYPE)

# 4XX responses
def BadRequest(error:any):
    """
    Return a response with HTTP 400 Bad Request status.
    """
    return Response({'error': error}, status.HTTP_400_BAD_REQUEST, content_type=CONTENT_TYPE)

def Conflict(error:any):
    """
    Return a response with HTTP 409 Conflict status.
    """
    return Response({'error': error}, status.HTTP_409_CONFLICT, content_type=CONTENT_TYPE)

def Forbidden(error:any):
    """
    Return a response with HTTP 403 Forbidden status.
    """
    return Response({'error': error}, status.HTTP_403_FORBIDDEN, content_type=CONTENT_TYPE)

def Gone(error:any):
    """
    Return a response with HTTP 410 Gone status.
    """
    return Response({'error': error}, status.HTTP_410_GONE, content_type=CONTENT_TYPE)

def NotAcceptable(error:any):
    """
    Return a response with HTTP 406 Not Acceptable status.
    """
    return Response({'error': error}, status.HTTP_406_NOT_ACCEPTABLE, content_type=CONTENT_TYPE)

def NotAllowed(error:any, allowed_methods):
    """
    Return a response with HTTP 405 Method Not Allowed status.
    """
    response = Response({'error': error}, status.HTTP_405_METHOD_NOT_ALLOWED, content_type=CONTENT_TYPE)
    response['Allow'] = ', '.join(map(str, allowed_methods))
    return response

def NotFound(error:any):
    """
    Return a response with HTTP 404 Not Found status.
    """
    return Response({'error': error}, status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)

def Unauthorized(error:any):
    """
    Return a response with HTTP 401 Unauthorized status.
    """
    return Response({'error': error}, status.HTTP_401_UNAUTHORIZED, content_type=CONTENT_TYPE)

# 5XX responses
def BadGateway(error:any):
    """
    Return a response with HTTP 502 Bad Gateway status.
    """
    return Response({'error': error}, status.HTTP_502_BAD_GATEWAY, content_type=CONTENT_TYPE)

def GatewayTimeout(error:any):
    """
    Return a response with HTTP 504 Gateway Timeout status.
    """
    return Response({'error': error}, status.HTTP_504_GATEWAY_TIMEOUT, content_type=CONTENT_TYPE)

def NotImplemented(error:any):
    """
    Return a response with HTTP 501 Not Implemented status.
    """
    return Response({'error': error}, status.HTTP_501_NOT_IMPLEMENTED, content_type=CONTENT_TYPE)

def ServerError(error:any):
    """
    Return a response with HTTP 500 Internal Server Error status.
    """
    return Response({'error': error}, status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

def ServiceUnavailable(error:any):
    """
    Return a response with HTTP 503 Service Unavailable status.
    """
    return Response({'error': error}, status.HTTP_503_SERVICE_UNAVAILABLE, content_type=CONTENT_TYPE)