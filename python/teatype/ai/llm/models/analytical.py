# Copyright © 2025-2026 @arsonite.
#
# This software and all its associated assets, code, designs, dialogue systems, characters, and in-game logic
# are proprietary and owned exclusively by @arsonite. Permission is granted to the user to install and play
# the game for personal use. Redistribution, resale, modification, reverse-engineering, or reuse of any part
# of the game is strictly prohibited without written permission.
#
# Third-party open-source components are used under their respective licenses.
# See /third-party-licenses.md for details.
#
# THE GAME IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
# NON-INFRINGEMENT, OR TITLE. @arsonite DOES NOT WARRANT THAT THE GAME WILL MEET YOUR
# REQUIREMENTS OR THAT OPERATION OF THE GAME WILL BE UNINTERRUPTED OR ERROR-FREE.
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# From package imports
from teatype.ai.llm.inference import Inferencer

class AnalyticalAI(Inferencer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)