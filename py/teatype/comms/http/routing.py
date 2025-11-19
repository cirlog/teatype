# Copyright (C) 2024-2025 Burak Günaydin
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
from pathlib import Path
from importlib import util as iutil
# Third-party imports
from teatype.io import path, probe
from teatype.logging import *

fastapi_support = probe.package('fastapi')

if fastapi_support:
    def register_middleware(app,
                            base_path:str,
                            auto_routing:bool=False,
                            version:int=None) -> None:
        """
        Dynamically imports and registers middleware from all Python modules in the versioned `.middleware` directory.
        """
        if not fastapi_support:
            err('FastAPI not installed, skipping middleware registration.')
            return
        
        if version is None and not auto_routing:
            err('auto_routing must be enabled to use versioning.')
            return
        
        middleware_directory = base_path
        if auto_routing:
            if version:
                middleware_directory += f'/v{version}'
            middleware_directory += '/middleware'
        
        for file_name in os.listdir(middleware_directory):
            # Skip non-Python files and special files
            if not file_name.endswith('.py') or file_name.startswith('__'):
                continue

            # Construct the module name and file path
            module_name = f'{middleware_directory.replace("/", ".")}.{file_name[:-3]}'
            file_path = os.path.join(middleware_directory, file_name)

            # Dynamically import the module
            spec = iutil.spec_from_file_location(module_name, file_path)
            module = iutil.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Iterate over all attributes to find middleware classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                # Check if the attribute is a class and its string name ends with 'Middleware'
                if isinstance(attr, type) and attr.__name__.endswith('Middleware') and attr.__name__ != 'BaseHTTPMiddleware':
                    # Add the middleware to the app (assuming it is compatible)
                    app.add_middleware(attr)
                    print(f'Dynamically registered middleware: {attr_name} from {module_name}')

    def register_routes(
        app,
        base_path:str,
        auto_routing:bool=False,
        root_prefix:str|None=None,
        version:int|None=None,
        *,
        nested_prefix:bool=False, # include subfolders in URL
        skip_inits:bool=True      # usually skip __init__.py
    ) -> None:
        if not fastapi_support:
            err('FastAPI not installed, skipping router registration.')
            return

        if version and not auto_routing:
            err('auto_routing must be enabled to use versioning.')
            return

        routes_dir = Path(base_path)
        if auto_routing:
            if version:
                routes_dir = path.join(routes_dir, f'v{version}', stringify=False)
            routes_dir = path.join(routes_dir, 'routes', stringify=False)

        routes_dir = routes_dir.resolve()
        if not routes_dir.exists():
            err(f'Routes dir not found: {routes_dir}')
            return

        # Use a base module namespace derived from the absolute path
        base_mod = '.'.join(routes_dir.parts)

        for pyfile in routes_dir.rglob('*.py'):
            name = pyfile.name
            if skip_inits and name == '__init__.py':
                continue
            if name.startswith('_'):
                continue  # skip private helpers

            rel = pyfile.relative_to(routes_dir).with_suffix('')  # e.g., trays/inferences -> trays.inferences
            module_name = f'{base_mod}.{".".join(rel.parts)}'

            # Avoid stale modules in dev reloads
            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = iutil.spec_from_file_location(module_name, str(pyfile))
            if not spec or not spec.loader:
                err(f'Failed to load spec for {pyfile}')
                continue

            module = iutil.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'router'):
                router = getattr(module, 'router')

                # Build URL prefix
                if nested_prefix:
                    # prepend subfolders (excluding the filename) to the root prefix
                    subdirs = '/'.join(rel.parts[:-1])
                    prefix = root_prefix
                    if subdirs:
                        prefix = (root_prefix or '') + '/' + subdirs
                else:
                    prefix = root_prefix

                if prefix:
                    app.include_router(router, prefix=prefix)
                else:
                    app.include_router(router)

                print(f'Dynamically registered routes from {module_name}')