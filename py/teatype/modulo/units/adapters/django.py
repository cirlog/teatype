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
Django backend adapter implementation.
"""

# Standard-library imports
import os
import sys
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

# Local imports
from teatype.logging import log, err, warn
from teatype.modulo.units.adapters.base import BaseBackendAdapter


class DjangoWorker(threading.Thread):
    """
    Worker thread for running Django server in background.
    
    Uses Django's ASGI application with Uvicorn for async support,
    or falls back to Daphne/Gunicorn.
    """
    
    def __init__(self, 
                 asgi_app: Any,
                 host: str,
                 port: int,
                 log_level: str = 'warning'):
        super().__init__(daemon=True)
        self._asgi_app = asgi_app
        self._host = host
        self._port = port
        self._log_level = log_level
        self._server = None
        self._should_exit = False
    
    def run(self) -> None:
        try:
            import uvicorn
            self._server = uvicorn.Server(
                uvicorn.Config(
                    self._asgi_app,
                    host=self._host,
                    port=self._port,
                    log_level=self._log_level
                )
            )
            self._server.run()
        except ImportError:
            # Fallback to Django dev server (synchronous, less ideal)
            warn('Uvicorn not available, falling back to Django dev server')
            self._run_dev_server()
    
    def _run_dev_server(self) -> None:
        """Run Django development server as fallback."""
        from django.core.management import execute_from_command_line
        argv = [sys.argv[0], 'runserver', f'{self._host}:{self._port}', '--noreload']
        execute_from_command_line(argv)
    
    def shutdown(self) -> None:
        self._should_exit = True
        if self._server:
            self._server.should_exit = True


class DjangoBackendAdapter(BaseBackendAdapter):
    """
    Django-based backend adapter.
    
    This adapter uses Django as the web framework and can serve both
    traditional Django applications with full ORM support and simple
    API-only configurations. It integrates well with HSDB for hybrid
    storage databases.
    
    Example:
        adapter = DjangoBackendAdapter(
            name='my-app',
            host='127.0.0.1',
            port=8080,
            dashboard_root=Path('/path/to/dashboard'),
            apps=['myapp', 'otherapp']
        )
        
        # Add custom routes (views)
        adapter.add_route('/api/data/', my_view_function, methods=['GET'])
        
        # Start the server
        adapter.start()
    
    Integration with HSDBServer:
        This adapter is designed to work seamlessly with HSDBServer,
        allowing ApplicationUnit to manage both the modulo lifecycle
        and the Django/HSDB backend together.
    """
    
    def __init__(self,
                 name: str,
                 *,
                 host: str = '127.0.0.1',
                 port: int = 8080,
                 dashboard_root: Optional[Path] = None,
                 apps: List[str] = None,
                 debug: bool = True,
                 secret_key: Optional[str] = None,
                 allowed_hosts: List[str] = None,
                 cors_allow_all: bool = True,
                 log_level: str = 'warning',
                 root_urlconf: Optional[str] = None,
                 base_dir: Optional[Path] = None) -> None:
        """
        Initialize the Django backend adapter.
        
        Args:
            name: Name for the backend application
            host: Host to bind the server to
            port: Port to bind the server to
            dashboard_root: Path to the dashboard root directory
            apps: List of Django apps to include
            debug: Enable Django debug mode
            secret_key: Django secret key (auto-generated if not provided)
            allowed_hosts: List of allowed hosts
            cors_allow_all: Allow all CORS origins
            log_level: Server log level
            root_urlconf: Custom root URL configuration module
            base_dir: Django BASE_DIR setting
        """
        super().__init__(name=name, host=host, port=port, dashboard_root=dashboard_root)
        
        self._apps = apps or []
        self._debug = debug
        self._secret_key = secret_key or f'django-modulo-{name}-auto-key'
        self._allowed_hosts = allowed_hosts or ['*']
        self._cors_allow_all = cors_allow_all
        self._log_level = log_level
        self._root_urlconf = root_urlconf
        self._base_dir = base_dir or Path.cwd()
        
        # Dynamic URL patterns storage
        self._dynamic_urlpatterns: List[tuple] = []
        
        # Configure Django
        self._configure_django()
        
        # Django application reference
        self._asgi_app = None
    
    def _configure_django(self) -> None:
        """Configure Django settings programmatically."""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modulo_django_settings')
        
        try:
            from django.conf import settings
            
            if not settings.configured:
                # Core installed apps
                installed_apps = [
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'django.contrib.sessions',
                    'django.contrib.staticfiles',
                ]
                
                # Try to add REST framework and CORS if available
                try:
                    import rest_framework
                    installed_apps.append('rest_framework')
                except ImportError:
                    pass
                
                try:
                    import corsheaders
                    installed_apps.append('corsheaders')
                except ImportError:
                    pass
                
                # Add user apps
                installed_apps.extend(self._apps)
                
                # Middleware
                middleware = [
                    'django.middleware.security.SecurityMiddleware',
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.middleware.common.CommonMiddleware',
                ]
                
                if 'corsheaders' in installed_apps:
                    # Insert CORS middleware after SecurityMiddleware
                    middleware.insert(1, 'corsheaders.middleware.CorsMiddleware')
                
                middleware.extend([
                    'django.middleware.csrf.CsrfViewMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware',
                    'django.middleware.clickjacking.XFrameOptionsMiddleware',
                ])
                
                settings.configure(
                    DEBUG=self._debug,
                    SECRET_KEY=self._secret_key,
                    ALLOWED_HOSTS=self._allowed_hosts,
                    ROOT_URLCONF=self._root_urlconf or 'modulo_urls',
                    BASE_DIR=self._base_dir,
                    INSTALLED_APPS=installed_apps,
                    MIDDLEWARE=middleware,
                    TEMPLATES=[
                        {
                            'BACKEND': 'django.template.backends.django.DjangoTemplates',
                            'DIRS': [],
                            'APP_DIRS': True,
                            'OPTIONS': {
                                'context_processors': [
                                    'django.template.context_processors.debug',
                                    'django.template.context_processors.request',
                                    'django.contrib.auth.context_processors.auth',
                                ],
                            },
                        },
                    ],
                    DATABASES={
                        'default': {
                            'ENGINE': 'django.db.backends.sqlite3',
                            'NAME': str(self._base_dir / 'db.sqlite3'),
                        }
                    },
                    STATIC_URL='/static/',
                    DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
                    CORS_ALLOW_ALL_ORIGINS=self._cors_allow_all,
                )
            
            # Setup Django
            import django
            django.setup()
            
        except ImportError as e:
            err(f'Django is not installed: {e}')
            raise
    
    @property
    def app(self) -> Any:
        """
        Get the Django ASGI application.
        
        Returns:
            Django ASGI application
        """
        if self._asgi_app is None:
            from django.core.asgi import get_asgi_application
            self._asgi_app = get_asgi_application()
        return self._asgi_app
    
    def mount_static_assets(self, path: str = '/assets') -> None:
        """
        Mount static assets directory.
        
        For Django, this adds to STATICFILES_DIRS.
        """
        if self.dashboard_assets_dir and self.dashboard_assets_dir.exists():
            from django.conf import settings
            
            # Add to STATICFILES_DIRS
            current_dirs = list(getattr(settings, 'STATICFILES_DIRS', []))
            if str(self.dashboard_assets_dir) not in current_dirs:
                current_dirs.append(str(self.dashboard_assets_dir))
                settings.STATICFILES_DIRS = current_dirs
    
    def add_route(self,
                  path: str,
                  handler: Callable,
                  methods: List[str] = None,
                  name: Optional[str] = None,
                  **kwargs) -> None:
        """
        Add a route (URL pattern) to the Django application.
        
        Args:
            path: URL path pattern (Django style, e.g., 'api/data/')
            handler: View function
            methods: HTTP methods (applied via decorator or in view logic)
            name: URL name for reverse lookups
            **kwargs: Additional options
        """
        # Store for later URL pattern generation
        self._dynamic_urlpatterns.append({
            'path': path,
            'handler': handler,
            'methods': methods or ['GET'],
            'name': name,
            **kwargs
        })
    
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
    
    def get_urlpatterns(self) -> List:
        """
        Generate Django URL patterns from registered routes.
        
        Returns:
            List of Django URL pattern objects
        """
        from django.urls import path as django_path
        from django.views.decorators.http import require_http_methods
        from django.http import JsonResponse, HttpResponse
        
        urlpatterns = []
        
        for route in self._dynamic_urlpatterns:
            handler = route['handler']
            methods = route['methods']
            
            # Wrap with method restriction if specified
            if methods and methods != ['GET']:
                handler = require_http_methods(methods)(handler)
            
            urlpatterns.append(
                django_path(route['path'], handler, name=route.get('name'))
            )
        
        # Add dashboard routes if configured
        if self.dashboard_root and self.dashboard_index_file:
            def dashboard_view(request):
                html = self.get_dashboard_html(inject_config=True)
                if html:
                    return HttpResponse(html, content_type='text/html')
                return JsonResponse({'error': self.get_dashboard_help_message()}, status=503)
            
            urlpatterns.append(django_path('dashboard/', dashboard_view, name='dashboard'))
            urlpatterns.append(django_path('dashboard/<path:subpath>/', dashboard_view, name='dashboard_spa'))
        
        return urlpatterns
    
    def start(self) -> None:
        """Start the Django server in a background thread."""
        if self._server_thread and self._server_thread.is_alive():
            return
        
        # Generate URL patterns before starting
        self._setup_urlconf()
        
        self._server_thread = DjangoWorker(
            self.app,
            self._host if hasattr(self, '_host') else self.host,
            self._port if hasattr(self, '_port') else self.port,
            self._log_level
        )
        self._server_thread.start()
        log(f'Django backend listening on http://{self.host}:{self.port}')
    
    def _setup_urlconf(self) -> None:
        """Setup Django URL configuration with dynamic routes."""
        import sys
        import types
        
        # Create a dynamic URL module
        urlpatterns = self.get_urlpatterns()
        
        # Create module object
        module_name = self._root_urlconf or 'modulo_urls'
        urls_module = types.ModuleType(module_name)
        urls_module.urlpatterns = urlpatterns
        
        # Register in sys.modules so Django can import it
        sys.modules[module_name] = urls_module
    
    def stop(self) -> None:
        """Stop the Django server gracefully."""
        if not self._server_thread:
            return
        
        self._server_thread.shutdown()
        self._server_thread.join(timeout=5)
        self._server_thread = None
