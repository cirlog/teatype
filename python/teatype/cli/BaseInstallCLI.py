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
from teatype.cli import BaseCLI

# TODO: Write base install script that creates dist folder, adds it to .gitignore if not yet exists,
#       and creates an install flag file in the dist folder where everytime the install script is
#       executed, append the exact time and date of the installation and whether it was successful or not
#       into the install flag file.
# TODO: Write optional flag to disable adding dist to .gitignore
class BaseInstallCLI(BaseCLI):
    def meta(self):
        return {
            'name': 'install',
            'shorthand': 'i',
            'help': 'Install a package/module',
            'flags': [
                {
                    'short': 'ng',
                    'long': 'no-gitignore',
                    'help': 'Do not add the dist directory to the .gitignore file',
                    'required': False
                }
            ]
        }

    def execute(self):
        pass