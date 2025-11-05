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

import time

class Timer:
    def __init__(self, duration: float):
        """
        Initialize a precise timer.
        
        Args:
            duration (float): The duration in seconds (can be fractional).
        """
        self.duration = duration
        self.start_time = time.perf_counter() # higher resolution than time.time()
        self.end_time = self.start_time + duration

    def wait(self):
        """
        Block until the timer expires.
        """
        now = time.perf_counter()
        remaining = self.end_time - now
        if remaining > 0:
            time.sleep(remaining)

    def expired(self) -> bool:
        """
        Check if the timer has expired.
        """
        return time.perf_counter() >= self.end_time

    def remaining(self) -> float:
        """
        Get remaining time in seconds (can be fractional, negative if expired).
        """
        return self.end_time - time.perf_counter()

# Example usage:
if __name__ == "__main__":
    t = Timer(5.0)   # precise 5 seconds
    print('Waiting...')
    t.wait()
    print('Done.')

    # Or as countdown in a loop
    t = Timer(3.0)
    while not t.expired():
        print(f'Remaining: {t.remaining():.3f}s')
        time.sleep(0.5)
    print('Countdown finished.')
