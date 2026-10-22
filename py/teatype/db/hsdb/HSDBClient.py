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
import contextlib
import glob
import json
import os
import time
import zlib
from pathlib import Path
from typing import List, Union

# Third-party imports
import requests
from teatype.db.hsdb.RawFileStructure import database_path

_OPERATORS = {'equals': None, 'gt': 'gt', 'gte': 'gte', 'lt': 'lt', 'lte': 'lte', 'contains': 'contains'}
_PYTHON_TYPES = {'bool': bool, 'float': float, 'int': int, 'str': str}

def default_port(name:str) -> int:
    """
    Stable port in 10000-29999 derived from the database name, used by cold (file-less) databases.
    """
    return 10000 + zlib.crc32(name.encode()) % 20000

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

class HSDBRemoteModel:
    """
    Model proxy built from a published schema (<db folder>/models/<Name>.json), no model class needed.
    """
    def __init__(self, client:'HSDBClient', schema:dict) -> None:
        self._client = client
        self.schema = schema
        self.name = schema['model_name']

    def __repr__(self) -> str:
        return f'<HSDBRemoteModel {self.name} fields={self.fields}>'

    @property
    def fields(self) -> List[str]:
        """
        Names accepted by create(): non-computed attributes and relations.
        """
        attributes = [name for name, attribute in self.schema['attributes'].items() if not attribute['computed']]
        return attributes + list(self.schema['relations'])

    def _validate(self, data:dict, partial:bool=False) -> None:
        unknown = set(data) - set(self.fields)
        if unknown:
            raise ValueError(f'{self.name}: unknown fields {sorted(unknown)}, expected {self.fields}')
        required = [name for name, attribute in self.schema['attributes'].items() if attribute['required'] and not attribute['computed']]
        required += [name for name, relation in self.schema['relations'].items() if relation['required']]
        missing = [name for name in required if name not in data]
        if missing and not partial:
            raise ValueError(f'{self.name}: missing required fields {missing}')
        for name, value in data.items():
            expected = _PYTHON_TYPES.get(self.schema['attributes'].get(name, {}).get('type'))
            if expected and not isinstance(value, expected):
                raise ValueError(f'{self.name}.{name} must be {expected.__name__}, got {type(value).__name__}')

    def all(self, **options) -> List[dict]:
        return self._client.all(self.name, **options)

    def count(self) -> int:
        return self._client.count(self.name)

    def create(self, data:dict=None, **fields) -> dict:
        data = {**(data or {}), **fields}
        self._validate(data)
        return self._client.create(self.name, data)

    def delete(self, id:str) -> bool:
        return self._client.delete(self.name, id)

    def find(self, **filters) -> List[dict]:
        return self._client.find(self.name, **filters)

    def get(self, id:str, **options) -> dict|None:
        return self._client.get(self.name, id, **options)

    def query(self) -> HSDBRemoteQuery:
        return self._client.query(self.name)

    def update(self, id:str, data:dict=None, **fields) -> dict|None:
        data = {**(data or {}), **fields}
        self._validate(data, partial=True)
        return self._client.update(self.name, id, data)

class HSDBClient:
    """
    HTTP client for a running HSDB unit. Models are passed as classes or by name; no local
    HybridStorage is created, so never instantiate relation-bearing models in a client process.
    Obtain one via `hsdb['name']` / `HSDBClient.discover(name)`, which also loads the model schemas
    from <db folder>/models/*.json so `client.Student` works without the Student class.
    """
    server:object=None # The HSDB unit, only set if this process launched the server

    def __init__(self, host:str='127.0.0.1', port:int=9876, timeout:float=5.0, name:str=None, models:dict=None) -> None:
        self.base_url = f'http://{host}:{port}'
        self.models = models or {} # model name -> schema dict
        self.name = name
        self.timeout = timeout
        self._session = requests.Session() # Keep-alive: reuses one TCP connection

    @classmethod
    def discover(cls, name:str, root_path:str=None, wait:float=0.0) -> 'HSDBClient':
        """
        Find the database `name`, retrying for up to `wait` seconds. Non-cold hosts publish
        <db folder>/server.json; cold hosts (memory only) listen on default_port(name).
        """
        directory = database_path(name, root_path)
        deadline = time.monotonic() + wait
        while True:
            addresses = [('127.0.0.1', default_port(name))]
            with contextlib.suppress(FileNotFoundError, json.JSONDecodeError):
                with open(os.path.join(directory, 'server.json')) as file:
                    published = json.load(file)
                addresses.insert(0, (published['host'], published['port']))
            for host, port in addresses:
                client = cls(host, port, name=name)
                info = client.info(timeout=1.0)
                if info and info.get('name') == name: # A stale file or a default port may belong to something else
                    schemas = [json.loads(Path(schema_file).read_text()) for schema_file in glob.glob(os.path.join(directory, 'models', '*.json'))]
                    if not schemas: # Cold mode writes no schema files, ask the server instead
                        schemas = client.request('GET', '/hsdb/schema').values()
                    client.models = {schema['model_name']: schema for schema in schemas}
                    return client
            if time.monotonic() >= deadline:
                raise ConnectionError(f'No running HSDB named "{name}" (looked in {directory} and on port {default_port(name)})')
            time.sleep(0.05)

    def model(self, name:str) -> HSDBRemoteModel:
        if name not in self.models:
            raise KeyError(f'No schema for model "{name}" (known: {sorted(self.models)}); cold-mode databases publish none')
        return HSDBRemoteModel(self, self.models[name])

    def __getattr__(self, name:str) -> HSDBRemoteModel:
        if name in self.__dict__.get('models', {}):
            return self.model(name)
        raise AttributeError(name)

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