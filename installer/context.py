from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import logging


@dataclass
class TaskResult:
    id: str
    status: str
    details: str
    fatal: bool = False


@dataclass
class ComponentSpec:
    id: str
    description: str
    default_enabled: bool = True
    fatal: bool = True


@dataclass
class InstallerContext:
    repo_root: Path
    assets_dir: Path
    profile: str
    dry_run: bool
    refresh_targets: list[str]
    real_user: str
    user_home: Path
    logger: logging.Logger
    log_dir: Path = Path("/var/log/beans")
    desktop_dir: Path = field(init=False)
    user_state_dir: Path = field(init=False)
    user_local_share_dir: Path = field(init=False)
    results: list[TaskResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.desktop_dir = self.user_home / "Desktop"
        self.user_state_dir = self.user_home / ".local" / "state" / "beans"
        self.user_local_share_dir = self.user_home / ".local" / "share" / "beans"
