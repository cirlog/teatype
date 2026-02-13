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

"""
FastAPI backend adapter implementation.
"""

# Standard-library imports
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Third-party imports
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Local imports
from teatype.logging import log
from teatype.modulo.units.adapters.base import BaseBackendAdapter


class UvicornWorker(threading.Thread):
    """
    Worker thread for running Uvicorn server in background.
    """
    
    def __init__(self, app: FastAPI, host: str, port: int, log_level: str = 'info'):
        super().__init__(daemon=True)
        self._server = uvicorn.Server(
            uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level=log_level
            )
        )

    def run(self) -> None:
        self._server.run()

    def shutdown(self) -> None:
        self._server.should_exit = True


class FastAPIBackendAdapter(BaseBackendAdapter):
    """
    FastAPI-based backend adapter.
    
    This adapter uses FastAPI as the web framework and Uvicorn as the ASGI server.
    It provides a high-performance async-capable backend suitable for modern
    web applications and API services.
    
    Example:
        adapter = FastAPIBackendAdapter(
            name='my-app',
            host='127.0.0.1',
            port=8080, 
            dashboard_root=Path('/path/to/dashboard')
        )
        
        # Add custom routes
        adapter.add_route('/api/data', get_data_handler, methods=['GET'])
        
        # Start the server
        adapter.start()
    """
    
    def __init__(self,
                 name: str,
                 *,
                 host: str = '127.0.0.1',
                 port: int = 8080,
                 dashboard_root: Optional[Path] = None,
                 log_level: str = 'info',
                 **fastapi_kwargs) -> None:
        """
        Initialize the FastAPI backend adapter.
        
        Args:
            name: Name for the backend application
            host: Host to bind the server to
            port: Port to bind the server to
            dashboard_root: Path to the dashboard root directory
            log_level: Uvicorn log level (debug, info, warning, error)
            **fastapi_kwargs: Additional kwargs to pass to FastAPI constructor
        """
        super().__init__(name=name, host=host, port=port, dashboard_root=dashboard_root)
        
        self._log_level = log_level
        
        # Create FastAPI application
        default_kwargs = {
            'title': f'TeaType Backend · {name}',
            'version': '1.0.0'
        }
        default_kwargs.update(fastapi_kwargs)
        self._app = FastAPI(**default_kwargs)
    
    @property
    def app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self._app
    
    def mount_static_assets(self, path: str = '/assets') -> None:
        """
        Mount static assets directory at the given path.
        
        Args:
            path: URL path to serve static files from
        """
        if self.dashboard_assets_dir and self.dashboard_assets_dir.exists():
            self._app.mount(
                path,
                StaticFiles(directory=str(self.dashboard_assets_dir), check_dir=False),
                name='dashboard_assets'
            )
    
    def add_route(self,
                  path: str,
                  handler: Callable,
                  methods: List[str] = None,
                  name: Optional[str] = None,
                  **kwargs) -> None:
        """
        Add a route to the FastAPI application.
        
        Args:
            path: URL path pattern
            handler: Request handler function/coroutine
            methods: HTTP methods to allow (defaults to ['GET'])
            name: Optional name for the route
            **kwargs: Additional route options (response_class, etc.)
        """
        methods = methods or ['GET']
        
        # FastAPI uses decorators, so we use add_api_route for programmatic registration
        for method in methods:
            self._app.add_api_route(
                path,
                handler,
                methods=[method],
                name=name,
                **kwargs
            )
    
    def add_get(self, path: str, handler: Callable, name: Optional[str] = None, **kwargs) -> None:
        """Convenience method for GET routes."""
        self.add_route(path, handler, methods=['GET'], name=name, **kwargs)
    
    def add_post(self, path: str, handler: Callable, name: Optional[str] = None, **kwargs) -> None:
        """Convenience method for POST routes."""
        self.add_route(path, handler, methods=['POST'], name=name, **kwargs)
    
    def add_put(self, path: str, handler: Callable, name: Optional[str] = None, **kwargs) -> None:
        """Convenience method for PUT routes."""
        self.add_route(path, handler, methods=['PUT'], name=name, **kwargs)
    
    def add_delete(self, path: str, handler: Callable, name: Optional[str] = None, **kwargs) -> None:
        """Convenience method for DELETE routes."""
        self.add_route(path, handler, methods=['DELETE'], name=name, **kwargs)
    
    def start(self) -> None:
        """Start the FastAPI server with Uvicorn in a background thread."""
        if self._server_thread and self._server_thread.is_alive():
            return
        
        self._server_thread = UvicornWorker(
            self._app,
            self.host,
            self.port,
            self._log_level
        )
        self._server_thread.start()
        log(f'FastAPI backend listening on http://{self.host}:{self.port}')
    
    def stop(self) -> None:
        """Stop the Uvicorn server gracefully."""
        if not self._server_thread:
            return
        
        self._server_thread.shutdown()
        self._server_thread.join(timeout=5)
        self._server_thread = None
