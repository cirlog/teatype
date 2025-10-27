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

def deepcopy(obj, _memo=None):
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
            copied_key = deepcopy(key, _memo)  # Deep copy the key
            copied_value = deepcopy(value, _memo)  # Deep copy the value
            copied_obj[copied_key] = copied_value  # Add the deep copied key-value pair to the new dictionary
        return copied_obj
    
    # Deep copy for lists
    elif isinstance(obj, list):
        copied_obj = []  # Create a new list to hold the deep copied values
        _memo[obj_id] = copied_obj  # Store the new list in the memo to handle cyclic references
        for item in obj:  # Iterate over each item in the original list
            copied_obj.append(deepcopy(item, _memo))  # Deep copy the item and append it to the new list
        return copied_obj
    
    # Deep copy for tuples
    elif isinstance(obj, tuple):
        copied_obj = tuple(deepcopy(item, _memo) for item in obj)  # Create a new tuple with deep copied items
        _memo[obj_id] = copied_obj  # Store the new tuple in the memo to handle cyclic references
        return copied_obj
    
    # Deep copy for sets
    elif isinstance(obj, set):
        copied_obj = set(deepcopy(item, _memo) for item in obj)  # Create a new set with deep copied items
        _memo[obj_id] = copied_obj  # Store the new set in the memo to handle cyclic references
        return copied_obj
    
    # For other object types, assume they are not deeply copyable
    # (e.g., functions, modules) and return them as-is
    return obj

def update_dict(dict1, dict2):
    """
    Recursively updates dict1 to match the structure and values of dict2 without removing unspecified fields.
    
    Args:
        dict1 (dict): The dictionary to be updated.
        dict2 (dict): The dictionary containing updates.
    
    Returns:
        dict: The updated dictionary.
    """
    # Iterate over each key-value pair in dict2
    for key, value in dict2.items():
        # If the value is a dictionary, perform a recursive update
        if isinstance(value, dict):
            # Retrieve the current value from dict1 or initialize as empty dict
            dict1[key] = update_dict(dict1.get(key, {}), value)
        # If the value is a list of dictionaries, perform a list update
        elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
            # Retrieve the current list from dict1 or initialize as empty list
            dict1[key] = update_list(dict1.get(key, []), value)
        else:
            # For non-dict and non-list values, directly update dict1
            dict1[key] = value
    # Return the updated dict1
    return dict1

def update_list(list1, list2):
    """
    Updates list1 to match list2 by merging items with the same unique identifiers.
    
    Args:
        list1 (list): The original list to be updated.
        list2 (list): The list containing updates.
    
    Returns:
        list: The updated list combining elements from list1 and list2.
    """
    def get_identifier(item):
        """
        Retrieves a unique identifier from an item.
        
        Args:
            item (dict): The dictionary item from which to extract the identifier.
        
        Returns:
            Any: The unique identifier based on 'long' or 'short' keys.
        """
        return item.get('long') or item.get('short')
    
    # Create a mapping from identifier to item for list1, excluding items without an identifier
    list1_map = {get_identifier(item): item for item in list1 if get_identifier(item) is not None}
    # Create a mapping from identifier to item for list2, excluding items without an identifier
    list2_map = {get_identifier(item): item for item in list2 if get_identifier(item) is not None}
    
    # Initialize an empty list to store the updated items
    updated_list = []
    # Iterate over each identifier and corresponding item in list2_map
    for identifier, item2 in list2_map.items():
        if identifier in list1_map:
            # If the identifier exists in list1_map, perform a recursive update
            updated_item = update_dict(list1_map[identifier], item2)
            # Append the updated item to the updated_list
            updated_list.append(updated_item)
        else:
            # If the item is only present in list2, append it as is
            updated_list.append(item2)
    
    # Iterate over list1_map to find items not present in list2_map
    for identifier, item1 in list1_map.items():
        if identifier not in list2_map:
            # Append items from list1 that were not updated by list2
            updated_list.append(item1)
    
    # Return the fully updated list
    return updated_list