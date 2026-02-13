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
import random
import socket
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Type

# Third-party imports
from fastapi import HTTPException
from fastapi.responses import HTMLResponse

# Local imports
from teatype.logging import hint, log
from teatype.modulo.units.core import CoreUnit
from teatype.modulo.units.adapters import BaseBackendAdapter, FastAPIBackendAdapter, DjangoBackendAdapter, _DJANGO_AVAILABLE

# Adapter type mapping - Django only available if django is installed
ADAPTER_TYPES: Dict[str, Type[BaseBackendAdapter]] = {
    'fastapi': FastAPIBackendAdapter,
}

# Add Django adapter if available
if _DJANGO_AVAILABLE and DjangoBackendAdapter is not None:
    ADAPTER_TYPES['django'] = DjangoBackendAdapter

# Type alias for adapter choice
AdapterType = Literal['fastapi', 'django']

# Port range for random port selection (common unprivileged port range)
PORT_RANGE_MIN = 10000
PORT_RANGE_MAX = 60000

def find_random_available_port(max_attempts: int = 100) -> int:
    """
    Find a random available port within the configured range.
    
    Args:
        max_attempts: Maximum number of ports to try
        
    Returns:
        An available port number
        
    Raises:
        RuntimeError: If no available port is found within max_attempts
    """
    for _ in range(max_attempts):
        port = random.randint(PORT_RANGE_MIN, PORT_RANGE_MAX)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f'Could not find an available port after {max_attempts} attempts in range {PORT_RANGE_MIN}-{PORT_RANGE_MAX}')

class BackendUnit(CoreUnit):
    """
    Pluggable backend server supporting multiple web frameworks.
    
    This unit provides a unified interface for running backend servers
    using different frameworks (FastAPI, Django). The adapter pattern
    allows seamless switching between frameworks.
    
    Dashboard serving is optional and configured via dashboard_root parameter.
    When dashboard_root is provided, the backend will serve the React dashboard
    from that directory's dist/ folder.
    
    Example with FastAPI (default):
        backend = BackendUnit.create(
            'my-app',
            adapter='fastapi',
            port=8080
        )
    
    Example with Django:
        backend = BackendUnit.create(
            'my-app',
            adapter='django',
            port=8080,
            apps=['myapp']  # Django apps
        )
    """
    def __init__(self,
                 name: str,
                 *,
                 adapter:AdapterType='fastapi',
                 dashboard_root:Optional[Path]=None,
                 host:Optional[str]='127.0.0.1',
                 port:Optional[int]=None,
                 verbose_logging:Optional[bool]=True,
                 **adapter_kwargs) -> None:
        """
        Initialize the backend unit.
        
        Args:
            name: Name of the backend unit
            adapter: Backend adapter type ('fastapi' or 'django')
            host: Host to bind the server to
            port: Port to bind the server to. If None, automatically finds a random available port.
            dashboard_root: Path to the React dashboard root directory.
                           If provided, serves dashboard from {dashboard_root}/dist/
                           If None, dashboard routes return 503 with help message.
            verbose_logging: Whether to enable verbose logging
            **adapter_kwargs: Additional keyword arguments passed to the adapter
                             (e.g., 'apps' for Django, 'debug' for Django)
        """
        super().__init__(name=name, verbose_logging=verbose_logging)
        
        self.host = host
        # Auto-find random available port if none specified
        self.port = port if port is not None else find_random_available_port()
        self.dashboard_root = Path(dashboard_root) if dashboard_root else None
        self.adapter_type = adapter
        
        # Compute dashboard paths if root is provided
        if self.dashboard_root:
            self.dashboard_dist_dir = self.dashboard_root / 'dist'
            self.dashboard_index_file = self.dashboard_dist_dir / 'index.html'
            self.dashboard_assets_dir = self.dashboard_dist_dir / 'assets'
        else:
            self.dashboard_dist_dir = None
            self.dashboard_index_file = None
            self.dashboard_assets_dir = None
        
        # Create the backend adapter
        AdapterClass = ADAPTER_TYPES.get(adapter)
        if not AdapterClass:
            raise ValueError(f"Unknown adapter type: {adapter}. Available: {list(ADAPTER_TYPES.keys())}")
        
        self._adapter: BaseBackendAdapter = AdapterClass(
            name=name,
            host=host,
            port=self.port,
            dashboard_root=dashboard_root,
            **adapter_kwargs
        )
        
        # Mount static assets and register routes
        self._adapter.mount_static_assets()
        self._register_routes()
    
    @property
    def app(self) -> Any:
        """Get the underlying web application from the adapter."""
        return self._adapter.app
    
    @property 
    def adapter(self) -> BaseBackendAdapter:
        """
        Get the backend adapter instance.
        """
        return self._adapter

    def _register_routes(self) -> None:
        """
        Register default routes on the adapter.
        """
        # Status endpoint
        async def status_route() -> Dict[str, Any]:
            return self._status_snapshot()
        
        self._adapter.add_get('/status', status_route, name='status_endpoint')
        
        # Dashboard endpoints (only for FastAPI - Django handles differently)
        if self.adapter_type == 'fastapi':
            async def dashboard_entrypoint():
                return self._react_dashboard_response()
            
            async def dashboard_spa(_: str):
                return self._react_dashboard_response()
            
            self._adapter.add_get('/dashboard', dashboard_entrypoint, name='dashboard')
            # For catch-all SPA routing, add directly to FastAPI app
            from fastapi.responses import HTMLResponse
            self._adapter.app.get('/dashboard/{_:path}', response_class=HTMLResponse, name='dashboard_spa')(dashboard_spa)

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
        if self._adapter.is_running():
            return
        self._adapter.start()

    def _stop_server(self) -> None:
        if not self._adapter.is_running():
            return
        self._adapter.stop()

    def _status_snapshot(self) -> Dict[str, Any]:
        return {
            'unit': self.name,
            'designation': self.designation,
            'status': self._status or 'idle',
            'loop_iter': self.loop_iter,
            'type': self.type,
            'adapter': self.adapter_type
        }

    def _react_dashboard_response(self) -> HTMLResponse:
        """Serve the React dashboard index.html with injected config."""
        html_content = self._adapter.get_dashboard_html(inject_config=True)
        if not html_content:
            raise HTTPException(status_code=503, detail=self._adapter.get_dashboard_help_message())
        return HTMLResponse(content=html_content)