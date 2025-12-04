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
from typing import TypeVar
# Third-party imports
from teatype.db.hsdb.HSDBAttribute import HSDBAttribute as HSDBAttributeClass
from teatype.db.hsdb.HSDBField import HSDBField as HSDBFieldClass

HSDBAttribute = TypeVar(HSDBAttributeClass)
HSDBField = TypeVar(HSDBFieldClass)

def transmute_id(entry_id:HSDBField|str) -> str:
    """
    Transmute the ID to a format that is compatible with the index.
    """
    entry_id_type = type(entry_id)
    if entry_id_type is not str and entry_id_type is HSDBField and entry_id_type is not HSDBFieldClass._ValueWrapper:
        raise TypeError(f'Entry ID must be a string or a HSDBField (subclass), not {entry_id_type}.')
    if isinstance(entry_id, HSDBFieldClass) or \
        isinstance(entry_id, HSDBFieldClass._ValueWrapper) or \
        isinstance(entry_id, HSDBAttributeClass) or \
        isinstance(entry_id, HSDBAttributeClass._AttributeWrapper):
        entry_id = entry_id.value
    return entry_id