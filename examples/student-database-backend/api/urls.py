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

# From package imports
from teatype.io import path

# TODO: Doesn't work for some reason
from teatype.db.hsdb.django_support.urlpatterns import parse_dynamic_routes

urlpatterns = parse_dynamic_routes(app_name='api', search_path=path.join(path.caller_parent(), 'resources'))