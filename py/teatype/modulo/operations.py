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
from typing import Dict, List, Optional

# Local imports
from teatype.logging import *
from teatype.modulo.units import parse_designation, print_designation
from teatype.comms.ipc.redis import RedisServiceManager, RedisDispatch, RedisChannel

class Operations:
    def __init__(self, verbose_logging:Optional[bool]=False):
        self.redis_service = RedisServiceManager(client_name='teatype.modulo.operations',
                                                 verbose_logging=verbose_logging)
        
    def dispatch(self, id:str, command:str, is_async:bool=True, payload:any=None) -> None:
        """
        Dispatch command to a Modulo unit.
        
        Args:
            id (str): ID of the Modulo unit.
            command (str): Command to dispatch.
            is_async (bool): Whether to dispatch asynchronously.
            payload (any): Additional payload data.
        """
        dispatch = RedisDispatch(RedisChannel.COMMANDS.value,
                                 'modulo.operations.dispatch',
                                 command,
                                 id,
                                 payload)
        if is_async:
            self.redis_service.send_message(dispatch)
        
    def list(self, filters:List[tuple[str,str]]=None, print:bool=False) -> List[Dict]|None:
        """
        List all available and running Modulo units.
        
        Args:
            filters (List[tuple[str,str]]): List of filters to apply.
            print (bool): Whether to print the results.
            
        Returns:
            List[Dict]|None: List of Modulo units or None if none found.
        """
        clients = self.redis_service.pool.clients
        units = []
        for client in clients:
            client_name = client.get('name', None)
            if client_name == None:
                continue
            
            try:
                designation_info = parse_designation(client_name)
                for filter_key, filter_value in (filters or []):
                    if designation_info.get(filter_key) != filter_value:
                        continue
                units.append({
                    'designation': client_name,
                    'name': designation_info.get('name'),
                    'type': designation_info.get('type'),
                    'id': designation_info.get('id'),
                    'pod': designation_info.get('pod')
                })
            except ValueError:
                continue
        
        n_units = len(units)
        if print:
            if n_units == 0:
                warn('No Modulo units found.', use_prefix=False)
            elif n_units == 1:
                success('Found 1 Modulo unit:')
            else:
                success(f'Found {len(units)} Modulo units:')
            for unit in units:
                print_designation(unit.get('designation'))
                println()
        return units if n_units > 0 else []

    def kill(self, id:str) -> bool:
        """
        Kill a Teatype Modulo unit by id.
        
        Args:
            id (str): ID of the Modulo unit to kill.
            
        Returns:
            bool: True if kill command was sent successfully, False otherwise.
        """
        self.dispatch(id=id, command='kill')
        return True
        
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
    parser.add_argument('id',
                        type=str,
                        help='ID of the unit')
    parser.add_argument('--message',
                        type=str,
                        help='Message to send (required for broadcast and dispatch operations)')

    args = parser.parse_args()
    operation = args.operation
    id = args.id
    
    operations = Operations()
    match operation:
        case 'dispatch':
            message = args.message
            if not message:
                err('Message is required for send operation.',
                    raise_exception=ValueError)
            operations.dispatch(id=id, command=message)
        case 'list':
            operations.list()
        case 'kill':
            operations.kill(id=id)

# TODO: Create singleton
# operations = Operations()