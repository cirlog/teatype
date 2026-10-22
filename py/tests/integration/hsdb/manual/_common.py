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

# Shared by the manual HSDB scripts: data goes to teatype/dist/hsdb/<DB_NAME>/ (dist is gitignored)

# Standard-library imports
from pathlib import Path

# Third-party imports
from teatype.io import env, path

DB_NAME = 'school'
DIST = Path(path.caller_parent(reverse_depth=6)) / 'dist'

# Host and clients resolve the database folder from this, so none of them needs a path argument
env.set('HSDB_ROOT_PATH', str(DIST))