# SPDX-License-Identifier: MIT

import os
import re
import shlex
import shutil
import subprocess

from gselib.ioc.definition import ProcessDefinition


class ScreenManager:
    """Manages an IOC process inside a GNU screen session."""

    def __init__(self, process_def: ProcessDefinition) -> None:
        self.process_def = process_def

    def is_running(self) -> bool:
        """Returns True if a screen session with this name exists."""
        result = subprocess.run(["screen", "-ls"], capture_output=True, text=True)
        return bool(re.search(rf"\.{re.escape(self.process_def.name)}\b", result.stdout))

    def start(self) -> None:
        """Starts the IOC in a detached, logged screen session."""
        if self.is_running():
            print(f"{self.process_def.name}: already running in screen session")

        log_path = self.process_def.log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        launch_cmd = ["screen", "-dmS", self.process_def.name, "-L", "-Logfile", str(log_path)] + shlex.split(self.process_def.command)

        subprocess.run(launch_cmd, check=True)
        print(f"{self.process_def.name}: started in screen session '{self.process_def.name}'")

    def stop(self) -> None:
        """Stops the IOC by sending quit to the screen session."""
        if not self.is_running():
            print(f"{self.process_def.name}: not running")
            return None

        subprocess.run(["screen", "-S", self.process_def.name, "-X", "quit"])
        print(f"{self.process_def.name}: stopped")

    def restart(self) -> None:
        """Stops and then restarts the screen session."""
        if not self.is_running():
            print(f"{self.process_def.name}: not running, started instead")
            self.start()
            return None

        self.stop()
        self.start()

    def status(self) -> None:
        """Prints RUNNING or STOPPED with session name."""
        state = "RUNNING" if self.is_running() else "STOPPED"
        print(f"{self.process_def.name}: {state} (screen session '{self.process_def.name}')")

    def connect(self) -> None:
        """Replaces the current process with an interactive screen reattach."""
        screen = shutil.which("screen")
        if screen is None:
            raise RuntimeError("screen not found on PATH")
        os.execlp(screen, "screen", "-r", self.process_def.name)
