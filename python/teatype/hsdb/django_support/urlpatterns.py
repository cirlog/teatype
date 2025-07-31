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

# System imports
import importlib
import pkgutil

# From package imports
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

# From local imports
from teatype.hsdb.django_support.views import HSDBDjangoCollection, HSDBDjangoResource, HSDBDjangoView

# TODO: Create a seperate base class without hsdb support
def parse_dynamic_routes(app_name:str, search_path:str, verbose:bool=False):
    print(f'Dynamic route registration for app "{app_name}"')
    urlpatterns = []
    for _, module_name, _ in pkgutil.iter_modules([search_path]):
        module = importlib.import_module(f'.{module_name}', package='restapi.raw.routes')
        if verbose:
            print('Found module:', module_name)
        for _, obj in vars(module).items():
            if isinstance(obj, type) and issubclass(obj, HSDBDjangoView):
                if verbose:
                        print(f'Found class: {obj.__name__}, is subclass of HSDBDjangoView: {issubclass(obj, HSDBDjangoView)}')
                        print(f'Is subclass of HSDBDjangoCollection: {issubclass(obj, HSDBDjangoCollection)}')

        cls = next(
            (
                obj
                for _, obj in vars(module).items()
                if isinstance(obj, type) and issubclass(obj, HSDBDjangoView) and (obj is not HSDBDjangoCollection and obj is not HSDBDjangoResource)
            ),
            None
        )
        if cls:
            if verbose:
                print(f'Selected class: {cls.__name__}')
        else:
            raise Exception('No valid class selected!')

        if issubclass(cls, HSDBDjangoView):
            instance = cls()
            api_name = instance.api_name()
            api_path = instance.api_path()
            view_type = 'collection' if cls.is_collection else 'resource'
            
            urlpatterns.append(path(api_path, cls.as_view(), name=api_name))
            print(f'    Registered route: "{api_path}" for {view_type} "{api_name}"')
    print()
    return format_suffix_patterns(urlpatterns)