# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class ProcessDefinition:
    """Holds the configuration for an IOCManager process."""

    name: str
    command: str
    log_dir: str | Path
    port: int | None = None
    autorestart: bool = True

    @property
    def log_file(self) -> Path:
        """Returns the path to the log file for this process."""
        return Path(self.log_dir) / f"{self.name}.log"


class IOCManager(Protocol):
    """Functions as a structural interface for IOC process managers."""

    process_def: ProcessDefinition

    def is_running(self) -> bool:
        """Returns True if the managed process is currently running."""
        ...

    def start(self) -> None:
        """Starts the process if it is not already running."""
        ...

    def stop(self) -> None:
        """Stops the running process."""
        ...

    def restart(self) -> None:
        """Restarts the process, falling back to start if not running."""
        ...

    def status(self) -> None:
        """Prints the current state of the process."""
        ...

    def connect(self) -> None:
        """Opens an interactive console session to the process."""
        ...
