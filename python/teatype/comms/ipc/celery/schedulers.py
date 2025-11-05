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

# Package imports
import celery

class TaskScheduler:
    def __init__(self):
        from .app import get_celery_app
        
        self.celery_app = get_celery_app()
        
    def schedule_task(self, task_name:str, *args, **kwargs):
        task = self.celery_app.send_task(task_name, args=args, kwargs=kwargs)
        return task
    
    def get_task_status(self, task_id:str):
        result = self.celery_app.AsyncResult(task_id)
        return result.status
    
    def revoke_task(self, task_id:str, terminate:bool=False):
        self.celery_app.control.revoke(task_id, terminate=terminate)
    
    def list_active_tasks(self):
        inspector = self.celery_app.control.inspect()
        active_tasks = inspector.active()
        return active_tasks
    
    def list_scheduled_tasks(self):
        inspector = self.celery_app.control.inspect()
        scheduled_tasks = inspector.scheduled()
        return scheduled_tasks