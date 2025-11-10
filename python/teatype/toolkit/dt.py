# Copyright (C) 2024-2025 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# Standard library imports
import datetime
from zoneinfo import ZoneInfo

class dt(datetime.datetime):
    """
    Enhanced datetime.datetime subclass with global timezone and parsing utilities.
    """
    _GLOBAL_TZ:str=None # holds a fallback timezone string for 'Z' replacements

    @classmethod
    def set_global_tz(cls, tz:str):
        """Configure a global timezone to apply when processing 'Z' suffixes.
        Args:
            tz: Timezone identifier (e.g., 'UTC', 'Europe/Berlin').
        """
        global _GLOBAL_TZ  # reference the module-level variable
        _GLOBAL_TZ = tz    # assign the provided tz string as the global default

    @classmethod
    def now(cls,
            continent:str=None,
            city:str=None,
            format:str='%Y-%m-%dT%H:%M:%S.%f%zZ',
            return_string:bool=True,
            tz:str='UTC') -> str:
        """
        Return current time in a specified timezone, formatted or as datetime.
        
        Args:
            continent: Optional continent for constructing tz (e.g. 'Europe').
            city: Optional city for constructing tz (e.g. 'Berlin').
            format: strftime format used if returning string.
            return_string: If False, returns datetime object directly.
            tz: Timezone identifier fallback (overridden by continent/city).
        Returns:
            Formatted datetime string or datetime object.
        Raises:
            ValueError: if no valid timezone is provided or tz is invalid.
        """
        # If tz not provided, try to build it from continent/city
        if not tz and continent and city:
            tz = f'{continent}/{city}'  # derive tz, e.g. 'America/New_York'
        # If still no tz, raise error
        if not tz:
            raise ValueError('No valid timezone information provided.')
        try:
            timezone = ZoneInfo(tz) # load timezone data
        except ZoneInfo.KeyError:
            raise ValueError(f'Invalid timezone: {tz}')
        current_time = datetime.datetime.now(timezone) # get localized now
        if not return_string:
            return current_time # return datetime object
        return current_time.strftime(format) # return formatted string

    @classmethod
    def fromisoformat(cls, date_string:str, include_tz:bool=False) -> datetime.datetime:
        """
        Parse ISO date strings, handling 'Z' as UTC or custom global tz.
        
        Args:
            date_string: ISO format string, possibly ending with 'Z'.
            include_tz: If True, convert 'Z' to global tz or 'UTC'; else strip 'Z'.
        Returns:
            datetime object, with tzinfo if include_tz=True.
        """
        if 'Z' in date_string:
            if include_tz:
                if _GLOBAL_TZ:
                    date_string = date_string.replace('Z', _GLOBAL_TZ) # use global tz
                else:
                    date_string = date_string.replace('Z', 'UTC') # default to UTC
            else:
                date_string = date_string.split('Z')[0] # remove 'Z' for naive parsing
        return super().fromisoformat(date_string) # delegate to base parser

    @classmethod
    def parse(cls, 
              dt_string:str,
              continent:str=None,
              city:str=None,
              format:str='%Y-%m-%dT%H:%M:%SZ%Z',
              tz:str='UTC') -> datetime.datetime:
        """
        Parse a datetime string with strptime format and attach timezone info.
        
        Args:
            dt_string: The datetime string to parse.
            continent: Optional continent for constructing tz.
            city: Optional city for constructing tz.
            format: strptime format template.
            tz: Timezone identifier fallback (overridden by continent/city).
        Returns:
            A timezone-aware datetime instance.
        Raises:
            ValueError: if no valid timezone is provided or tz is invalid.
        """
        if not tz and continent and city:
            tz = f'{continent}/{city}' # derive tz if not explicitly set
        if not tz:
            raise ValueError('No valid timezone information provided.')
        try:
            timezone = ZoneInfo(tz) # load timezone for replacement
        except ZoneInfo.KeyError:
            raise ValueError(f'Invalid timezone: {tz}')
        dt_instance = datetime.datetime.strptime(dt_string, format) # parse naive dt
        dt_instance = dt_instance.replace(tzinfo=timezone) # attach tzinfo
        return dt_instance