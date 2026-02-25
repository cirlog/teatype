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
import io
import shutil
import sys

class LiveTerm:
    """
    A reusable console renderer that updates lines in-place without clearing the screen.
    
    This avoids the flickering/flashing problem caused by full screen clears while
    preserving terminal scroll history and readability.
    
    Uses stdout redirection to capture any stray prints from other code, preventing
    them from disrupting the display.
    
    Usage:
        with LiveTerm() as term:
            while running:
                term.render(['Line 1', f'FPS: {fps}'])
    """
    
    # ANSI escape codes
    CLEAR_LINE='\033[2K'    # Clear entire line
    CURSOR_UP='\033[A'      # Move cursor up one line
    CURSOR_START='\033[G'   # Move cursor to start of line
    HIDE_CURSOR='\033[?25l' # Hide cursor
    RESTORE_CURSOR='\033[u' # Restore cursor position
    SHOW_CURSOR='\033[?25h' # Show cursor
    SAVE_CURSOR='\033[s'    # Save cursor position
    
    def __init__(self,
                 hide_cursor:bool=True,
                 truncate_lines:bool=True,
                 capture_stdout:bool=True):
        """
        Initialize the LiveTerm.
        
        Args:
            hide_cursor: If True, hides the cursor during rendering for cleaner output.
            truncate_lines: If True, truncate lines to terminal width to prevent wrapping.
            capture_stdout: If True, redirect stdout to capture stray prints from other code.
        """
        self._capture_stdout = capture_stdout
        self._hide_cursor = hide_cursor
        self._truncate_lines = truncate_lines
        
        self._captured_output = None
        self._cursor_hidden = False
        self._original_stdout = None
        self._previous_row_count = 0
        self._real_stdout = None
    
    def _get_terminal_width(self) -> int:
        """
        Get the current terminal width.
        """
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80  # fallback
    
    def __enter__(self):
        # Store reference to real stdout for our rendering
        self._real_stdout = sys.stdout
        
        # Redirect stdout to capture stray prints
        if self._capture_stdout:
            self._original_stdout = sys.stdout
            self._captured_output = io.StringIO()
            sys.stdout = self._captured_output
        
        # Clear for clean slate, write directly to real stdout
        self._real_stdout.write('\033[2J\033[H')  # Clear screen and move to top
        self._real_stdout.flush()
        
        if self._hide_cursor:
            self._set_cursor_visibility(False)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore stdout first
        if self._capture_stdout and self._original_stdout:
            sys.stdout = self._original_stdout
        
        if self._cursor_hidden:
            self._set_cursor_visibility(True)
        
        # Print any captured output that was suppressed
        if self._captured_output:
            captured = self._captured_output.getvalue()
            if captured:
                print(f'\n[Suppressed output during LiveTerm session:]\n{captured}')
        
        return False
    
    def _set_cursor_visibility(self, visible:bool) -> None:
        """
        Set cursor visibility.
        """
        out = self._real_stdout or sys.stdout
        if visible:
            out.write(self.SHOW_CURSOR)
            self._cursor_hidden = False
        else:
            out.write(self.HIDE_CURSOR)
            self._cursor_hidden = True
        out.flush()
    
    def render(self, lines:list[str], flush:bool=True) -> None:
        """
        Render lines to the console, updating in place.
        
        Args:
            lines: List of strings to render. Each string represents one line.
            flush: If True, flush stdout after rendering.
        """
        term_width = self._get_terminal_width()
        
        # Process lines - truncate if needed to prevent wrapping
        processed_lines = []
        for line in lines:
            if self._truncate_lines and len(line) >= term_width:
                # Truncate with ellipsis, leaving room for the ellipsis
                processed_lines.append(line[:term_width - 4] + '...')
            else:
                processed_lines.append(line)
        
        # Build the complete output string
        output = ''
        
        # Move cursor up to the start of our previous output
        if self._previous_row_count > 0:
            output += f'\033[{self._previous_row_count}A'
        
        # Render each line, moving to start, clearing, writing content
        for i, line in enumerate(processed_lines):
            output += f'\r{self.CLEAR_LINE}{line}'
            if i < len(processed_lines) - 1:
                output += '\n'
        
        # If we have fewer lines than before, clear the remaining old lines
        extra_lines = self._previous_row_count - len(processed_lines)
        if extra_lines > 0:
            for _ in range(extra_lines):
                output += f'\n\r{self.CLEAR_LINE}'
            # Move cursor back up to end of our content
            output += f'\033[{extra_lines}A'
        
        # Move to end of last line and add newline to position for next render
        output += '\n'
        
        # Write atomically to real stdout (bypassing any redirect)
        out = self._real_stdout or sys.stdout
        out.write(output)
        
        if flush:
            out.flush()
        
        # Track how many rows we rendered
        self._previous_row_count = len(processed_lines)
    
    def clear(self) -> None:
        """
        Clear all previously rendered lines.
        """
        if self._previous_row_count > 0:
            output = ''
            # Move up to start of our output
            output += f'\033[{self._previous_row_count}A'
            # Clear each line
            for _ in range(self._previous_row_count):
                output += f'\r{self.CLEAR_LINE}\n'
            # Move back up
            output += f'\033[{self._previous_row_count}A'
            out = self._real_stdout or sys.stdout
            out.write(output)
            out.flush()
            self._previous_row_count = 0
    
    def reset(self) -> None:
        """
        Reset line tracking without clearing. Use after intentional newlines.
        """
        self._previous_row_count = 0