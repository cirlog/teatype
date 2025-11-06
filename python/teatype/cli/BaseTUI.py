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
import sys
from typing import List

# From package imports
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import Completer, Completion, WordCompleter
from teatype import colorwrap
from teatype.cli import BaseCLI
from teatype.cli.args import Action
from teatype.enum import EscapeColor
from teatype.io import clear_shell
from teatype.logging import *

class _StopOnSpaceCompleter(Completer):
    """
    Provides completions only until the first space is typed.
    Once a space is detected, no more completions are offered.
    """
    def __init__(self, words):
        self.words = words

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if ' ' not in text:  # Only complete if no space typed yet
            for word in self.words:
                if word.startswith(text):
                    yield Completion(word, start_position=-len(text))

def _modified_prompt(prompt_text:str, options:list[str]=None) -> any:
    try:
        # Apply color to the prompt
        display_text = f'{EscapeColor.LIGHT_GREEN}{prompt_text}{EscapeColor.RESET}'

        # Build options string for display
        if options:
            options_string = '(' + '/'.join(options) + '): '
            options_string = f'{EscapeColor.GRAY}{options_string}{EscapeColor.RESET}'

        # Log the prompt
        log(display_text)

        # Use prompt_toolkit with custom completer
        if options:
            completer = _StopOnSpaceCompleter(options)
            prompt_answer = pt_prompt(
                '> ',
                completer=completer,
                complete_while_typing=True, # keep completions while typing first word
                handle_sigint=True          # allows Ctrl+C to raise KeyboardInterrupt
            )
        else:
            prompt_answer = pt_prompt(
                '> ',
                handle_sigint=True
            )

        # Validate input if options are provided
        if options and prompt_answer.split()[0] not in options:
            error_message = 'Invalid input. Available options are: ' + ', '.join(options)
            err(error_message, use_prefix=False, verbose=False)
        return prompt_answer
    except KeyboardInterrupt:
        return 'exit'
    except SystemExit:
        return None
    except Exception:
        return None

class BaseTUI(BaseCLI):
    def __init__(self,
                 proxy_mode:bool=False,
                 auto_init:bool=True,
                 auto_parse:bool=True,
                 auto_validate:bool=True,
                 auto_execute:bool=True,
                 env_path:str='.../.env'):
        # Prepare meta with additional flags
        meta_info = self.meta()
        def _meta_closure():
            additional_flags = [
                {
                    'long': 'debug',
                    'short': 'd',
                    'help': 'Enable debug mode for the TUI.',
                    'required': False,
                },
                {
                    'long': 'manual-refresh',
                    'short': 'mr',
                    'help': 'Enable manual refresh mode for the TUI.',
                    'required': False,
                },
                {
                    'long': 'one-shot',
                    'short': 'os',
                    'help': 'Execute a single command and exit the TUI.',
                    'required': False
                }
            ]
            meta_info['flags'] = meta_info['flags'] + additional_flags if 'flags' in meta_info else additional_flags
            return meta_info
        self.meta = _meta_closure
        
        super().__init__(proxy_mode,
                         auto_init,
                         auto_parse,
                         auto_validate,
                         auto_execute,
                         env_path)
        self.actions = [Action(**action) for action in self.meta().get('actions', [])]
        self.actions.append(Action(name='exit', help=f'{EscapeColor.GRAY}(or CRTL+C){EscapeColor.RESET} Leave the TUI.'))
                
        self.on_init()
        
    def post_validate(self):
        self.debug = self.get_flag('debug')
        self.manual_refresh = self.get_flag('manual-refresh')
        self.one_shot = self.get_flag('one-shot')
        if self.manual_refresh:
            manual_refresh_action = Action(name='clear',
                                           help='Refreshes the shell in manual mode.')
            self.actions.append(manual_refresh_action)
            
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
            
        if 'No command provided.' in self._parsing_errors:
            self._parsing_errors.remove('No command provided.')
        
    def execute(self):
        self.run()
        
    def run(self):
        clear_shell()
        
        self.dirty = False
        self.exit = False
        self.no_option = False
        self.output = None
        self.unknown_command = None
        iter = 0
        while True:
            try:
                iter += 1
                if iter > 1 and self.one_shot:
                    break
                
                println()
                if self.exit:
                    break
                
                if self.manual_refresh:
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
                    log(f'{EscapeColor.GREEN}-------')
                    println()
                    self.output = None
                
                user_input = _modified_prompt('Enter an action to perform:',
                                              options=[action.name for action in self.actions])
                matching_action = next((action for action in self.actions if action.name == user_input), None)
                if matching_action:
                    if self.manual_refresh:
                        if user_input == 'clear':
                            clear_shell()
                            continue
                        
                    if user_input == 'exit':
                        self.exit = True
                        continue
                    
                    option = None
                    if matching_action.option:
                        try:
                            option = user_input.split(' ')[1]
                        except:
                            self.no_option = True
                            continue
                        
                    self.output = self.on_prompt(user_input, option)
                    continue
                
                self.unknown_command = user_input
            except (KeyboardInterrupt, EOFError):
                self.exit = True
        if self.one_shot:
            warn(f'One-shot command executed. Exiting {self.name} TUI.', pad_before=1, use_prefix=False)
        else:
            warn(f'Exiting {self.name} TUI.', pad_before=1, use_prefix=False)
        println()
        
    #########
    # Hooks #
    #########
    
    def on_init(self):
        pass
    
    def on_prompt(self, user_input:str, option:any=None):
        pass