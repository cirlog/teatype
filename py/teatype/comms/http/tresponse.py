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

# Standard-library imports
import json as json_util

class TResponse:
    """
    Conversion class to represent an HTTP response object.
    Allows both attribute-style and dict-style access to JSON payload.
    Has proxies for response.status_code and response.content, but keeps the originals as well for backwards-compatibility.
    """
    content:any
    data:any
    headers:dict
    ok:bool
    status:int
    status_code:int
    
    def __init__(self,
                 content:any,
                 headers:dict,
                 status_code:int,
                 parse_json:bool=True):
        self.content = content
        self.headers = headers
        self.status = status_code
        self.status_code = status_code
        
        self.ok = 200 <= status_code < 300
        
        if type(content) == bytes or type(content) == bytearray:
            content = content.decode('utf-8')
        if type(content) == str and parse_json:
            content = json_util.loads(content)
        if type(content) == dict:
            self.data = TResponse._AttrDict(content)
        else:
            self.data = content

    class _AttrDict(dict):
        """
        A dict subclass that exposes keys as attributes.
        Falls back to normal dict.get() when needed.
        """
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(f"No such attribute: {name}")

        def __setattr__(self, name, value):
            self[name] = value

        def __delattr__(self, name):
            try:
                del self[name]
            except KeyError:
                raise AttributeError(f"No such attribute: {name}")
            
    @property
    def fastapi(self):
        """
        Converts to FastAPI Response object.
        """
        try:
            from fastapi import Response
            return Response(
                content=json_util.dumps(self.data),
                status_code=self.status,
                headers=self.headers
            )
        except:
            raise ImportError("FastAPI is not installed.")