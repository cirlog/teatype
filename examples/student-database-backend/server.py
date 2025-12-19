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
import sys

# Third-party imports
from teatype.db.hsdb.HSDBServer import HSDBServer

# Local imports
from api.models import *

# Define your apps
APPS = [
    'api'
]

MODELS = [
    Class,
    Professor,
    Student,
    University
]

if __name__ == '__main__':
    """
    Main entry point for the HSDBServer application.
    """
    # Create HSDBServer instance with your configuration
    server = HSDBServer(
        apps=APPS,
        cold_mode=True,
        cors_allow_all=True,
        debug=True,
        models=MODELS,
    )
    
    # Create URL patterns
    from django.urls import path
    import sys
    
    # Dynamically create and set URL patterns
    urlpatterns = server.create_urlpatterns(
        include_admin=False
    )
    
    # Create a temporary module for URL configuration
    import types
    url_module = types.ModuleType('hsdb_server_urls')
    url_module.urlpatterns = urlpatterns
    sys.modules['hsdb_server_urls'] = url_module
    
    
    
    # Check if we're running a command or just starting the server
    if len(sys.argv) > 1:
        if sys.argv[1] == 'runserver':
            # Run the development server
            server.run()
        else:
            # Execute any Django management command
            server.execute_command(*sys.argv[1:])
    else:
        # Default: run the server
        server.run()