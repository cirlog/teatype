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

# System imports
import re
import traceback

# From system imports
from abc import ABCMeta
from typing import List, Type

# From package imports
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView
from teatype.hsdb import HybridStorage
from teatype.util import kebabify
from teatype.web.django_support.responses import NotAllowed, ServerError, Success

_COLLECTION_METHODS=['GET', 'POST']
_DATA_REQUIRED_METHODS=['POST', 'PUT', 'PATCH']
_RESOURCE_METHODS=['GET', 'PUT', 'PATCH', 'DELETE']

# TODO: Create a seperate base class without hsdb support
# TODO: Check if request method is implemented without auto_view
class HSDBDjangoView(APIView):
    __metaclass__:ABCMeta=ABCMeta
    api_parents:List[str]=[]
    auto_view=True
    data_key:str=None # TODO: Automate data key as well and allow overwriting
    is_collection:bool
    hsdb_model:Type=None
    overwrite_api_name:str=None
    overwrite_api_plural_name:str=None
    overwrite_api_path:str=None
    
    @property
    def allowed_methods(self) -> List[str]:
        if self.is_collection:
            return [method for method in dir(self) if method in _COLLECTION_METHODS]
        return [method for method in dir(self) if method in _RESOURCE_METHODS]

    def _auto_method(self, request, kwargs):
        try:
            if not self.auto_view:
                raise NotImplementedError(f'Auto mode is off, you need to implement the {request.method} method yourself.')

            if self.hsdb_model is None:
                raise ValueError('Can\' use auto mode without specifying a hsdb_model in view')
            
            if request.method in _DATA_REQUIRED_METHODS:
                if not request.data:
                    return NotAllowed(f'Data is required for {request.method} requests')
                
                if self.data_key not in request.data:
                    return NotAllowed(f'Data key {self.data_key} is required for {request.method} requests')
                
                data = request.data[self.data_key]
            
            hybrid_storage = HybridStorage.instance()
            match request.method:
                case 'GET':
                    if self.is_collection:
                        query_response = hybrid_storage.get_entries(self.hsdb_model, serialize=True)
                    else:
                        id = kwargs.get(self.api_id())
                        query_response = hybrid_storage.get_entry(id, serialize=True)
                case 'POST':
                    query_response = hybrid_storage.create_entry(self.hsdb_model, data)
                    if query_response is None:
                        return ServerError('Entry already exists')
                # case 'PUT':
                #     query_response = hybrid_storage.create_entry()
                # case 'PATCH':
                #     query_response = hybrid_storage.modify_entry()
                # case 'DELETE':
                #     query_response = hybrid_storage.delete_entry()
            # TODO: Implement proper query_response handling
            if query_response is not None:
                return Success(query_response)
            else:
                query_response_error = 'Query-response was "None"'
                print(query_response_error)
                return ServerError({'message': query_response_error})
        except Exception as exc:
            traceback.print_exc()
            return ServerError(exc)
    
    # TODO: Figure out how to make these work as properties
    def api_id(self) -> str:
        parsed_name = kebabify(type(self).__name__)
        return f'{parsed_name}_id'
    
    def api_name(self) -> str:
        if self.overwrite_api_name:
            return self.overwrite_api_name
        return kebabify(type(self).__name__)
    
    def api_plural_name(self) -> str:
        api_name = self.api_name()
        if self.is_collection:
            return api_name
        return api_name + 's' if not api_name.endswith('s') else api_name
        # return api_name + 's' if not api_name.endswith('s') else api_name + 'es'
    
    # TODO: consider api parents
    def api_path(self) -> str:
        if self.overwrite_api_path:
            return self.overwrite_api_path
        
        parsed_name = kebabify(type(self).__name__)
        if self.is_collection:
            return f'/{parsed_name}'
        return f'/{self.api_plural_name()}/<str:{self.api_id()}>'

    def initial(self, request, *args, **kwargs) -> None:
        """
        Dispatch function that triggers before delegating requests to
        the CRUD methods (GET, PUT, PATCH, DELETE).
        """
        request_method = request.method
        if self.is_collection and request_method not in _COLLECTION_METHODS:
            return NotAllowed(f'You can\'t use {request_method} requests on collections.')

        if request_method not in self.allowed_methods:
            return NotAllowed(f'Method not allowed. Allowed methods: {self.allowed_methods}')
        
    def handle_exception(self, exc):
        if isinstance(exc, MethodNotAllowed):
            return NotAllowed(f'Method not allowed. Allowed methods: {self.allowed_methods}')

    def get(self, request, *args, **kwargs):
        return self._auto_method(request, kwargs)
    
    def post(self, request, *args, **kwargs):
        return self._auto_method(request, kwargs)

    def post(self, request, *args, **kwargs):
        return self._auto_method(request, kwargs)

    def put(self, request, *args, **kwargs):
        return self._auto_method(request, kwargs)

    def patch(self, request, *args, **kwargs):
        return self._auto_method(request, kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self._auto_method(request, kwargs)
    
class HSDBDjangoResource(HSDBDjangoView):
    is_collection:bool=False
    
class HSDBDjangoCollection(HSDBDjangoView):
    is_collection:bool=True