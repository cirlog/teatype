#!/usr/bin/env python3.13
from __future__ import annotations

from pathlib import Path

from teatype.cli import BaseCLI
from teatype.io import path, shell
from teatype.logging import err, hint

class ReactDashboardBase(BaseCLI):
    """Shared helpers for React dashboard CLI scripts."""

    def __init__(self,
                 auto_init: bool = True,
                 auto_parse: bool = True,
                 auto_validate: bool = True,
                 auto_execute: bool = True):
        self.repo_root = Path(path.caller_parent(reverse_depth=4))
        self.project_root = self.repo_root / 'react' / 'dashboard'
        self.logs_dir = Path(path.create(self.repo_root, 'logs'))
        self.pid_file = self.project_root / '.devserver.pid'
        super().__init__(auto_init=auto_init,
                         auto_parse=auto_parse,
                         auto_validate=auto_validate,
                         auto_execute=auto_execute)

    def _ensure_project_exists(self) -> None:
        if not self.project_root.exists():
            err(f'React dashboard sources missing at {self.project_root}.', exit=True)

    def _pnpm(self) -> str:
        pnpm_available = shell('pnpm --version', mute=True) == 0
        if pnpm_available:
            return 'pnpm'
        hint('pnpm not detected. Falling back to corepack-managed pnpm.')
        return 'corepack pnpm'
