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
from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Union

def fullcopy(obj, _memo=None):
    """
    Perform a deep copy of an object without using `json.dumps` or `copy.deepcopy`.
    """
    # Initialize memo dictionary for cyclic references
    if _memo is None:
        _memo = {}

    # Check for immutable types or objects that do not need deep copying
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    
    # Check for cyclic references
    obj_id = id(obj)
    if obj_id in _memo:
        return _memo[obj_id]
    
    # Deep copy for dictionaries
    if isinstance(obj, dict):
        copied_obj = {}  # Create a new dictionary to hold the deep copied values
        _memo[obj_id] = copied_obj  # Store the new dictionary in the memo to handle cyclic references
        for key, value in obj.items():  # Iterate over each key-value pair in the original dictionary
            copied_key = fullcopy(key, _memo)  # Deep copy the key
            copied_value = fullcopy(value, _memo)  # Deep copy the value
            copied_obj[copied_key] = copied_value  # Add the deep copied key-value pair to the new dictionary
        return copied_obj
    
    # Deep copy for lists
    elif isinstance(obj, list):
        copied_obj = []  # Create a new list to hold the deep copied values
        _memo[obj_id] = copied_obj  # Store the new list in the memo to handle cyclic references
        for item in obj:  # Iterate over each item in the original list
            copied_obj.append(fullcopy(item, _memo))  # Deep copy the item and append it to the new list
        return copied_obj
    
    # Deep copy for tuples
    elif isinstance(obj, tuple):
        copied_obj = tuple(fullcopy(item, _memo) for item in obj)  # Create a new tuple with deep copied items
        _memo[obj_id] = copied_obj  # Store the new tuple in the memo to handle cyclic references
        return copied_obj
    
    # Deep copy for sets
    elif isinstance(obj, set):
        copied_obj = set(fullcopy(item, _memo) for item in obj)  # Create a new set with deep copied items
        _memo[obj_id] = copied_obj  # Store the new set in the memo to handle cyclic references
        return copied_obj
    
    # For other object types, assume they are not deeply copyable
    # (e.g., functions, modules) and return them as-is
    return obj

def merge(dict1, dict2):
    """
    Recursively merges dict2 into dict1.
    
    Args:
        dict1 (dict): The original dictionary to be merged into.
        dict2 (dict): The dictionary to merge from.
    
    Returns:
        dict: The merged dictionary.
    """
    from teatype.io import merge_lists # Avoid circular import issues
    # Iterate over each key-value pair in dict2
    for key, value in dict2.items():
        # If the value is a dictionary, perform a recursive update
        if isinstance(value, dict):
            # Retrieve the current value from dict1 or initialize as empty dict
            dict1[key] = merge(dict1.get(key, {}), value)
        # If the value is a list of dictionaries, perform a list update
        elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
            # Retrieve the current list from dict1 or initialize as empty list
            dict1[key] = merge_lists(dict1.get(key, []), value)
        else:
            # For non-dict and non-list values, directly update dict1
            dict1[key] = value
    # Return the updated dict1
    return dict1

def to_object(d:Dict[str,Any]) -> object:
    """
    Convert a nested dict to an object with attribute-style access (recursively).
    """
    class _DictObject:
        def __init__(self, data: Dict[str, Any]):
            for key, value in data.items():
                if isinstance(value, dict):
                    setattr(self, key, to_object(value))
                else:
                    setattr(self, key, value)
        def __repr__(self):
            return f'DictObject({self.__dict__})'
    return _DictObject(d)

def _autonest() -> defaultdict:
    return defaultdict(_autonest)

def to_plain_dict(d: Union[defaultdict, dict]) -> Dict[str, Any]:
    """
    Convert nested defaultdicts to plain dicts (recursively).
    """
    if isinstance(d, defaultdict):
        d = dict(d)
    if isinstance(d, dict):
        return {k: to_plain_dict(v) for k, v in d.items()}
    return d

def build_hierarchy(
    kv: Iterable[Tuple[str, Any]],
    *,
    sep: str = ":",
    coerce_leaf: bool = True,
) -> Dict[str, Any]:
    """
    Build a nested dict from iterable of (compound_key, value) where compound_key uses `sep`.
    Example: "foo:bar:baz" -> {"foo": {"bar": {"baz": value}}}
    """
    root = _autonest()
    for key, val in kv:
        parts = [p for p in str(key).split(sep) if p]
        if not parts:
            # edge-case: empty key, skip
            continue
        node = root
        for p in parts[:-1]:
            node = node[p]
        node[parts[-1]] = val if coerce_leaf else {"__value__": val}
    return to_plain_dict(root)

def render_tree(
    data: Dict[str, Any],
    *,
    indent_size: int = 4,
) -> List[str]:
    """
    Render a nested dict as an ASCII tree. Returns list of lines (no trailing newline).
    Non-dict leaves are printed as `- key: value`.
    """
    lines: List[str] = []

    def _walk(obj: Any, prefix: str = "") -> None:
        if not isinstance(obj, dict) or not obj:
            return

        items = list(obj.items())
        last_idx = len(items) - 1
        for idx, (k, v) in enumerate(items):
            is_last = idx == last_idx
            branch = "└── " if is_last else "├── "
            if isinstance(v, dict):
                lines.append(f"{prefix}{branch}{k}")
                child_prefix = f"{prefix}{'    ' if is_last else '│   '}"
                _walk(v, child_prefix)
            else:
                leaf_prefix = f"{prefix}{'    ' if is_last else '│   '}"
                lines.append(f"{leaf_prefix}{k}: {v}")

    # Left pad every line by indent_size spaces at the very left for visual alignment
    _walk(data, "")
    return [(" " * indent_size) + line for line in lines]