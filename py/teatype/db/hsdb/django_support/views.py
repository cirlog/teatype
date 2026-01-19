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
import traceback
from abc import ABCMeta
from typing import List, Type

# Third-party imports
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView
from teatype.db.hsdb import HybridStorage, HSDBQuery
from teatype.logging import *
from teatype.toolkit import kebabify
from teatype.comms.http.responses import Conflict, Gone, NotAllowed, ServerError, Success

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
    
    def _parse_bool_param(self, value:any) -> bool:
        """Parse a query parameter value to a boolean."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, list):
            value = value[0] if value else ''
        return str(value).lower() in ('true', '1', 'yes')

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
            
            # Parse serialization options from query params
            include_relations = self._parse_bool_param(request.GET.get('include_relations'))
            expand_relations = self._parse_bool_param(request.GET.get('expand_relations'))
            
            match request.method:
                case 'GET':
                    if self.is_collection:
                        # Check if there are any query params (excluding reserved ones)
                        query_params = dict(request.GET)
                        has_filter_params = any(
                            key not in {'include_relations', 'expand_relations', 'sort', 'order', 
                                       'page', 'page_size', 'limit', 'offset', 'fields', 'ids_only'}
                            for key in query_params.keys()
                        )
                        
                        if has_filter_params or any(k in query_params for k in ['sort', 'page', 'page_size', 'limit']):
                            # Build query from params
                            query = HSDBQuery.from_params(self.hsdb_model, query_params)
                            results = query.collect()
                            
                            # Serialize results
                            query_response = [
                                entry.model.serialize(entry, 
                                                     include_relations=include_relations,
                                                     expand_relations=expand_relations)
                                for entry in results
                            ]
                        else:
                            # No filtering, get all entries
                            query_response = hybrid_storage.fetch_model_entries(
                                self.hsdb_model, 
                                serialize=True,
                                include_relations=include_relations,
                                expand_relations=expand_relations
                            )
                    else:
                        id = kwargs.get(self.api_id())
                        query_response = hybrid_storage.fetch_entry(
                            id, 
                            serialize=True,
                            include_relations=include_relations,
                            expand_relations=expand_relations
                        )
                case 'POST':
                    query_response, return_code = hybrid_storage.create_entry(self.hsdb_model, data)
                    if return_code == 409:
                        return Conflict('Entry already exists', data=query_response)
                    elif return_code == 410:
                        return Gone('Entry was lost')
                    elif return_code == 500:
                        return ServerError('Internal server error during entry creation')
                    # Serialize the created entry
                    if query_response:
                        query_response = query_response.model.serialize(
                            query_response,
                            include_relations=include_relations,
                            expand_relations=expand_relations
                        )
                case 'PUT':
                    id = kwargs.get(self.api_id())
                    if not id:
                        return NotAllowed('ID is required for PUT requests')
                    query_response, return_code = hybrid_storage.update_entry(id, data)
                    if return_code == 404:
                        return NotAllowed('Entry not found')
                    elif return_code == 500:
                        return ServerError('Internal server error during entry update')
                    # Serialize the updated entry
                    if query_response:
                        query_response = query_response.model.serialize(
                            query_response,
                            include_relations=include_relations,
                            expand_relations=expand_relations
                        )
                case 'PATCH':
                    id = kwargs.get(self.api_id())
                    if not id:
                        return NotAllowed('ID is required for PATCH requests')
                    query_response, return_code = hybrid_storage.update_entry(id, data)
                    if return_code == 404:
                        return NotAllowed('Entry not found')
                    elif return_code == 500:
                        return ServerError('Internal server error during entry update')
                    # Serialize the updated entry
                    if query_response:
                        query_response = query_response.model.serialize(
                            query_response,
                            include_relations=include_relations,
                            expand_relations=expand_relations
                        )
                case 'DELETE':
                    id = kwargs.get(self.api_id())
                    if not id:
                        return NotAllowed('ID is required for DELETE requests')
                    success, return_code = hybrid_storage.delete_entry(id)
                    if return_code == 404:
                        return NotAllowed('Entry not found')
                    elif return_code == 500:
                        return ServerError('Internal server error during entry deletion')
                    query_response = {'deleted': True, 'id': id}
            # TODO: Implement proper query_response handling
            if query_response is not None:
                return Success(query_response)
            else:
                query_response_error = 'Query-response was "None"'
                err(query_response_error, verbose=False)
                return ServerError({'message': query_response_error})
        except Exception as exc:
            err('Exception during auto method handling', traceback=True)
            return ServerError(str(exc))
    
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
            return f'{parsed_name}'
        return f'{self.api_plural_name()}/<str:{self.api_id()}>'

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