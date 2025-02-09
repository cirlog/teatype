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

try:
    import django
    from .hsdb_django_responses import *
    from .hsdb_django_urlpatterns import parse_dynamic_routes
    from .hsdb_django_views import HSDBDjangoView, HSDBDjangoResource, HSDBDjangoCollection
except:
    pass