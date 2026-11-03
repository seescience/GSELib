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


class IOCGroup:
    """Manages a collection of IOCManager instances as a unit."""

    def __init__(self, managers: list[IOCManager]) -> None:
        self._managers = managers

    def list_all(self) -> None:
        """Prints the name, port, and command for every process."""
        print(f" {'NAME':<20} {'PORT':<8} COMMAND")
        print("-" * 60)

        for manager in self._managers:
            process_def = manager.process_def
            port = str(process_def.port) if process_def is not None else "-"
            print(f" {process_def.name:<20} {port:<8} {process_def.command}")

    def start_all(self) -> None:
        """Starts all processes that are not already running."""
        for manager in self._managers:
            manager.start()

    def stop_all(self) -> None:
        """Stops all running processes."""
        for manager in self._managers:
            manager.stop()

    def restart_all(self) -> None:
        """Restarts every process."""
        for manager in self._managers:
            manager.restart()

    def status_all(self) -> None:
        """Prints the running state of every process."""
        for manager in self._managers:
            manager.status()
