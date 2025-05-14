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

# System-level imports
from datetime import datetime
from uuid import uuid4

def generate_id(truncate:int=None) -> str:
    """
    Creates a 60-character pseudo-random UUID using a custom algorithm that incorporates the current timestamp.
    This method avoids revealing the machine's MAC address, unlike the standard UUID1.

    The algorithm has been tested to prevent collisions in both single-threaded and multi-threaded environments.

    Args:
        truncate (int, optional): If provided and less than 60, truncates the UUID to the specified length. Defaults to None.

    Returns:
        str: The generated 60-character UUID.
    """
    current_datetime = datetime.now() # Capture the current datetime
    date_part = f'{current_datetime.day}{current_datetime.month}{current_datetime.year}' # Format the date
    # Format the time components separately to maintain a consistent date portion in the UUID
    time_part = f'{current_datetime.microsecond}{current_datetime.second}{current_datetime.minute}{current_datetime.hour}'
    # Convert time and date to integers, then to hexadecimal strings
    primary_id = hex(int(time_part))[2:] + hex(int(date_part))[2:] + date_part
    # Generate a secondary pseudo-random ID using UUID4 for additional entropy
    random_id = uuid4().hex + uuid4().hex # Remove hyphens for consistency
    # Combine both IDs and truncate to 60 characters for URL compatibility
    unique_id = (primary_id + random_id)[:60]
    if truncate and truncate < 60:
        unique_id = unique_id[:truncate] # Apply truncation if specified
    return unique_id