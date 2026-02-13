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
Abstract base class for backend adapters.
"""

# Standard-library imports
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


class BaseBackendAdapter(ABC):
    """
    Abstract base class for backend web framework adapters.
    
    This class defines the interface that all backend adapters must implement,
    allowing the BackendUnit and ApplicationUnit to work with different
    web frameworks interchangeably.
    
    Adapters handle:
    - Creating and configuring the web application
    - Mounting static files/assets
    - Registering API routes
    - Starting/stopping the server thread
    - Serving dashboard HTML with config injection
    """
    
    def __init__(self,
                 name: str,
                 *,
                 host: str = '127.0.0.1',
                 port: int = 8080,
                 dashboard_root: Optional[Path] = None) -> None:
        """
        Initialize the backend adapter.
        
        Args:
            name: Name for the backend application
            host: Host to bind the server to
            port: Port to bind the server to
            dashboard_root: Path to the dashboard root directory (for static serving)
        """
        self.name = name
        self.host = host
        self.port = port
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
        
        self._server_thread = None
    
    @property
    @abstractmethod
    def app(self) -> Any:
        """
        Get the underlying web application object.
        
        Returns:
            The framework-specific application (FastAPI, Django application, etc.)
        """
        pass
    
    @abstractmethod
    def mount_static_assets(self, path: str = '/assets') -> None:
        """
        Mount static assets directory at the given path.
        
        Args:
            path: URL path to serve static files from
        """
        pass
    
    @abstractmethod
    def add_route(self,
                  path: str,
                  handler: Callable,
                  methods: List[str] = None,
                  name: Optional[str] = None,
                  **kwargs) -> None:
        """
        Add a route to the application.
        
        Args:
            path: URL path pattern (e.g., '/api/status')
            handler: Request handler function/coroutine
            methods: HTTP methods to allow (e.g., ['GET', 'POST'])
            name: Optional name for the route
            **kwargs: Additional framework-specific options
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """
        Start the backend server in a background thread.
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the backend server gracefully.
        """
        pass
    
    def is_running(self) -> bool:
        """
        Check if the server is currently running.
        
        Returns:
            True if the server thread is alive, False otherwise
        """
        return self._server_thread is not None and self._server_thread.is_alive()
    
    def get_dashboard_html(self, inject_config: bool = True) -> Optional[str]:
        """
        Get the dashboard HTML content, optionally with injected config.
        
        Args:
            inject_config: Whether to inject runtime configuration script
            
        Returns:
            HTML content string, or None if dashboard is not available
        """
        if not self.dashboard_index_file or not self.dashboard_index_file.exists():
            return None
        
        html_content = self.dashboard_index_file.read_text()
        
        if inject_config:
            config_script = f'''<script>
    window.__MODULO_CONFIG__ = {{
        apiBaseUrl: '',
        backendPort: {self.port},
        backendHost: '{self.host}'
    }};
</script>'''
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', f'{config_script}\n</head>')
        
        return html_content
    
    def get_dashboard_help_message(self) -> str:
        """
        Get a help message when the dashboard is not available.
        
        Returns:
            Help message string
        """
        if not self.dashboard_root:
            return 'No dashboard configured for this backend.'
        return (
            f'Dashboard build missing at {self.dashboard_dist_dir}. '
            f'Build the dashboard first with "pnpm build" in {self.dashboard_root}, '
            'or use the Vite dev server during development.'
        )
