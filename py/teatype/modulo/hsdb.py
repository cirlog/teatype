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
import os
import time
from typing import List

# Third-party imports
from fastapi import HTTPException, Request
from teatype.db.hsdb import HybridStorage
from teatype.db.hsdb.HSDBClient import HSDBClient
from teatype.db.hsdb.core import HSDBQuery
from teatype.logging import success, warn
from teatype.modulo.units.application import ApplicationUnit

class HSDB(ApplicationUnit):
    """
    The main Hybdrid Storage Database application unit. Only one instance should be created per deployment.
    All other HSDB components (like IndexDatabase, RawFileHandler, etc.) should be accessed via this unit.
    All HSDB operations are channeled through this application unit.
    """
    _client:HSDBClient=None # Process-wide handle returned by attach()

    def __init__(self,
                 models:List[type],
                 host:str='127.0.0.1',
                 port:int=9876,
                 *,
                 cold_mode:bool=False,
                 root_path:str=None) -> None:
        # Embedded in someone else's process: no dashboard, no Redis, no background units
        super().__init__('HybridStorageDatabase',
                         backend_host=host,
                         backend_port=port,
                         include_dashboard=False,
                         include_rax=False,
                         include_service=False,
                         include_socket=False,
                         log_level='warning',
                         verbose_logging=False)
        self.backend.daemon = True # A non-daemon backend thread would keep the host process alive on exit
        self.hybrid_storage = HybridStorage(models=models, root_path=root_path, cold_mode=cold_mode)
        self._models = {model.__name__: model for model in models}
        self._register_hsdb_routes()

    #############
    # Internals #
    #############

    def _setup_signal_handlers(self) -> None:
        pass # The default handlers would swallow Ctrl+C for the whole host process

    def _print_startup_banner(self) -> None:
        success(f'HSDB serving {len(self._models)} models on http://{self.backend_host}:{self.backend_port}')

    def _model(self, name:str) -> type:
        if name not in self._models:
            raise HTTPException(404, f'Unknown model "{name}"')
        return self._models[name]

    def _entry(self, model_name:str, id:str) -> object:
        model = self._model(model_name)
        try:
            entry = self.hybrid_storage.fetch_entry(id)
        except KeyError:
            raise HTTPException(404, f'No {model_name} with id "{id}"')
        if entry.model is not model: # Ids are global, so guard against cross-model access
            raise HTTPException(404, f'No {model_name} with id "{id}"')
        return entry

    def _serialize(self, entry:object, request:Request) -> dict:
        flag = lambda key: request.query_params.get(key, '').lower() in ('1', 'true', 'yes')
        return entry.model.serialize(entry,
                                     include_relations=flag('include_relations'),
                                     expand_relations=flag('expand_relations'))

    def _register_hsdb_routes(self) -> None:
        def info() -> dict:
            return {'service': 'hsdb',
                    'pid': os.getpid(),
                    'models': {name: model.count() for name, model in self._models.items()}}

        def query(model:str, request:Request) -> list:
            try:
                entries = HSDBQuery.from_params(self._model(model), dict(request.query_params)).collect()
            except KeyError: # HSDBQuery raises on a completely empty database
                entries = []
            return [self._serialize(entry, request) for entry in entries]

        def create(model:str, data:dict) -> dict:
            # Cold mode never yields a file, which create_entry would report as a failed write (410)
            entry, return_code = self.hybrid_storage.create_entry(self._model(model), data, write=not self.hybrid_storage.rf_handler.cold_mode)
            if return_code != 200:
                raise HTTPException(return_code, 'Entry could not be created, see server log')
            return entry

        def get_one(model:str, id:str, request:Request) -> dict:
            return self._serialize(self._entry(model, id), request)

        def update(model:str, id:str, data:dict, request:Request) -> dict:
            self._entry(model, id)
            entry, return_code = self.hybrid_storage.update_entry(id, data)
            if return_code != 200:
                raise HTTPException(return_code, 'Entry could not be updated, see server log')
            return self._serialize(entry, request)

        def delete(model:str, id:str) -> dict:
            self._entry(model, id)
            self.hybrid_storage.delete_entry(id)
            return {'deleted': True, 'id': id}

        # Plain functions on purpose: FastAPI runs them in its threadpool, so big queries don't block the event loop
        self.add_route('/hsdb', info)
        self.add_route('/hsdb/{model}', query)
        self.add_route('/hsdb/{model}', create, methods=['POST'])
        self.add_route('/hsdb/{model}/{id}', get_one)
        self.add_route('/hsdb/{model}/{id}', update, methods=['PATCH'])
        self.add_route('/hsdb/{model}/{id}', delete, methods=['DELETE'])

    ##############
    # Public API #
    ##############

    @classmethod
    def attach(cls,
               models:List[type]=None,
               host:str='127.0.0.1',
               port:int=9876,
               *,
               cold_mode:bool=False,
               root_path:str=None,
               startup_timeout:float=10.0) -> HSDBClient:
        """
        Return a client for the HSDB at host:port, launching the server in this process first
        if nothing answers there. The server owns the data and dies with the process that launched
        it (client.server is that unit, None if the server lives elsewhere). Models only matter
        for the launching process; clients address models by class or name.
        """
        if cls._client:
            return cls._client

        client = HSDBClient(host, port)
        info = client.info(timeout=0.25)
        if info is None:
            if not models:
                warn('No HSDB running and no models given: launching a server without models')
            server = cls.create(models=models or [], host=host, port=port, cold_mode=cold_mode, root_path=root_path)
            server.start()
            deadline = time.monotonic() + startup_timeout
            while not client.ping() and time.monotonic() < deadline:
                time.sleep(0.05)
            # Lost the bind race to another process: the port answers, but not through our thread
            if server.backend.adapter.is_running():
                client.server = server
            info = client.info()
            if info is None:
                raise RuntimeError(f'HSDB did not come up on {host}:{port}')
        elif models:
            missing = {model.__name__ for model in models} - set(info['models'])
            if missing:
                warn(f'Running HSDB (pid {info["pid"]}) does not serve {sorted(missing)}, restart it with these models')

        cls._client = client
        return client