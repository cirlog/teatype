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

# System imports
import datetime

# From system imports
from zoneinfo import ZoneInfo

class dt(datetime.datetime):
    _GLOBAL_TZ:str=None
    
    @classmethod
    def set_global_tz(cls, tz:str):
        global _GLOBAL_TZ
        _GLOBAL_TZ = tz

    @classmethod
    def now(cls,
            continent:str=None,
            city:str=None,
            format:str='%Y-%m-%dT%H:%M:%SZ%Z',
            return_string:bool=True,
            tz:str='UTC',) -> str:
        # If tz not provided, try to build it from continent/city
        if not tz and continent and city:
            tz = f'{continent}/{city}'

        # If still no tz, raise error
        if not tz:
            raise ValueError('No valid timezone information provided.')

        try:
            timezone = ZoneInfo(tz)
        except ZoneInfo.KeyError:
            raise ValueError(f'Invalid timezone: {tz}')

        current_time = datetime.datetime.now(timezone)
        if not return_string:
            return current_time
        return current_time.strftime(format)

    @classmethod
    def parse(cls, 
              dt_string:str,
              continent:str=None,
              city:str=None,
              format:str='%Y-%m-%dT%H:%M:%SZ%Z',
              tz:str='UTC') -> datetime.datetime:
        if not tz and continent and city:
            tz = f'{continent}/{city}'

        if not tz:
            raise ValueError('No valid timezone information provided.')

        try:
            timezone = ZoneInfo(tz)
        except ZoneInfo.KeyError:
            raise ValueError(f'Invalid timezone: {tz}')

        dt_instance = datetime.datetime.strptime(dt_string, format)
        dt_instance = dt_instance.replace(tzinfo=timezone)
        return dt_instance