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

# System imports
import os
import sys
import subprocess
from typing import Literal

# Local imports
from teatype.io import path
from teatype.modulo.units import *
from teatype.comms.ipc.redis import RedisConnectionPool, RedisDispatch, RedisChannel

class Operations:
    def __init__(self):
        self.redis_connection_pool = RedisConnectionPool(verbose_logging=True)

    def kill(self, designation:str) -> None:
        """
        Kill a Teatype Modulo unit by designation.
        """
        if designation == 'all':
            pass
        
    def dispatch(self, designation:str, command:str) -> None:
        if not self.redis_connection_pool.establish_connection():
            err('Failed to establish Redis connection. Is Redis server running?',
                raise_exception=ConnectionError)
        
        dispatch = RedisDispatch(RedisChannel.COMMANDS.value,
                                 'modulo.operations.dispatch',
                                 command,
                                 designation)
        self.redis_connection_pool.send_message(dispatch)
        
if __name__ == "__main__":
    import argparse
    
    println()
    
    parser = argparse.ArgumentParser(
        description='Execute Teatype Modulo operations.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('operation',
                        type=str,
                        choices=['broadcast', 'dispatch', 'kill'],
                        help='Which command to execute')
    parser.add_argument('designation',
                        type=str,
                        help='Designation of the unit')
    parser.add_argument('--message',
                        type=str,
                        help='Message to send (required for broadcast and dispatch operations)')

    args = parser.parse_args()
    operation = args.operation
    designation = args.designation
    
    operations = Operations()
    match operation:
        case 'dispatch':
            message = args.message
            if not message:
                err('Message is required for send operation.',
                    raise_exception=ValueError)
            operations.dispatch(designation=designation, command=message)
        case 'kill':
            operations.kill(designation=designation)