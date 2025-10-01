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
import platform
import shutil
import subprocess

# From package imports
from teatype.io import shell
from teatype.logging import *

def _ensure_aria2():
    if shutil.which('aria2c'):
        return True

    system = platform.system().lower()
    warn('aria2 is not installed. Attempting to install it ...', use_prefix=False)

    try:
        if system == 'linux':
            shell('apt-get install -y aria2', sudo=True)
        elif system == 'darwin':
            shell('brew update', sudo=False)
        elif system == 'windows':
            err('Please install aria2 manually (choco install aria2 / scoop install aria2).')
            return False
        else:
            err(f'Automatic installation for {system} not implemented.')
            return False
    except subprocess.CalledProcessError as e:
        print(f'[ERROR] Installation failed: {e}')
        return False

    return shutil.which('aria2c') is not None

def fetch(url:str, filename:str=None, connections:int=16, splits:int=16):
    """
    Downloads a file using aria2 with multiple connections.
    """
    if not _ensure_aria2():
        err('aria 2 could not be installed.', exit=True)
    download_command = f'aria2c -x{connections} -s{splits} --continue=true --auto-file-renaming=false'
    if filename:
        download_command += f' -o {filename}'
    download_command += f' {url}'
    shell(download_command)