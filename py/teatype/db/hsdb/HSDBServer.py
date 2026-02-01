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
import sys
from typing import List, Type

# Third-party imports
import django
from django.conf import settings
from teatype.db.hsdb import HybridStorage
from teatype.io import env, path
from teatype.logging import *

class HSDBServer:
    """
    Hybrid Storage Database Server with integrated Django functionality.
    
    This class combines HSDB storage capabilities with Django web framework,
    making it easy to create hybrid Django applications by simply importing
    HSDBServer and defining custom models and routes.
    
    Usage:
        # In your main application file
        from teatype.db.hsdb import HSDBServer
        from your_app.models import YourModel
        
        server = HSDBServer(
            models=[YourModel],
            apps=['your_app'],
            host='127.0.0.1',
            port=8000
        )
        server.run()
    """
    def __init__(self, 
                 apps:List[str]=None,
                 models:List[Type]=None,
                 host:str='127.0.0.1', 
                 port:int=8080,
                 *,
                 allowed_hosts:List[str]=None,
                 cold_mode:bool=False,
                 cors_allow_all:bool=True,
                 debug:bool=None,
                 root_path:str=None,
                 root_urlconf:str=None,
                 settings_module:str=None) -> None:
        """
        Initialize HSDBServer with Django integration.
        
        Args:
            apps: List of Django apps to include
            models: List of HSDB models to register
            host: Host address for the server
            port: Port number for the server
            allowed_hosts: List of allowed hosts for Django settings
            cold_mode: Whether to start in cold mode (no DB initialization)
            cors_allow_all: Whether to allow all CORS origins
            debug: Enable or disable Django debug mode
            root_path: Root path for HSDB storage
            root_urlconf: Root URL configuration module for Django
            settings_module: Django settings module to use
        """
        self.apps = apps or []
        self.cold_mode = cold_mode
        self.host = host
        self.models = models or []
        self.port = port
        
        # Load environment variables (optional - doesn't fail if .env is missing)
        # env.load()
        
        # Initialize HSDB HybridStorage
        self.hybrid_storage = HybridStorage(models=self.models,
                                            root_path=root_path,
                                            cold_mode=cold_mode)
        
        # Configure Django settings
        self._configure_django_settings(
            debug=debug,
            settings_module=settings_module,
            root_urlconf=root_urlconf,
            allowed_hosts=allowed_hosts,
            cors_allow_all=cors_allow_all
        )
        
        success(f'HSDBServer initialized on {host}:{port}')
    
    def _schema_view(self, request):
        """
        API endpoint that returns the full schema of all registered models.
        Includes attributes, relations, and their configurations.
        
        Returns JSON like:
        {
            "models": {
                "Student": {
                    "model_name": "Student",
                    "resource_name": "student",
                    "resource_name_plural": "students",
                    "attributes": {...},
                    "relations": {...}
                },
                ...
            },
            "count": 4
        }
        """
        from django.http import JsonResponse
        
        schema = {
            'models': {},
            'count': len(self.models)
        }
        
        for model in self.models:
            if hasattr(model, 'schema'):
                schema['models'][model.__name__] = model.schema()
        
        return JsonResponse(schema)
    
    def _models_list_view(self, request):
        """
        API endpoint that returns a simple list of all registered models
        with their basic info and entry counts.
        
        Returns JSON like:
        {
            "models": [
                {"name": "Student", "resource": "students", "count": 1234},
                {"name": "University", "resource": "universities", "count": 9},
                ...
            ]
        }
        """
        from django.http import JsonResponse
        from teatype.toolkit import kebabify
        
        models_list = []
        
        for model in self.models:
            model_info = {
                'name': model.__name__,
                'resource': kebabify(model.__name__, remove='-model', plural=True),
                'count': model.count() if hasattr(model, 'count') else 0
            }
            models_list.append(model_info)
        
        return JsonResponse({'models': models_list})
    
    def _api_registry_view(self, request):
        """
        API endpoint that returns a comprehensive registry of all available APIs,
        including model info, allowed methods, field schemas, and endpoints.
        
        This is used by frontend clients to dynamically initialize API clients
        based on the registered models and their associated views.
        
        Returns JSON like:
        {
            "apis": [
                {
                    "name": "Student",
                    "resource": "students",
                    "endpoint": "/students",
                    "count": 1234,
                    "allowedMethods": {
                        "collection": ["GET", "POST"],
                        "resource": ["GET", "PUT", "PATCH", "DELETE"]
                    },
                    "fields": {
                        "name": {"type": "str", "required": true, "indexed": false},
                        "age": {"type": "int", "required": true, "indexed": true},
                        ...
                    },
                    "relations": {
                        "school": {"model": "School", "type": "one"},
                        ...
                    }
                },
                ...
            ],
            "baseEndpoint": "api/v1",
            "timestamp": "2026-02-01T12:00:00Z"
        }
        """
        from django.http import JsonResponse
        from teatype.toolkit import kebabify
        from datetime import datetime, timezone
        
        apis = []
        
        for model in self.models:
            resource_name = kebabify(model.__name__, remove='-model', plural=True)
            
            # Build field schema
            fields = {}
            if hasattr(model, 'attributes'):
                for attr in model.attributes():
                    attr_name = attr.key
                    if attr_name in ['id', 'created_at', 'updated_at', 'model', 'model_name', 
                                     'path', 'resource_name', 'resource_name_plural', 'migration_id']:
                        continue  # Skip base/computed fields
                    fields[attr_name] = {
                        'type': attr.type.__name__ if hasattr(attr.type, '__name__') else str(attr.type),
                        'required': not attr.nullable,
                        'indexed': attr.indexed,
                        'unique': attr.unique,
                        'computed': attr.computed,
                    }
                    if attr.default is not None:
                        fields[attr_name]['default'] = attr.default
            
            # Build relations schema
            relations = {}
            if hasattr(model, 'relations') and callable(model.relations):
                for rel in model.relations():
                    rel_name = rel.key
                    relations[rel_name] = {
                        'model': rel.model.__name__ if hasattr(rel.model, '__name__') else str(rel.model),
                        'type': 'many' if rel.is_list else 'one',
                        'backref': rel.backref,
                    }
            
            # Default allowed methods for auto views
            allowed_methods = {
                'collection': ['GET', 'POST'],
                'resource': ['GET', 'PUT', 'PATCH', 'DELETE']
            }
            
            api_info = {
                'name': model.__name__,
                'resource': resource_name,
                'endpoint': f'/{resource_name}',
                'count': model.count() if hasattr(model, 'count') else 0,
                'allowedMethods': allowed_methods,
                'fields': fields,
                'relations': relations,
            }
            apis.append(api_info)
        
        # Determine base endpoint from config
        base_endpoint = ''
        if hasattr(self, '_base_endpoint'):
            base_endpoint = self._base_endpoint
        
        return JsonResponse({
            'apis': apis,
            'baseEndpoint': base_endpoint,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
        
    def _configure_django_settings(self,
                                   debug:bool=None,
                                   settings_module:str=None,
                                   root_urlconf:str=None,
                                   allowed_hosts:List[str]=None,
                                   cors_allow_all:bool=True) -> None:
        """
        Configure Django settings programmatically.
        """
        # Set Django settings module
        if settings_module:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
        else:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hsdb_server_settings')
            
        # Configure settings if not already configured
        if not settings.configured:
            base_dir = path.workdir()
            
            settings.configure(
                DEBUG=debug if debug is not None else env.get('DEBUG', 'True').lower() == 'true',
                SECRET_KEY=env.get('SECRET_KEY', 'hsdb-server-default-secret-key-change-in-production'),
                ALLOWED_HOSTS=allowed_hosts or env.get('ALLOWED_HOSTS', '*').split(','),
                ROOT_URLCONF=root_urlconf or env.get('ROOT_URLCONF', 'hsdb_server_urls'),
                BASE_DIR=base_dir,
                
                # Application definition
                INSTALLED_APPS=[
                    'django.contrib.admin',
                    'django.contrib.auth',
                    'django.contrib.contenttypes',
                    'django.contrib.sessions',
                    'django.contrib.messages',
                    'django.contrib.staticfiles',
                    'rest_framework',
                    'corsheaders',
                ] + self.apps,
                
                # Middleware
                MIDDLEWARE=[
                    'django.middleware.security.SecurityMiddleware',
                    'corsheaders.middleware.CorsMiddleware',
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.middleware.common.CommonMiddleware',
                    'django.middleware.csrf.CsrfViewMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware',
                    'django.contrib.messages.middleware.MessageMiddleware',
                    'django.middleware.clickjacking.XFrameOptionsMiddleware',
                ],
                
                # Templates
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
                                'django.contrib.messages.context_processors.messages',
                            ],
                        },
                    },
                ],
                
                # Database (not used with HSDB)
                DATABASES={},
                
                # Internationalization
                LANGUAGE_CODE=env.get('LANGUAGE_CODE', 'en-us'),
                TIME_ZONE=env.get('TIME_ZONE', 'UTC'),
                USE_I18N=env.get('USE_I18N', 'True').lower() == 'true',
                USE_TZ=env.get('USE_TZ', 'True').lower() == 'true',
                
                # Static files
                STATIC_URL=env.get('STATIC_URL', '/static/'),
                
                # CORS settings
                CORS_ALLOW_ALL_ORIGINS=cors_allow_all,
                CORS_ALLOW_CREDENTIALS=True,
                CORS_ALLOW_METHODS=[
                    'DELETE',
                    'GET',
                    'OPTIONS',
                    'PATCH',
                    'POST',
                    'PUT',
                ],
                CORS_ALLOW_HEADERS=[
                    'accept',
                    'accept-encoding',
                    'authorization',
                    'content-type',
                    'dnt',
                    'origin',
                    'user-agent',
                    'x-csrftoken',
                    'x-requested-with',
                    'x-auth-token',
                ],
                
                # Disable trailing slash for REST API compatibility
                APPEND_SLASH=False,
                
                # File upload settings
                DATA_UPLOAD_MAX_MEMORY_SIZE=None,
                DATA_UPLOAD_MAX_NUMBER_FIELDS=None,
                FILE_UPLOAD_MAX_MEMORY_SIZE=None,
                
                # Default auto field
                DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
            )
            
            # Setup Django
            django.setup()
            success('Django configured successfully')
    
    def get_asgi_application(self):
        """
        Get the ASGI application for deployment.
        
        Returns:
            The Django ASGI application
        """
        from django.core.asgi import get_asgi_application
        return get_asgi_application()
    
    def get_wsgi_application(self):
        """
        Get the WSGI application for deployment.
        
        Returns:
            The Django WSGI application
        """
        from django.core.wsgi import get_wsgi_application
        return get_wsgi_application()
    
    def create_urlpatterns(self, base_endpoint:str=None, include_admin:bool=False):
        """
        Create URL patterns dynamically for registered apps.
        
        Args:
            base_endpoint: Base API endpoint prefix (e.g., 'v1', 'api')
            include_admin: Whether to include Django admin interface
            
        Returns:
            List of URL patterns
        """
        import importlib
        import importlib.util
        from pathlib import Path
        from django.urls import path
        from django.conf.urls.static import static
        from teatype.db.hsdb.django_support.urlpatterns import parse_dynamic_routes
        
        # Store base endpoint for API registry
        self._base_endpoint = base_endpoint or ''
        
        urlpatterns = []
        
        # Add HSDB schema/models endpoint
        schema_route = f'{base_endpoint}/hsdb/schema/' if base_endpoint else 'hsdb/schema/'
        urlpatterns.append(path(schema_route, self._schema_view, name='hsdb-schema'))
        
        # Add HSDB models list endpoint
        models_route = f'{base_endpoint}/hsdb/models/' if base_endpoint else 'hsdb/models/'
        urlpatterns.append(path(models_route, self._models_list_view, name='hsdb-models'))
        
        # Add HSDB API registry endpoint (comprehensive model + API info for frontend clients)
        registry_route = f'{base_endpoint}/hsdb/registry/' if base_endpoint else 'hsdb/registry/'
        urlpatterns.append(path(registry_route, self._api_registry_view, name='hsdb-registry'))
        
        # Add admin if requested
        if include_admin:
            from django.contrib import admin
            admin_url = f'{base_endpoint}/admin/' if base_endpoint else 'admin/'
            urlpatterns.append(path(admin_url, admin.site.urls))
        
        # Add app URLs dynamically using parse_dynamic_routes
        for app_name in self.apps:
            try:
                # Find the resources directory for the app
                # Use importlib for proper module importing
                app_module = importlib.import_module(app_name)
                
                # Try to get the app path from __file__ or use importlib.util.find_spec
                app_path = None
                if hasattr(app_module, '__file__') and app_module.__file__ is not None:
                    app_path = Path(app_module.__file__).parent
                elif hasattr(app_module, '__path__'):
                    # Handle namespace packages or packages without __file__
                    app_path = Path(list(app_module.__path__)[0])
                else:
                    # Fallback: use importlib.util.find_spec to locate the module
                    spec = importlib.util.find_spec(app_name)
                    if spec and spec.origin:
                        app_path = Path(spec.origin).parent
                    elif spec and spec.submodule_search_locations:
                        app_path = Path(list(spec.submodule_search_locations)[0])
                
                if app_path is None:
                    warn(f'Could not determine path for app: {app_name}')
                    continue
                resources_path = app_path / 'resources'
                
                if resources_path.exists():
                    app_urlpatterns = parse_dynamic_routes(
                        app_name=app_name,
                        search_path=str(resources_path),
                        verbose=True
                    )
                    
                    # Add base endpoint prefix if provided
                    if base_endpoint:
                        for pattern in app_urlpatterns:
                            pattern.pattern._route = f'{base_endpoint}/{pattern.pattern._route}'
                    
                    urlpatterns.extend(app_urlpatterns)
                    success(f'Registered URLs for app: {app_name}')
                else:
                    warn(f'No resources directory found for app: {app_name}')
            except Exception as e:
                err(f'Could not register URLs for app {app_name}', traceback=True)
        
        # Add static files
        if hasattr(settings, 'STATIC_URL'):
            urlpatterns += static(settings.STATIC_URL, document_root=getattr(settings, 'STATIC_ROOT', ''))
        
        return urlpatterns
    
    def run(self, use_ssl:bool=False, cert_file:str=None, key_file:str=None):
        """
        Run the Django development server.
        
        Args:
            use_ssl: Whether to use SSL/HTTPS
            cert_file: Path to SSL certificate file
            key_file: Path to SSL key file
        """
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            err(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable?",
                exit=True
            )
            return
        
        # Build command arguments
        argv = [sys.argv[0], 'runserver', f'{self.host}:{self.port}', '--noreload']
        
        # Add SSL support if requested
        if use_ssl:
            argv[1] = 'runsslserver'
            if cert_file:
                argv.append(f'--certificate={cert_file}')
            if key_file:
                argv.append(f'--key={key_file}')
        
        success(f'Starting HSDBServer on {"https" if use_ssl else "http"}://{self.host}:{self.port}')
        execute_from_command_line(argv)
    
    def execute_command(self, *args):
        """
        Execute Django management commands.
        
        Args:
            *args: Command arguments (e.g., 'makemigrations', 'migrate', 'shell')
        """
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            err("Couldn't import Django management utilities", exit=True)
            return
        argv = [sys.argv[0]] + list(args)
        execute_from_command_line(argv)