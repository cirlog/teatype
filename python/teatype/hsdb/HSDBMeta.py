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

# From system imports
from abc import ABCMeta

# From package imports
from teatype.hsdb import HSDBAttribute

class HSDBMeta(ABCMeta):
    """
    Metaclass to collect HSDBAttributes from the class definition.
    """
    def __new__(cls, name, bases, dct):
        fields = {}
        for attr_name, attr_value in dct.items():
            if isinstance(attr_value, HSDBAttribute):
                attr_value.name = attr_name
                fields[attr_name] = attr_value

        dct['_fields'] = fields
        return super().__new__(cls, name, bases, dct)