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

# From package imports
from teatype import logging

def implemented_trap(message:str,
                     trap:callable,
                     pad_before:int=None,
                     pad_after:int=None,
                     verbose:bool=False,
                     use_prefix:bool=True) -> None:
    trap_message = logging._format(message,
                           prefix='IMPLEMENTED TRAP',
                           use_prefix=use_prefix,
                           pad_before=pad_before,
                           verbose=verbose)
    
    # logger.critical(trap_message) # Log the message as is
    
    if pad_after:
        logging.println(pad_after) # Print a blank line to add padding below the message