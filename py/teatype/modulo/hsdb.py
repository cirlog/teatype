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
import atexit
import contextlib
import fcntl
import json
import os
import socket
import time
from typing import List

# Third-party imports
from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from teatype.db.hsdb import HybridStorage
from teatype.db.hsdb.HSDBClient import HSDBClient, default_port
from teatype.db.hsdb.RawFileStructure import database_path
from teatype.db.hsdb.core import HSDBQuery
from teatype.logging import success
from teatype.modulo.units.application import ApplicationUnit

class HSDB(ApplicationUnit):
    """
    Server unit of one named database. Use the `hsdb` registry below instead of creating it directly.
    """
    def __init__(self,
                 name:str,
                 models:List[type],
                 host:str='127.0.0.1',
                 port:int=None,
                 *,
                 cold_mode:bool=False,
                 cors_origins:str=None,
                 root_path:str=None) -> None:
        # Embedded in someone else's process: no dashboard, no Redis, no background units
        super().__init__(name,
                         backend_host=host,
                         backend_port=port,
                         include_dashboard=False,
                         include_rax=False,
                         include_service=False,
                         include_socket=False,
                         log_level='warning',
                         verbose_logging=False)
        self.backend.daemon = True # A non-daemon backend thread would keep the host process alive on exit
        if cors_origins:
            self.app.add_middleware(CORSMiddleware, allow_origin_regex=cors_origins, allow_methods=['*'], allow_headers=['*'])
        self.hybrid_storage = HybridStorage(models=models, root_path=root_path, cold_mode=cold_mode, name=name)
        self._models = {model.__name__: model for model in models}
        for model in models:
            self.hybrid_storage.rf_handler.write_model(model)
        restored = self.hybrid_storage.restore()
        if restored:
            success(f'HSDB "{name}" restored {restored} entries from disk')
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
                    'name': self.name,
                    'pid': os.getpid(),
                    'models': {name: model.count() for name, model in self._models.items()}}

        def schema() -> dict:
            return {name: model.schema() for name, model in self._models.items()}

        def query(model:str, request:Request) -> list:
            params = dict(request.query_params)
            fields = params.pop('fields', None) # HSDBQuery's own 'fields' only supports one field and yields non-models
            try:
                entries = HSDBQuery.from_params(self._model(model), params).collect()
            except KeyError: # HSDBQuery raises on a completely empty database
                entries = []
            rows = [self._serialize(entry, request) for entry in entries]
            if fields:
                wanted = ['id', *fields.split(',')]
                rows = [{key: row[key] for key in wanted if key in row} for row in rows]
            return rows

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
        self.add_route('/hsdb/schema', schema) # Before /hsdb/{model}, which would otherwise swallow it
        self.add_route('/hsdb/{model}', query)
        self.add_route('/hsdb/{model}', create, methods=['POST'])
        self.add_route('/hsdb/{model}/{id}', get_one)
        self.add_route('/hsdb/{model}/{id}', update, methods=['PATCH'])
        self.add_route('/hsdb/{model}/{id}', delete, methods=['DELETE'])

    ##############
    # Public API #
    ##############

class _HSDBRegistry:
    """
    Entry point exposed as `hsdb`. A database is identified by its name; the host process of a name
    holds an flock on <db folder>/server.lock and publishes host/port in <db folder>/server.json.
    Cold databases use no files: an abstract unix socket as lock and default_port(name) as port.
    One process can host one database (HybridStorage is a per-process singleton) but connect to many.
    """
    def __init__(self) -> None:
        self._clients = {}
        self._hosted = None

    def __getitem__(self, name:str) -> HSDBClient:
        return self.connect(name)

    def connect(self, name:str, *, root_path:str=None, wait:float=0.0) -> HSDBClient:
        """
        Client for a running database; waits up to `wait` seconds for it to appear.
        """
        if name not in self._clients:
            self._clients[name] = HSDBClient.discover(name, root_path, wait)
        return self._clients[name]

    def init(self,
             name:str,
             models:List[type],
             *,
             cold_mode:bool=False,
             cors_origins:str=None,
             host:str='127.0.0.1',
             port:int=None,
             root_path:str=None,
             startup_timeout:float=10.0) -> HSDBClient:
        """
        Host the database `name` in this process, or connect if another process already does.
        Returns a client either way; `client.server` is set only for the host. `cors_origins` is a regex of
        browser origins allowed to call the server (none by default, i.e. no CORS headers).
        """
        if name in self._clients:
            return self._clients[name]
        if self._hosted:
            raise RuntimeError(f'This process already hosts "{self._hosted}", one hosted database per process')

        if cold_mode:
            # Memory only: no files at all, so the lock is an abstract unix socket and the port derives from the name
            if port is not None:
                raise ValueError('Cold-mode databases are found via their name-derived port, do not pass a port')
            port = default_port(name)
            lock = socket.socket(socket.AF_UNIX)
            try:
                lock.bind(f'\0hsdb:{name}') # Released by the OS when this process dies
            except OSError:
                lock.close()
                return self.connect(name, root_path=root_path, wait=startup_timeout)
            info_file = None
        else:
            directory = database_path(name, root_path)
            os.makedirs(directory, exist_ok=True)
            lock = open(os.path.join(directory, 'server.lock'), 'w')
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB) # Released by the OS when this process dies
            except BlockingIOError:
                lock.close()
                return self.connect(name, root_path=root_path, wait=startup_timeout)
            info_file = os.path.join(directory, 'server.json')
            with contextlib.suppress(FileNotFoundError):
                os.remove(info_file) # Left over from a crashed host

        server = HSDB.create(name=name, models=models, host=host, port=port, cold_mode=cold_mode, cors_origins=cors_origins, root_path=root_path)
        server.start()
        probe = HSDBClient(host, server.backend_port)
        deadline = time.monotonic() + startup_timeout
        while not probe.ping() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not server.backend.adapter.is_running():
            raise RuntimeError(f'HSDB "{name}" did not come up on {host}:{server.backend_port}')

        server.lock = lock # Keep the lock for the lifetime of the process
        if info_file:
            with open(info_file, 'w') as file:
                json.dump({'name': name, 'host': host, 'port': server.backend_port, 'pid': os.getpid()}, file)
            def unpublish() -> None:
                with contextlib.suppress(FileNotFoundError):
                    os.remove(info_file)
            atexit.register(unpublish)

        client = HSDBClient.discover(name, root_path)
        client.server = server
        self._hosted = name
        self._clients[name] = client
        return client

hsdb = _HSDBRegistry()