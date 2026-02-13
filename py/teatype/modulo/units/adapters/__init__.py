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
Backend adapters for different web frameworks.

This module provides a unified interface for running backend servers
using different frameworks (FastAPI, Django, etc.)
"""

from teatype.modulo.units.adapters.base import BaseBackendAdapter
from teatype.modulo.units.adapters.fastapi import FastAPIBackendAdapter

# Django adapter is optional - only available when Django is installed
try:
    from teatype.modulo.units.adapters.django import DjangoBackendAdapter
    _DJANGO_AVAILABLE = True
except ImportError:
    DjangoBackendAdapter = None  # type: ignore
    _DJANGO_AVAILABLE = False

__all__ = [
    'BaseBackendAdapter',
    'FastAPIBackendAdapter',
    'DjangoBackendAdapter',
    '_DJANGO_AVAILABLE',
]
