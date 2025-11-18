#!/usr/bin/env python3.11

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
# all copies or substantial portions of the Software.import os

# Standard library imports
import subprocess
import sys
from pathlib import Path

def setup_pypi_server():
    """
    Set up and run a local PyPI server for testing.
    """
    
    # Define paths
    home_dir = Path.home()
    server_dir = home_dir / 'srv' / 'pypi'
    packages_dir = server_dir / 'packages'
    htpasswd_file = server_dir / 'htpasswd'
    venv_dir = home_dir / 'pypi-server-venv'
    
    # Create server directories
    print('Creating server directories...')
    packages_dir.mkdir(parents=True, exist_ok=True)
    
    # Create virtual environment
    print('Creating virtual environment...')
    subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
    
    # Get venv python and pip paths
    venv_python = venv_dir / 'bin' / 'python'
    venv_pip = venv_dir / 'bin' / 'pip'
    
    # Install dependencies
    print('Installing apache-utils2...')
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'apache2-utils'], check=False)
    
    print('Installing pypiserver[passlib]...')
    subprocess.run([str(venv_pip), 'install', 'pypiserver[passlib]'], check=True)
    
    # Create htpasswd file with user
    print('Creating htpasswd file...')
    subprocess.run(
        ['htpasswd', '-sc', str(htpasswd_file), 'camera-client'],
        check=True
    )
    
    # Start PyPI server
    print('Starting PyPI server...')
    pypi_server = venv_dir / 'bin' / 'pypi-server'
    subprocess.run([
        str(pypi_server), 'run',
        '-i', '0.0.0.0',
        '-p', '8080',
        '-P', str(htpasswd_file),
        '-a', 'update,download,list',
        str(packages_dir)
    ], check=True)

if __name__ == '__main__':
    setup_pypi_server()