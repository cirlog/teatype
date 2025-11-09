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

# Third-party imports
from teatype.io.dict import merge

def merge(list1, list2):
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
            updated_item = merge(list1_map[identifier], item2)
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