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
import os
import sys
import time

class Timely:
    def __init__(self,
                 duration:float,
                 *,
                 auto_start:bool=True,
                 hook:callable=None, # Called each cycle during wait() with self as argument
                 yield_duration:float=0.0001) -> None:
        """
        Initialize a precise timer.
        
        Args:
            duration (float): The duration in seconds (can be fractional).
        """
        self.duration = duration
        self.hook = hook
        self.yield_interval = yield_duration # Defautl: 100 microseconds, to yield to other threads/processes for better accuracy
        if hook is not None:
            auto_start = False
        if auto_start:
            self.start_time = time.perf_counter() # higher resolution than time.time()
            self.end_time = self.start_time + duration
        else:
            self.start_time = None
            self.end_time = None

    ##############
    # Properties #
    ##############
        
    @property
    def elapsed(self) -> float:
        """
        Get elapsed time in seconds (can be fractional).
        """
        return time.perf_counter() - self.start_time

    @property
    def expired(self) -> bool:
        """
        Check if the timer has expired. Uses a small sleep to yield to other threads/processes for better accuracy.
        """
        time.sleep(self.yield_interval) # Yield to other threads/processes to improve accuracy
        return time.perf_counter() >= self.end_time

    @property
    def remaining(self) -> float:
        """
        Get remaining time in seconds (can be fractional). Returns 0 if expired.
        If formatted=True, returns a string with 's' suffix and 3 decimal places.        
        """
        if self.expired:
            return 0.0
        return self.end_time - time.perf_counter()
    
    ##############
    # Public API #
    ##############
    
    def format(self, seconds:float) -> str:
        """
        Format a time duration in seconds to a string with 's' suffix and 3 decimal places.
        """
        return f'{seconds:.3f}s'
    
    def start(self) -> None:
        """
        Start or restart the timer.
        """
        self.start_time = time.perf_counter()
        self.end_time = self.start_time + self.duration

    def wait(self) -> None:
        """
        Block until the timer expires.
        If a hook is set, starts the timer, runs a progress bar loop executing the hook
        each cycle with printed output displayed below the bar and cleared each iteration.
        Otherwise, simply sleeps until expiry.
        """
        class _CaptureStream:
            """
            A stdout wrapper that counts printed lines so the progress bar
            knows how many terminal lines to clear each cycle.
            """
            def __init__(self, stream):
                self._stream = stream
                self.line_count = 0

            def write(self, text):
                self.line_count += text.count('\n')
                return self._stream.write(text)

            def flush(self):
                self._stream.flush()

            def __getattr__(self, name):
                return getattr(self._stream, name)

        if self.hook is not None:
            self.start()
            real_stdout = sys.stdout
            capture = _CaptureStream(real_stdout)
            sys.stdout = capture
            output_lines = 0

            try:
                while time.perf_counter() < self.end_time:
                    # Clear previous cycle (progress bar + hook output)
                    total_lines = output_lines + capture.line_count
                    if total_lines > 0:
                        real_stdout.write(f'\033[{total_lines}A\033[J')

                    # Render progress bar
                    progress = (time.perf_counter() - self.start_time) / self.duration
                    output_lines = self._render_progress_bar(real_stdout, progress)
                    capture.line_count = 0

                    # Call hook
                    self.hook()

                    # Yield to other threads/processes
                    time.sleep(self.yield_interval)

                # Final render: clear and draw completed bar
                total_lines = output_lines + capture.line_count
                if total_lines > 0:
                    real_stdout.write(f'\033[{total_lines}A\033[J')
                self._render_progress_bar(real_stdout, 1.0)
                real_stdout.write('\n')
                real_stdout.flush()
            finally:
                sys.stdout = real_stdout
        else:
            now = time.perf_counter()
            remaining = self.end_time - now
            if remaining > 0:
                time.sleep(remaining)

    def _render_progress_bar(self, stream, progress:float) -> int:
        try:
            cols = os.get_terminal_size().columns
        except (AttributeError, ValueError, OSError):
            cols = 80

        progress = min(1.0, max(0.0, progress))
        elapsed_t = time.perf_counter() - self.start_time
        remaining_t = max(0.0, self.duration - elapsed_t)

        label = f' {elapsed_t:.1f}s / {self.duration:.1f}s | -{remaining_t:.1f}s '
        bar_w = max(10, cols // 3)
        filled = int(bar_w * progress)
        bar = '█' * filled + '░' * (bar_w - filled)

        stream.write(f'[{bar}]{label}\n')
        stream.flush()
        return 1

# Example usage:
if __name__ == "__main__":
    t = Timely(2.0)
    print('Waiting 2 seconds ...')
    t.wait()
    print('Done.')

    # Or as countdown in a loop
    t = Timely(1.0, yield_duration=0.1)
    while not t.expired:
        print(f'Elapsed: {t.format(t.elapsed)}, Remaining: {t.format(t.remaining)}')
        
    print('Countdown finished.')
    
    def _hook():
        pass
    
    # Or with a hook: auto progress bar + hook output each cycle
    Timely(5.0, hook=_hook).wait()

    print('Hook timer finished.')
