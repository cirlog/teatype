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
import threading
from pathlib import Path
from typing import Any, Dict, Optional

# Third-party imports
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Local imports
from teatype.logging import hint, log
from teatype.modulo.units.core import CoreUnit

PACKAGE_ROOT = Path(__file__).resolve().parents[4]
REACT_DASHBOARD_ROOT = PACKAGE_ROOT / 'react' / 'dashboard'
REACT_DIST_DIR = REACT_DASHBOARD_ROOT / 'dist'
REACT_INDEX_FILE = REACT_DIST_DIR / 'index.html'
REACT_ASSETS_DIR = REACT_DIST_DIR / 'assets'

class UvicornWorker(threading.Thread):
    def __init__(self, app:FastAPI, host:str, port:int):
        super().__init__(daemon=True)
        
        self._server = uvicorn.Server(uvicorn.Config(app,
                                                     host=host,
                                                     port=port,
                                                     log_level='debug'))

    def run(self) -> None:
        self._server.run()

    def shutdown(self) -> None:
        self._server.should_exit = True

class BackendUnit(CoreUnit):
    """
    FastAPI-powered backend with dashboard rendering.
    """
    def __init__(self,
                 name:str,
                 *,
                 host:Optional[str]='127.0.0.1',
                 port:Optional[int]=8080,
                 verbose_logging:Optional[bool]=True) -> None:
        super().__init__(name=name, verbose_logging=verbose_logging)
        
        self.host = host
        self.port = port
        
        self._app = FastAPI(title=f'TeaType Moduloe Backend Unit · {name}', version='1.0.0')
        self._server_thread = None

        self._mount_static_assets()
        self._register_routes()

    # FastAPI wiring
    def _mount_static_assets(self) -> None:
        self._app.mount(
            '/assets',
            StaticFiles(directory=str(REACT_ASSETS_DIR), check_dir=False),
            name='dashboard_assets'
        )

    def _register_routes(self) -> None:
        @self._app.get('/status', name='status_endpoint')
        async def status_route() -> Dict[str, Any]:
            return self._status_snapshot()

        @self._app.get('/dashboard', response_class=HTMLResponse)
        async def dashboard_entrypoint():
            return self._react_dashboard_response()

        @self._app.get('/dashboard/{_:path}', response_class=HTMLResponse)
        async def dashboard_spa(_: str):
            return self._react_dashboard_response()

    # Lifecycle
    def on_loop_start(self) -> None:
        self._start_server()

    def on_loop_run(self) -> None:
        self.loop_idle_time = 1.0

    def on_loop_end(self) -> None:
        self._stop_server()

    def shutdown(self, force: bool = False) -> None:
        if not force and self._shutdown_in_progress:
            return
        self._shutdown_in_progress = True
        hint('Shutting down backend unit ...')
        self._stop_server()

    # Internals
    def _start_server(self) -> None:
        if self._server_thread:
            return
        self._server_thread = UvicornWorker(self._app, self.host, self.port)
        self._server_thread.start()
        log(f'Backend server listening on http://{self.host}:{self.port}')

    def _stop_server(self) -> None:
        if not self._server_thread:
            return
        self._server_thread.shutdown()
        self._server_thread.join(timeout=5)
        self._server_thread = None

    def _status_snapshot(self) -> Dict[str, Any]:
        return {
            'unit': self.name,
            'designation': self.designation,
            'status': self._status or 'idle',
            'loop_iter': self.loop_iter,
            'type': self.type
        }

    def _react_dashboard_response(self) -> FileResponse:
        if not REACT_INDEX_FILE.exists():
            raise HTTPException(status_code=503, detail=self._react_dashboard_help())
        return FileResponse(str(REACT_INDEX_FILE))

    @staticmethod
    def _react_dashboard_help() -> str:
        return (
            'React dashboard build missing. Run "python packages/teatype/scripts/frontend/react-dashboard/build" '
            'to generate dist assets, or use "python packages/teatype/scripts/frontend/react-dashboard/start" '
            'to rely on the Vite dev server during development.'
        )