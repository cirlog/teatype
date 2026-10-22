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

# Third-party imports
from teatype.enum import XTerm

# Local imports
from teatype.modulo.tracer.task import Task

_ROUTINE_TYPE_COLORS = {
    'intervention': XTerm.RED,
    'misc': XTerm.LIGHT_BLUE,
    'monitoring': XTerm.BLUE,
}

class Routine(Task):
    """
    Task that runs its call handler over and over, with a fixed pause in between.
    """
    _kind='routine'
    
    def __init__(self,
                 call_handler:callable,
                 type:str,
                 name:str=None,
                 description:str='',
                 interval:float=5.0,
                 priority:int=0,
                 active_on_start:bool=True,
                 vars:dict=None) -> None:
        super().__init__(name=name if name is not None else getattr(call_handler, '__name__', str(call_handler)),
                         description=description,
                         active_on_start=active_on_start)
        
        self._call_handler = call_handler
        self.type = type
        self._type_color = _ROUTINE_TYPE_COLORS.get(type, XTerm.RESET)
        self._interval = interval
        self._priority = priority
        self._iteration = 0
        
        # Name -> default of the variables this routine needs on tracer.vars; shared names are created by the first routine
        self.vars = vars or {}
    
    def _step(self, tracer:object) -> float:
        if self._execute(tracer, self._call_handler):
            self._iteration += 1
        return self._interval
    
    ##########
    # Getter #
    ##########
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(type=self.type, priority=self._priority, interval=self._interval)
        data['stats']['iteration'] = self._iteration
        return data