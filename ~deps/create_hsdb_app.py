#!/usr/bin/env python3.13

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
HSDBServer App Generator

Creates a new HSDB application structure with models and routes.

Usage:
    python create_hsdb_app.py <app_name>
    
Example:
    python create_hsdb_app.py products
"""

import os
import sys
from pathlib import Path

def create_app_structure(app_name: str, base_path: str = 'api'):
    """
    Create a new HSDB app structure.
    
    Args:
        app_name: Name of the app to create
        base_path: Base directory for apps (default: 'api')
    """
    app_path = Path(base_path) / app_name
    
    # Check if app already exists
    if app_path.exists():
        print(f"Error: App '{app_name}' already exists at {app_path}")
        return False
    
    # Create directory structure
    directories = [
        app_path,
        app_path / 'models',
        app_path / 'routes',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create __init__.py files
    for directory in directories:
        init_file = directory / '__init__.py'
        init_file.write_text(f"# {app_name} package\n")
        print(f"Created: {init_file}")
    
    # Create example model
    model_content = f'''# Copyright (C) 2024-2026 Burak Günaydin
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

# From package imports
from teatype.db.hsdb import HSDBModel, HSDBAttribute

class ExampleModel(HSDBModel):
    """
    Example model for {app_name} app.
    
    Customize this model by adding your own attributes.
    """
    name = HSDBAttribute(str, required=True)
    description = HSDBAttribute(str)
    
    def __init__(self, data:dict, **kwargs):
        super().__init__(data, **kwargs)
'''
    
    model_file = app_path / 'models' / 'ExampleModel.py'
    model_file.write_text(model_content)
    print(f"Created: {model_file}")
    
    # Create example route
    route_content = f'''# Copyright (C) 2024-2026 Burak Günaydin
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

# From package imports
from teatype.db.hsdb.django_support.views import HSDBDjangoResource

# From local imports
from {base_path}.{app_name}.models import ExampleModel

class ExampleResource(HSDBDjangoResource):
    """
    REST API resource for ExampleModel.
    
    Automatically provides CRUD operations:
    - GET /{app_name}/example-resources/<id> - Get single resource
    - PUT /{app_name}/example-resources/<id> - Update resource
    - PATCH /{app_name}/example-resources/<id> - Partial update
    - DELETE /{app_name}/example-resources/<id> - Delete resource
    """
    allowed_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
    auto_view = True
    data_key = 'example_data'
    hsdb_model = ExampleModel
'''
    
    route_file = app_path / 'routes' / 'ExampleResource.py'
    route_file.write_text(route_content)
    print(f"Created: {route_file}")
    
    # Create collection route
    collection_content = f'''# Copyright (C) 2024-2026 Burak Günaydin
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

# From package imports
from teatype.db.hsdb.django_support.views import HSDBDjangoCollection

# From local imports
from {base_path}.{app_name}.models import ExampleModel

class ExampleCollection(HSDBDjangoCollection):
    """
    REST API collection for ExampleModel.
    
    Automatically provides collection operations:
    - GET /{app_name}/example-collection - List all resources
    - POST /{app_name}/example-collection - Create new resource
    """
    allowed_methods = ['GET', 'POST']
    auto_view = True
    data_key = 'example_data'
    hsdb_model = ExampleModel
'''
    
    collection_file = app_path / 'routes' / 'ExampleCollection.py'
    collection_file.write_text(collection_content)
    print(f"Created: {collection_file}")
    
    # Create urls.py
    urls_content = f'''# Copyright (C) 2024-2026 Burak Günaydin
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

# From package imports
from teatype.db.hsdb.django_support.urlpatterns import parse_dynamic_routes
from teatype.io import path

# Automatically discover and register all routes in the routes/ directory
urlpatterns = parse_dynamic_routes(
    app_name='{app_name}',
    search_path=path.join(path.caller_parent(), 'routes')
)
'''
    
    urls_file = app_path / 'urls.py'
    urls_file.write_text(urls_content)
    print(f"Created: {urls_file}")
    
    # Create main application file
    main_content = f'''#!/usr/bin/env python3.13

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
{app_name.capitalize()} Application

Main entry point for the {app_name} HSDBServer application.

Usage:
    python {app_name}_app.py runserver
    python {app_name}_app.py shell
"""

import sys
import types

from teatype.db.hsdb import HSDBServer
from {base_path}.{app_name}.models import ExampleModel

# Define your models
MODELS = [
    ExampleModel,
    # Add more models here
]

# Define your apps
APPS = [
    '{base_path}.{app_name}',
    # Add more apps here
]

def main():
    # Create HSDBServer instance
    server = HSDBServer(
        models=MODELS,
        apps=APPS,
        host='127.0.0.1',
        port=8000,
        cold_mode=False,
        debug=True,
        cors_allow_all=True,  # Only for development!
    )
    
    # Create URL patterns
    urlpatterns = server.create_urlpatterns(
        base_endpoint='v1',
        include_admin=False
    )
    
    # Register URL module
    url_module = types.ModuleType('hsdb_server_urls')
    url_module.urlpatterns = urlpatterns
    sys.modules['hsdb_server_urls'] = url_module
    
    # Run server or execute command
    if len(sys.argv) > 1:
        if sys.argv[1] == 'runserver':
            server.run()
        else:
            server.execute_command(*sys.argv[1:])
    else:
        server.run()

if __name__ == '__main__':
    main()
'''
    
    main_file = Path(f'{app_name}_app.py')
    main_file.write_text(main_content)
    os.chmod(main_file, 0o755)
    print(f"Created: {main_file}")
    
    print(f"\n✓ Successfully created app '{app_name}'!")
    print(f"\nNext steps:")
    print(f"1. Customize the model in: {model_file}")
    print(f"2. Customize the routes in: {app_path}/routes/")
    print(f"3. Run the server: python {app_name}_app.py runserver")
    print(f"\nAPI will be available at:")
    print(f"  - http://127.0.0.1:8000/v1/{app_name}/example-collection (GET, POST)")
    print(f"  - http://127.0.0.1:8000/v1/{app_name}/example-resources/<id> (GET, PUT, PATCH, DELETE)")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_hsdb_app.py <app_name>")
        print("\nExample: python create_hsdb_app.py products")
        sys.exit(1)
    
    app_name = sys.argv[1]
    
    # Validate app name
    if not app_name.isidentifier():
        print(f"Error: '{app_name}' is not a valid Python identifier")
        sys.exit(1)
    
    success = create_app_structure(app_name)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()