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
import importlib.util
import os
from types import SimpleNamespace

# Third-party imports
from teatype.io import path
from teatype.logging import *

# Local imports
from teatype.modulo.tracer.history import History
from teatype.modulo.tracer.registry import Registry, WorkhorseRegistry
from teatype.modulo.tracer.routine import Routine
from teatype.modulo.tracer.schedule import Schedule
from teatype.modulo.tracer.workhorse import Workhorse

class Tracer:
    """
    Scaffolding for long-running monitors: routines (looping), schedules (timed) and workhorses (one-shot subprocess jobs).
    
    Transport-agnostic on purpose: mix it into whatever receives the commands (Redis, sockets, ...) and
    forward those to on_command(). Routines and schedules are called with the tracer itself.
    
    Args:
        name: Name of the tracer.
        base_path: Root of the project. Holds the routines/, schedules/ and workloads/ folders; also working directory and
                   PYTHONPATH of workhorses, so their scripts can import project modules.
        state_path: Where routines.json and schedules.json (name -> active on start) are kept. None disables persistence.
        workhorse_log_path: Where workhorse subprocess output goes. Defaults to <base_path>/logs/workhorses.
        python_executable: Interpreter that runs workhorses. Defaults to the current one.
    """
    def __init__(self,
                 name:str,
                 *,
                 base_path:str,
                 python_executable:str=None,
                 state_path:str=None,
                 workhorse_log_path:str=None) -> None:
        self.tracer_name = name
        self.base_path = base_path
        
        self.history = History()
        # State shared between routines, filled by the subclass
        self.vars = SimpleNamespace()
        
        self.routines = Registry(self, 'routines', path.join(state_path, 'routines.json') if state_path else None)
        self.schedules = Registry(self, 'schedules', path.join(state_path, 'schedules.json') if state_path else None)
        self.workhorses = WorkhorseRegistry(base_path=base_path,
                                            log_path=workhorse_log_path or path.join(base_path, 'logs', 'workhorses'),
                                            python_executable=python_executable)
    
    #############
    # Internals #
    #############
    
    def _discover(self, folder:str, target_class:type) -> list:
        """
        Import every public .py file of a folder and collect the instances of target_class in it
        """
        directory = path.join(self.base_path, folder)
        instances = []
        if not os.path.isdir(directory):
            return instances
        
        for filename in sorted(os.listdir(directory)):
            if filename.startswith('_') or not filename.endswith('.py'):
                continue
            filepath = path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception as exc:
                err(f'Failed to import {filepath}: {exc}')
                continue
            
            for attr in vars(module).values():
                if isinstance(attr, target_class):
                    if isinstance(attr, Workhorse):
                        attr.script = filepath
                    instances.append(attr)
        return instances
    
    def _register_vars(self, routine:Routine) -> None:
        for name, default in routine.vars.items():
            if not hasattr(self.vars, name):
                setattr(self.vars, name, default)
    
    ##############
    # Public API #
    ##############
    
    def add_routine(self, routine:Routine) -> Routine:
        self._register_vars(routine)
        self.routines.add(routine)
        self.history.push(f'Added {routine.type} routine "{routine.name}"')
        return routine
    
    def add_schedule(self, schedule:Schedule) -> Schedule:
        return self.schedules.add(schedule)
    
    def add_workhorse(self, workhorse:Workhorse) -> Workhorse:
        return self.workhorses.add(workhorse)
    
    def discover(self, routines:str='routines', schedules:str='schedules', workloads:str='workloads') -> None:
        """
        Register everything found in the routines, schedules and workloads folders below base_path.
        """
        routines = self._discover(routines, Routine)
        # All vars exist before the first routine starts, so no routine reads one that a later routine declares
        for routine in routines:
            self._register_vars(routine)
        for routine in routines:
            self.add_routine(routine)
        for schedule in self._discover(schedules, Schedule):
            self.add_schedule(schedule)
        for workhorse in self._discover(workloads, Workhorse):
            self.add_workhorse(workhorse)
        
        active_routines = [routine.name for routine in self.routines.get_all() if routine.is_active_on_start]
        active_schedules = [schedule.name for schedule in self.schedules.get_all() if schedule.is_active_on_start]
        workhorses = self.workhorses.get_names()
        for label, names in (('Active routines', active_routines),
                             ('Active schedules', active_schedules),
                             ('Available workhorses', workhorses)):
            self.history.push(f'{label} ({len(names)}): {", ".join(names) if names else "none"}')
    
    def stop(self) -> None:
        self.routines.stop_all()
        self.schedules.stop_all()
    
    def on_command(self, command:dict) -> dict|None:
        """
        Handle the built-in commands (get-routines, set-routine-active, get-schedules, set-schedule-active,
        launch-workhorse). Returns the response, or None if the command is not a tracer command.
        """
        name = command.get('command')
        data = command.get('command_data') or {}
        
        if name == 'get-routines':
            return self.routines.to_dict()
        if name == 'get-schedules':
            return self.schedules.to_dict()
        if name in ('set-routine-active', 'set-schedule-active'):
            kind = name.split('-')[1] # 'routine' | 'schedule'
            item_name, active = data.get(f'{kind}_name'), data.get('active')
            if item_name is None or active is None:
                return {'success': False, 'error': f'Missing {kind}_name or active field'}
            registry = self.routines if kind == 'routine' else self.schedules
            return registry.setActive(item_name, bool(active))
        if name == 'launch-workhorse':
            key = data.get('key')
            if key is None:
                return {'success': False, 'error': 'Missing key field'}
            result = self.workhorses.launch(key, data.get('payload'))
            if result.get('success'):
                self.history.push(f'Launched workhorse with key: {key} (PID: {result.get("pid")})')
            else:
                self.history.push(f'Failed to launch workhorse with key: {key} - {result.get("error")}', level='ERROR')
            return result
        return None
    
    #########
    # Hooks #
    #########
    
    def on_defer_schedules(self) -> bool:
        """
        Schedules that are due wait while this returns True (e.g. while a session is locked).
        """
        return False