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
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import Completer, Completion, WordCompleter
from teatype import colorwrap
from teatype.cli import BaseCLI
from teatype.cli.args import Action
from teatype.enum import XTerm
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
                    
# TODO: Auto-complete designations
def _modified_prompt(prompt_text:str, options:list[str]=None) -> any:
    try:
        # Apply color to the prompt
        display_text = f'{XTerm.LIGHT_GREEN}{prompt_text}{XTerm.RESET}'

        # Build options string for display
        if options:
            options_string = '(' + '/'.join(options) + '): '
            options_string = f'{XTerm.GRAY}{options_string}{XTerm.RESET}'

        # Log the prompt
        log(display_text)

        # Use prompt_toolkit with custom completer
        completer = _StopOnSpaceCompleter(options)
        prompt_answer = pt_prompt(
            '> ',
            completer=completer,
            complete_while_typing=True, # keep completions while typing first word
            handle_sigint=True          # allows Ctrl+C to raise KeyboardInterrupt
        )
        prompt_answer = prompt_answer.strip()
        if ' ' in prompt_answer:
            user_input, option = prompt_answer.split(' ', 1)
        else:
            user_input = prompt_answer
            option = None
        return user_input, option
    except KeyboardInterrupt:
        return 'exit', None
    except SystemExit:
        return None, None
    except Exception:
        return None, None

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
                    'name': 'command',
                    'shorthand': 'c',
                    'help': 'Run a single action non-interactively and exit (e.g. -c list, -c "edit 1").',
                    'required': False,
                    'options': str
                },
                {
                    'name': 'debug',
                    'shorthand': 'd',
                    'help': 'Enable debug mode for the TUI.',
                    'required': False,
                },
                {
                    'name': 'manual-refresh',
                    'shorthand': 'mr',
                    'help': 'Enable manual refresh mode for the TUI.',
                    'required': False,
                }
            ]
            meta_info['flags'] = meta_info['flags'] + additional_flags if 'flags' in meta_info else additional_flags
            return meta_info
        self.meta = _meta_closure
        
        # Must be set before calling super().__init__(), since auto_validate triggers
        # post_validate() synchronously during that call, which requires self.actions.
        self.actions = [Action(**action) for action in self.meta().get('actions', [])]
        self.actions.append(Action(name='exit', help=f'{XTerm.GRAY}(or CRTL+C){XTerm.RESET} Leave the TUI.'))
        
        super().__init__(proxy_mode,
                         auto_init,
                         auto_parse,
                         auto_validate,
                         auto_execute,
                         env_path)
                
        self.on_init()
        
    def post_validate(self):
        self.debug = self.get_flag('debug')
        self.manual_refresh = self.get_flag('manual-refresh')
        self.command = self.get_flag('command')
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
        if getattr(self, 'command', None):
            self.run_command()
        else:
            self.run()
            
    def run_command(self):
        """
        Runs a single action given via the -c flag like a regular CLI command and exits,
        without the interactive screen. The action's option is passed after a space,
        e.g. -c "edit 1".
        """
        user_input, _, option = self.command.strip().partition(' ')
        option = option.strip() or None
        
        available_actions = [action.name for action in self.actions if action.name not in ('clear', 'exit')]
        matching_action = next((action for action in self.actions if action.name == user_input and action.name in available_actions), None)
        if not matching_action:
            err(f'Unknown action "{user_input}". Available actions: {", ".join(available_actions)}.',
                exit=True,
                pad_before=1,
                pad_after=1,
                verbose=False)
        if matching_action.option and not option:
            err(f'Action "{user_input}" requires <{matching_action.option_name}> (e.g., -c "{user_input} <{matching_action.option_name}>").',
                exit=True,
                pad_before=1,
                pad_after=1,
                verbose=False)
            
        output = self.on_prompt(user_input, option)
        if output:
            println()
            print(output)
        
    def run(self):
        clear_shell()
        
        self.dirty = False
        self.exit = False
        self.no_option = False
        self.output = None
        self.unknown_command = None
        while True:
            try:
                println()
                if self.exit:
                    break
                
                if self.manual_refresh:
                    hint('MANUAL REFRESH: Shell will not be cleared automatically.', use_prefix=False)
                else:
                    clear_shell()
                    
                println()
                log(f'<| {self.meta().get("name")} tui |>', color='gray')
                
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
                    log(f'{XTerm.GREEN}Output:')
                    log(f'{XTerm.GREEN}-------')
                    println()
                    for line in self.output.split('\n'):
                        # if line.strip() == '':
                        #     continue
                        log('   ' + line)
                    log(f'{XTerm.GREEN}-------')
                    println()
                    self.output = None
                
                user_input, option = _modified_prompt('Input:',
                                                      options=[action.name for action in self.actions])
                if user_input != None:
                    matching_action = next((action for action in self.actions if action.name == user_input), None)
                    if matching_action:
                        if self.manual_refresh:
                            if user_input == 'clear':
                                clear_shell()
                                continue
                            
                        if user_input == 'exit':
                            self.exit = True
                            continue
                        
                        if matching_action.option and not option:
                            self.no_option = True
                            continue
                            
                        self.output = self.on_prompt(user_input, option)
                        continue
                    
                self.unknown_command = user_input
            except (KeyboardInterrupt, EOFError):
                self.exit = True
        warn(f'Exiting {self.name} TUI.', pad_before=1, use_prefix=False)
        println()
        
    #########
    # Hooks #
    #########
    
    def on_init(self):
        pass
    
    def on_prompt(self, user_input:str, option:any=None):
        pass