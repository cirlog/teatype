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
import socket
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


def find_available_port(start_port: int = 8080, max_attempts: int = 100) -> int:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: The port number to start searching from
        max_attempts: Maximum number of ports to try
        
    Returns:
        An available port number
        
    Raises:
        RuntimeError: If no available port is found within max_attempts
    """
    for offset in range(max_attempts):
        port = start_port + offset
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f'Could not find an available port after {max_attempts} attempts starting from {start_port}')

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
    FastAPI-powered backend server.
    
    Dashboard serving is optional and configured via dashboard_root parameter.
    When dashboard_root is provided, the backend will serve the React dashboard
    from that directory's dist/ folder.
    """
    def __init__(self,
                 name:str,
                 *,
                 host:Optional[str]='127.0.0.1',
                 port:Optional[int]=None,
                 dashboard_root:Optional[Path]=None,
                 verbose_logging:Optional[bool]=True) -> None:
        """
        Initialize the backend unit.
        
        Args:
            name: Name of the backend unit
            host: Host to bind the server to
            port: Port to bind the server to. If None, automatically finds an available port starting from 8080.
            dashboard_root: Path to the React dashboard root directory.
                           If provided, serves dashboard from {dashboard_root}/dist/
                           If None, dashboard routes return 503 with help message.
            verbose_logging: Whether to enable verbose logging
        """
        super().__init__(name=name, verbose_logging=verbose_logging)
        
        self.host = host
        # Auto-find available port if none specified
        self.port = port if port is not None else find_available_port(8080)
        self.dashboard_root = Path(dashboard_root) if dashboard_root else None
        
        # Compute dashboard paths if root is provided
        if self.dashboard_root:
            self.dashboard_dist_dir = self.dashboard_root / 'dist'
            self.dashboard_index_file = self.dashboard_dist_dir / 'index.html'
            self.dashboard_assets_dir = self.dashboard_dist_dir / 'assets'
        else:
            self.dashboard_dist_dir = None
            self.dashboard_index_file = None
            self.dashboard_assets_dir = None
        
        self._app = FastAPI(title=f'TeaType Modulo Backend Unit · {name}', version='1.0.0')
        self._server_thread = None

        self._mount_static_assets()
        self._register_routes()

    # FastAPI wiring
    def _mount_static_assets(self) -> None:
        """Mount static assets if dashboard is configured."""
        if self.dashboard_assets_dir and self.dashboard_assets_dir.exists():
            self._app.mount(
                '/assets',
                StaticFiles(directory=str(self.dashboard_assets_dir), check_dir=False),
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

    def _react_dashboard_response(self) -> HTMLResponse:
        """Serve the React dashboard index.html with injected config."""
        if not self.dashboard_index_file or not self.dashboard_index_file.exists():
            raise HTTPException(status_code=503, detail=self._react_dashboard_help())
        
        # Read the HTML and inject configuration
        html_content = self.dashboard_index_file.read_text()
        
        # Inject runtime config script before the closing </head> tag
        config_script = f'''<script>
    window.__MODULO_CONFIG__ = {{
        apiBaseUrl: '',
        backendPort: {self.port},
        backendHost: '{self.host}'
    }};
</script>'''
        
        # Insert config script before </head>
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', f'{config_script}\n</head>')
        
        return HTMLResponse(content=html_content)

    def _react_dashboard_help(self) -> str:
        """Return help message when dashboard build is missing."""
        if not self.dashboard_root:
            return 'No dashboard configured for this backend unit.'
        return (
            f'React dashboard build missing at {self.dashboard_dist_dir}. '
            f'Build the dashboard first with "pnpm build" in {self.dashboard_root}, '
            'or use the Vite dev server during development.'
        )