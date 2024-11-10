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
import os

# From package imports
from setuptools import setup, find_packages

# From-as package imports
from setuptools.command.sdist import sdist as _sdist

# Custom `sdist` command to include/exclude files from source distribution
class sdist(_sdist):
    def make_release_tree(self, base_dir, files):
        _sdist.make_release_tree(self, base_dir, files)
        # Exclude specific files
        exclude_files = ['.env', 'tests/*', '*.log', '*.pyc', 'scripts/*']
        for filename in exclude_files:
            filepath = os.path.join(base_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

setup(
    name="teatype",
    version="0.0.1",
    author="arsonite",
    author_email="notarson@gmail.com",
    description="A package for tea",
    url="https://github.com/arsonite/teatype",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Own License",
        "Operating System :: OS Independent",
    ],
    
    # Custom commands
    cmdclass={
        "sdist": sdist,  # Use the custom sdist command
    },
    
    python_requires='>=3.11',
    install_requires=[],
)