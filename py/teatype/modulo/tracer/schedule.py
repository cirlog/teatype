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
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
# Local imports
from teatype.modulo.tracer.task import Task

class ScheduleInterval(Enum):
    DAYS='days'
    HOURS='hours'
    MINUTES='minutes'
    SECONDS='seconds'
    WEEKS='weeks'

_INTERVAL_SECONDS = {
    ScheduleInterval.SECONDS: 1,
    ScheduleInterval.MINUTES: 60,
    ScheduleInterval.HOURS: 3600,
    ScheduleInterval.DAYS: 86400,
    ScheduleInterval.WEEKS: 604800,
}

class Schedule(Task):
    """
    Task that runs its handler every N units of time, or at fixed times of day ("HH:MM" or "HH:MM:SS").
    """
    _kind='schedule'
    
    def __init__(self,
                 name:str,
                 handler:callable,
                 description:str='',
                 interval_value:float=None,
                 interval_unit:ScheduleInterval=None,
                 at_times:list=None,
                 active_on_start:bool=True) -> None:
        super().__init__(name=name, description=description, active_on_start=active_on_start)
        
        self._handler = handler
        self._interval_value = interval_value
        self._interval_unit = interval_unit
        self._at_times = at_times
        self._next_run:Optional[datetime] = None
        
        self._compute_next_run()
    
    #############
    # Internals #
    #############
    
    def _compute_next_run(self) -> None:
        now = datetime.now()
        if self._interval_value is not None and self._interval_unit is not None:
            self._next_run = now + timedelta(seconds=self._interval_value * _INTERVAL_SECONDS[self._interval_unit])
        elif self._at_times is not None:
            candidates = []
            for time_string in self._at_times:
                parts = [int(part) for part in time_string.strip().split(':')]
                candidate = now.replace(hour=parts[0], minute=parts[1], second=parts[2] if len(parts) > 2 else 0, microsecond=0)
                candidates.append(candidate if candidate > now else candidate + timedelta(days=1))
            if candidates:
                self._next_run = min(candidates)
    
    def _error_message(self, exc:Exception) -> str:
        return f'Schedule "{self.name}" error: {exc}'
    
    def _on_start(self) -> None:
        self._compute_next_run()
    
    def _step(self, tracer:object) -> float:
        if self._next_run is not None and datetime.now() >= self._next_run:
            if tracer.on_defer_schedules():
                tracer.history.push(f'Schedule "{self.name}" deferred due to active session lock', level='SCHEDULE')
                return 5.0
            
            # TODO: Log on success (true or false)
            # tracer.history.push(f'Schedule "{self.name}" triggered', level='SCHEDULE')
            self._execute(tracer, self._handler)
            self._compute_next_run()
        
        # Stay responsive to stop events
        remaining = (self._next_run - datetime.now()).total_seconds() if self._next_run is not None else 0
        return min(remaining, 1.0) if remaining > 0 else 0.5
    
    ##########
    # Getter #
    ##########
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            interval={'value': self._interval_value,
                      'unit': self._interval_unit.value if self._interval_unit else None} if self._interval_value else None,
            at_times=self._at_times,
            next_run=self._next_run.isoformat() if self._next_run else None
        )
        return data
