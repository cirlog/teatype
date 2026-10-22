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
from typing import List, Union

# Third-party imports
import requests

_OPERATORS = {'equals': None, 'gt': 'gt', 'gte': 'gte', 'lt': 'lt', 'lte': 'lte', 'contains': 'contains'}

def _model_name(model:Union[type, str]) -> str:
    return model if isinstance(model, str) else model.__name__

class HSDBRemoteQuery:
    """
    Query builder mirroring the HSDBQuery verbs. Conditions are sent as the query string
    that HSDBQuery.from_params() parses on the server, so nothing is evaluated client-side.
    Results are serialized dicts, not model instances.
    """
    def __init__(self, client:'HSDBClient', model:Union[type, str]) -> None:
        self._client = client
        self._model = model
        self._params = {}
        self._field = None

    def where(self, field:str) -> 'HSDBRemoteQuery':
        self._field = field
        return self

    def _condition(self, operator:str, value:any) -> 'HSDBRemoteQuery':
        suffix = _OPERATORS[operator]
        self._params[self._field if suffix is None else f'{self._field}__{suffix}'] = value
        return self

    def equals(self, value:any) -> 'HSDBRemoteQuery': return self._condition('equals', value)
    def greater_than(self, value:any) -> 'HSDBRemoteQuery': return self._condition('gt', value)
    def greater_than_or_equals(self, value:any) -> 'HSDBRemoteQuery': return self._condition('gte', value)
    def less_than(self, value:any) -> 'HSDBRemoteQuery': return self._condition('lt', value)
    def less_than_or_equals(self, value:any) -> 'HSDBRemoteQuery': return self._condition('lte', value)
    def contains(self, value:any) -> 'HSDBRemoteQuery': return self._condition('contains', value)

    def sort_by(self, field:str, order:str='asc') -> 'HSDBRemoteQuery':
        self._params['sort'] = f'-{field}' if order == 'desc' else field
        return self

    def paginate(self, page:int, page_size:int) -> List[dict]:
        self._params.update(page=page, page_size=page_size)
        return self.all()

    def all(self, **options) -> List[dict]:
        return self._client.request('GET', f'/hsdb/{_model_name(self._model)}', params={**self._params, **options})

    def first(self) -> dict|None:
        return next(iter(self.paginate(0, 1)), None)

    def last(self) -> dict|None:
        return next(iter(self.paginate(-1, 1)), None)

    def count(self) -> int:
        return len(self.all())

class HSDBClient:
    """
    HTTP client for a running HSDB unit. Models are passed as classes or by name; no local
    HybridStorage is created, so never instantiate relation-bearing models in a client process.
    """
    server:object=None # The HSDB unit, only set if this process launched the server

    def __init__(self, host:str='127.0.0.1', port:int=9876, timeout:float=5.0) -> None:
        self.base_url = f'http://{host}:{port}'
        self.timeout = timeout
        self._session = requests.Session() # Keep-alive: reuses one TCP connection

    def request(self, method:str, path:str, *, params:dict=None, json:dict=None, allow_404:bool=False) -> any:
        response = self._session.request(method, self.base_url + path, params=params, json=json, timeout=self.timeout)
        if allow_404 and response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def info(self, timeout:float=None) -> dict|None:
        """
        Return {'service', 'pid', 'models': {name: count}} or None if no HSDB answers.
        """
        try:
            response = self._session.get(f'{self.base_url}/hsdb', timeout=timeout or self.timeout)
            info = response.json()
            return info if info.get('service') == 'hsdb' else None
        except (requests.RequestException, ValueError, AttributeError):
            return None

    def ping(self, timeout:float=0.25) -> bool:
        return self.info(timeout) is not None

    def query(self, model:Union[type, str]) -> HSDBRemoteQuery:
        return HSDBRemoteQuery(self, model)

    def all(self, model:Union[type, str], **options) -> List[dict]:
        return self.query(model).all(**options)

    def count(self, model:Union[type, str]) -> int:
        return self.request('GET', '/hsdb')['models'][_model_name(model)]

    def create(self, model:Union[type, str], data:dict) -> dict:
        return self.request('POST', f'/hsdb/{_model_name(model)}', json=data)

    def delete(self, model:Union[type, str], id:str) -> bool:
        return self.request('DELETE', f'/hsdb/{_model_name(model)}/{id}', allow_404=True) is not None

    def find(self, model:Union[type, str], **filters) -> List[dict]:
        """
        Keyword filters use the HSDBQuery.from_params syntax, e.g. find(Student, age__gte=18, sort='-name').
        """
        return self.request('GET', f'/hsdb/{_model_name(model)}', params=filters)

    def get(self, model:Union[type, str], id:str, **options) -> dict|None:
        return self.request('GET', f'/hsdb/{_model_name(model)}/{id}', params=options, allow_404=True)

    def update(self, model:Union[type, str], id:str, data:dict, **options) -> dict|None:
        return self.request('PATCH', f'/hsdb/{_model_name(model)}/{id}', params=options, json=data, allow_404=True)