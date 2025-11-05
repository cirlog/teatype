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

# From system imports
from abc import abstractmethod

# From package imports
from teatype import colorwrap
from teatype.cli import BaseCLI
from teatype.cli.args import Action
from teatype.enum import EscapeColor
from teatype.io import clear_shell
from teatype.logging import *

DEBUG_MODE = False
MANUAL_REFRESH = True # If True, the shell will be cleared automatically after each command

class BaseTUI(BaseCLI):
    def __init__(self,
                 proxy_mode:bool=False,
                 auto_init:bool=True,
                 auto_parse:bool=True,
                 auto_validate:bool=True,
                 auto_execute:bool=True,
                 env_path:str='.../.env'):
        super().__init__(proxy_mode,
                         auto_init,
                         auto_parse,
                         auto_validate,
                         auto_execute,
                         env_path)
        self.actions = [Action(**action) for action in self.meta().get('actions', [])]
        if MANUAL_REFRESH:
            manual_refresh_action = Action(name='clear',
                                           help='Refreshes the shell in debug mode.')
            self.actions.append(manual_refresh_action)
            
        self.actions.append(Action(name='exit', help=f'{EscapeColor.GRAY}(or CRTL+C){EscapeColor.RESET} Leave the TUI.'))
        # Calculate max lengths for action.name and action.option_name separately
        name_lengths = [len(action.name) for action in self.actions]
        option_lengths = [len(action.option_name) for action in self.actions if action.option_name]
        max_name_len = max(name_lengths) if name_lengths else 0
        max_opt_len = max(option_lengths) if option_lengths else 0

        # Format each action with two aligned columns: name and <option>
        for action in self.actions:
            name_part = action.name.ljust(max_name_len)
            if action.option_name:
                # +2 accounts for the angle brackets <>
                option_part = f"<{action.option_name}>".ljust(max_opt_len + 4)
            else:
                option_part = " " * (max_opt_len + 4)
            action.str = f"  {name_part} {option_part}  {action.help}"
            if action.name == 'clear':
                action.str = colorwrap(action.str, 'cyan')
            if action.name == 'exit':
                action.str = colorwrap(action.str, 'red')
                
        self.on_init()
        
    def post_validate(self):
        if 'No command provided.' in self._parsing_errors:
            self._parsing_errors.remove('No command provided.')
        
    def execute(self):
        self.run()
        
    def run(self):
        clear_shell()
        
        println()
        
        self.dirty = False
        self.exit = False
        self.no_option = False
        self.output = None
        self.unknown_command = None
        while True:
            try:
                if self.exit:
                    break
                
                if MANUAL_REFRESH:
                    hint('MANUAL REFRESH: Shell will not be cleared automatically.', use_prefix=False)
                else:
                    clear_shell()
                
                println()
                log('Available actions:')
                for action in self.actions:
                    log(action.str)
                println()
                
                if self.unknown_command:
                    warn(f'Unknown command: "{self.unknown_command}". Please try again.', use_prefix=False)
                    println()
                    self.unknown_command = None
                    
                if self.no_option:
                    warn('No valid option provided. Please specify an option after the command (e.g., "edit 1").', use_prefix=False)
                    println()
                    self.no_option = False
                    
                if self.output:
                    log(f'{EscapeColor.GREEN}Output:')
                    log(f'{EscapeColor.GREEN}-------')
                    for line in self.output.split('\n'):
                        if line.strip() == '':
                            continue
                        log('   ' + line)
                    println()
                    self.output = None
                    
                user_input = input(f'{EscapeColor.LIGHT_GREEN}{self.name}> {EscapeColor.RESET}').strip().lower()
                matching_action = next((action for action in self.actions if action.name == user_input), None)
                if matching_action:
                    option = None
                    if matching_action.option:
                        try:
                            option = user_input.split(' ')[1]
                        except:
                            self.no_option = True
                            continue
                        
                    self.output = self.on_prompt(user_input, option)
                    continue
                
                if MANUAL_REFRESH:
                    if user_input == 'clear':
                        clear_shell()
                        continue
                elif user_input == 'exit':
                    self.exit = True
                else:
                    self.unknown_command = user_input
            except (KeyboardInterrupt, EOFError):
                self.exit = True
        println()
        warn(f'Exiting {self.name} TUI.', pad_before=1, use_prefix=False)
        println()
        
    #########
    # Hooks #
    #########
    
    def on_init(self):
        pass
    
    def on_prompt(self, user_input:str, option:any=None):
        pass