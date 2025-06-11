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
from teatype.cli import BaseCLI

class BaseTUI(BaseCLI):
    def execute(self):
        self.run()
        
    @abstractmethod
    def run(self):
        """
        This method should be implemented by subclasses to define the specific
        functionality of the TUI.
        """
        raise NotImplementedError('Subclasses must implement the run method.')