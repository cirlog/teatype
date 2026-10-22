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
import json
import os
import subprocess
import sys
import threading
from enum import Enum
from typing import Optional
# Third-party imports
from teatype.io import path
from teatype.toolkit import generate_id

class WorkhorseState(Enum):
    COMPLETED='completed'
    ERROR='error'
    IDLE='idle'
    RUNNING='running'

class Workhorse:
    """
    One-shot job: its steps run one after another in a separate process, fed with a JSON payload.
    """
    def __init__(self,
                 name:str,
                 description:str='',
                 steps:list=None,
                 allow_multiple:bool=False) -> None:
        self.script:Optional[str] = None # Set by Tracer.discover()
        
        self.name = name
        self._description = description
        self.steps = steps or []
        self._allow_multiple = allow_multiple
        self._state = WorkhorseState.IDLE
        self._lock = threading.Lock()
        self._process:Optional[subprocess.Popen] = None
        self._pid:Optional[int] = None
    
    def _monitor(self, log_file) -> None:
        try:
            exit_code = self._process.wait()
            with self._lock:
                self._state = WorkhorseState.COMPLETED if exit_code == 0 else WorkhorseState.ERROR
        except Exception:
            with self._lock:
                self._state = WorkhorseState.ERROR
        finally:
            log_file.close()
    
    def launch(self,
               payload:dict=None,
               base_path:str=None,
               log_path:str=None,
               python_executable:str=None) -> dict:
        with self._lock:
            if not self._allow_multiple and self._state == WorkhorseState.RUNNING:
                return {'success': False, 'error': f'Workhorse "{self.name}" is already running'}
            self._state = WorkhorseState.RUNNING
        
        log_file_path = path.join(log_path, f'{self.name}-{generate_id()}.txt')
        path.create(log_path)
        
        try:
            log_file = open(log_file_path, 'a')
            
            env = os.environ.copy()
            existing = env.get('PYTHONPATH', '')
            env['PYTHONPATH'] = base_path + (':' + existing if existing else '')
            
            self._process = subprocess.Popen(
                [python_executable or sys.executable, '-m', 'teatype.modulo.tracer.runner', self.script],
                stdin=subprocess.PIPE,
                stdout=log_file,
                stderr=log_file,
                cwd=base_path,
                env=env,
            )
            
            if payload:
                self._process.stdin.write(json.dumps(payload).encode())
            self._process.stdin.close()
            
            self._pid = self._process.pid
            threading.Thread(target=self._monitor,
                             args=(log_file,),
                             name=f'workhorse-monitor-{self.name}',
                             daemon=True).start()
            
            return {'success': True, 'name': self.name, 'pid': self._pid, 'log': log_file_path}
        except Exception as exc:
            with self._lock:
                self._state = WorkhorseState.ERROR
            return {'success': False, 'error': str(exc)}
    
    ##########
    # Getter #
    ##########
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'description': self._description,
            'state': self._state.value,
            'pid': self._pid,
        }
