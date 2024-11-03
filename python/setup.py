# Copyright (C) 2024-2025 Burak Günaydin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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