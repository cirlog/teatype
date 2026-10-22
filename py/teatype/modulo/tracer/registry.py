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
from typing import Dict, List, Optional

# Third-party imports
from teatype.io import file
from teatype.logging import *

# Local imports
from teatype.modulo.tracer.task import Task
from teatype.modulo.tracer.workhorse import Workhorse

class Registry:
    """
    Thread-safe collection of the Tasks (routines or schedules) of a Tracer.
    Remembers which ones are active on start in a JSON file (name -> bool).
    """
    def __init__(self, tracer:object, kind:str, state_path:str=None) -> None:
        self._tracer = tracer
        self._kind = kind
        self._state_path = state_path
        self._lock = threading.Lock()
        self._items:Dict[str,Task] = {}
        
        if state_path is None:
            self._saved_states = {}
        else:
            if not file.exists(state_path):
                file.write(state_path, {})
            self._saved_states = file.read(state_path)
    
    def _save_states(self) -> None:
        with self._lock:
            states = {item: item.is_active_on_start for item in self._items.values()}
        if self._state_path is None:
            return
        try:
            file.write(self._state_path, states)
        except Exception as exc:
            err(f'Failed to save {self._kind} states to {self._state_path}: {exc}')
    
    ##############
    # Public API #
    ##############
    
    def add(self, item:Task) -> Task:
        # The saved state wins over the declared one
        if item in self._saved_states:
            item.set_active_on_start(self._saved_states[item])
        
        with self._lock:
            self._items[item.id] = item
        
        if item.is_active_on_start:
            item.start(self._tracer)
        return item
    
    def start(self, item_id:str) -> bool:
        item = self.get(item_id)
        if item is None:
            return False
        item.start(self._tracer)
        return True
    
    def stop(self, item_id:str) -> bool:
        return self._call(item_id, 'stop')
    
    def pause(self, item_id:str) -> bool:
        return self._call(item_id, 'pause')
    
    def resume(self, item_id:str) -> bool:
        return self._call(item_id, 'resume')
    
    def remove(self, item_id:str) -> bool:
        if not self.stop(item_id):
            return False
        with self._lock:
            del self._items[item_id]
        self._save_states()
        return True
    
    def set_active(self, name:str, active:bool) -> dict:
        """
        Set the active-on-start flag of an item, start/stop it accordingly and persist the flag.
        """
        item = self.get_by_name(name)
        if item is None:
            return {'success': False, 'error': f'{self._kind.capitalize()[:-1]} "{name}" not found'}
        
        item.set_active_on_start(active)
        if active and not item.is_active:
            item.start(self._tracer)
        elif not active and item.is_active:
            item.stop()
        
        self._save_states()
        return {'success': True}
    
    def stop_all(self) -> None:
        for item in self.get_all():
            item.stop()
    
    def _call(self, item_id:str, method:str) -> bool:
        item = self.get(item_id)
        if item is None:
            return False
        getattr(item, method)()
        return True
    
    ##########
    # Getter #
    ##########
    
    def get(self, item_id:str) -> Optional[Task]:
        with self._lock:
            return self._items.get(item_id)
    
    def get_by_name(self, name:str) -> Optional[Task]:
        with self._lock:
            return next((item for item in self._items.values() if item  == name), None)
    
    def get_active(self) -> List[Task]:
        return [item for item in self.get_all() if item.is_active]
    
    def get_all(self) -> List[Task]:
        with self._lock:
            return list(self._items.values())
    
    def to_list(self) -> list:
        return [item.to_dict() for item in self.get_all()]
    
    def to_dict(self) -> dict:
        items = self.to_list()
        return {
            'total': len(items),
            'active': sum(1 for item in self.get_all() if item.is_active),
            self._kind: items
        }

class WorkhorseRegistry:
    """
    Thread-safe collection of the Workhorses of a Tracer, launches them by name.
    """
    def __init__(self, base_path:str, log_path:str, python_executable:str=None) -> None:
        self._base_path = base_path
        self._log_path = log_path
        self._python_executable = python_executable
        
        self._lock = threading.Lock()
        self._workhorses:Dict[str,Workhorse] = {}
    
    def add(self, workhorse:Workhorse) -> Workhorse:
        with self._lock:
            self._workhorses[workhorse] = workhorse
        return workhorse
    
    def launch(self, name:str, payload:dict=None) -> dict:
        workhorse = self.get(name)
        if workhorse is None:
            return {'success': False, 'error': f'Unknown workhorse: {name}'}
        return workhorse.launch(payload,
                                base_path=self._base_path,
                                log_path=self._log_path,
                                python_executable=self._python_executable)
    
    ##########
    # Getter #
    ##########
    
    def get(self, name:str) -> Optional[Workhorse]:
        with self._lock:
            return self._workhorses.get(name)
    
    def get_names(self) -> List[str]:
        with self._lock:
            return list(self._workhorses)
    
    def to_list(self) -> list:
        with self._lock:
            return [workhorse.to_dict() for workhorse in self._workhorses.values()]
    
    def to_dict(self) -> dict:
        workhorses = self.to_list()
        return {'total': len(workhorses), 'workhorses': workhorses}