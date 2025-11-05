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
from celery import Celery

_celery_app_instance = None

@property
def get_celery_app():
    """
    Get the singleton Celery app instance.
    """
    global _celery_app_instance
    
    if _celery_app_instance is None:
        _celery_app_instance = Celery(
            'global-teatype-celery-app',
            broker='redis://127.0.0.1:6379/0',
            backend='redis://127.0.0.1:6379/1',
        )
        _celery_app_instance.conf.update(
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            timezone='Europe/Berlin',
            enable_utc=True,
            task_acks_late=True, # ensures tasks aren't lost if worker crashes mid-task
            worker_prefetch_multiplier=1, # prevent one worker from hoarding tasks
        )
    return _celery_app_instance

# Create singleton instance on first import
app = get_celery_app()