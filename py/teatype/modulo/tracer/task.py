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
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Optional

# Third-party imports
from teatype.toolkit import generate_id

class TaskState(Enum):
    ACTIVE='active'
    ERROR='error'
    IDLE='idle'
    PAUSED='paused'
    RUNNING='running'
    STOPPED='stopped'

class Task:
    """
    Threaded unit of work owned by a Tracer. Subclasses decide when the handler runs (_step).
    """
    _kind:str='task' # Thread name prefix
    
    def __init__(self, name:str, description:str='', active_on_start:bool=True) -> None:
        self.id = generate_id()
        self.name = name
        self.description = description
        self.is_active_on_start = active_on_start
        self._state = TaskState.IDLE
        self._thread:Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        self._created_at = datetime.now()
        self._error_count = 0
        self._last_error:Optional[str] = None
        self._last_run:Optional[datetime] = None
        self._run_count = 0
        self._total_runtime = 0.0
    
    #############
    # Internals #
    #############
    
    def _execute(self, tracer:object, handler:callable) -> bool:
        with self._lock:
            self._state = TaskState.RUNNING
        
        start = time.time()
        success = False
        try:
            handler(tracer)
            self._run_count += 1
            success = True
        except Exception as exc:
            self._error_count += 1
            self._last_error = str(exc)
            tracer.history.push(self._error_message(exc), level='ERROR')
            with self._lock:
                self._state = TaskState.ERROR
        finally:
            self._total_runtime += time.time() - start
            self._last_run = datetime.now()
            with self._lock:
                if self._state == TaskState.RUNNING:
                    self._state = TaskState.ACTIVE
        return success
    
    def _run_loop(self, tracer:object) -> None:
        while not self._stop_event.is_set():
            if self._state == TaskState.PAUSED:
                self._stop_event.wait(0.5)
                continue
            self._stop_event.wait(self._step(tracer))
        
        with self._lock:
            self._state = TaskState.STOPPED
            
            
    ##############
    # Properties #
    ##############

    def is_active(self) -> bool:
        return self._state in (TaskState.ACTIVE, TaskState.RUNNING)
    
    ##############
    # Public API #
    ##############
    
    def start(self, tracer:object) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        
        self._stop_event.clear()
        self._state = TaskState.ACTIVE
        self._on_start()
        
        self._thread = threading.Thread(target=self._run_loop,
                                        args=(tracer,),
                                        name=f'{self._kind}-{self.name}',
                                        daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        self._state = TaskState.STOPPED
    
    def pause(self) -> None:
        with self._lock:
            if self._state == TaskState.ACTIVE:
                self._state = TaskState.PAUSED
    
    def resume(self) -> None:
        with self._lock:
            if self._state == TaskState.PAUSED:
                self._state = TaskState.ACTIVE
    
    ##########
    # Getter #
    ##########
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'active_on_start': self.is_active_on_start,
            'state': self._state.value,
            'last_run': self._last_run.isoformat() if self._last_run else None,
            'stats': {
                'run_count': self._run_count,
                'error_count': self._error_count,
                'last_error': self._last_error,
                'total_runtime_seconds': round(self._total_runtime, 3),
                'created_at': self._created_at.isoformat(),
            }
        }
    
    #########
    # Hooks #
    #########
    
    def _error_message(self, exc:Exception) -> str:
        return f'[{self._name}] Error: {exc}'
    
    def _on_start(self) -> None:
        pass
    
    def _step(self, tracer:object) -> float:
        """
        Run the handler if due and return the seconds to wait before the next step.
        """
        raise NotImplementedError
