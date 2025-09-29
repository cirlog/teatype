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

from .dt import dt
# TODO: Deactivated until auto updating all components is possible
# from .fastjson import compress as compress_json
# from .fastjson import decompress as decompress_json
# from .fastjson import dump as dump_json
# from .fastjson import load as load_json
from .generate_id import generate_id
from .kebabify import kebabify, unkebabify
from .implemented_trap import implemented_trap
from .SingletonMeta import SingletonMeta
from .staticproperty import staticproperty
from .stopwatch import GLOBAL_STOPWATCH_CONFIG, stopwatch
from .Timer import Timer