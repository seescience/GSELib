# SPDX-License-Identifier: MIT

import asyncio
import os
import shutil
import subprocess

from gselib.ioc.definition import ProcessDefinition
from gselib.utils import sysinfo


class ProcServManager:
    """Manages a procServ-controller IOC process."""

    def __init__(self, process_def: ProcessDefinition, procserv_bin: str = "procServ") -> None:
        self.process_def = process_def
        self._procserv_bin = procserv_bin

    def is_running(self) -> bool:
        """Returns True if the procServ port is accepting TCP connections."""
        return asyncio.run(_check_port(sysinfo.hostname, self.process_def.port))

    def start(self) -> None:
        """Starts the IOC under procServ if it is not alread running."""
        if self.process_def.port is None:
            raise ValueError(f"{self.process_def.name}: port is required for ProcServManager")
        if self.is_running():
            print(f"{self.process_def.name}: already running on port {self.process_def.port}")
            return None

        procserv_executable = shutil.which(self._procserv_bin) or self._procserv_bin
        log_path = self.process_def.log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        launch_cmd = [procserv_executable, "-n", self.process_def.name, "-L", str(log_path), str(self.process_def.port), self.process_def.command]

        if not self.process_def.autorestart:
            launch_cmd.insert(1, "--noautorestart")

        subprocess.Popen(launch_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        print(f"{self.process_def.name}: started on port {self.process_def.port}")

    def stop(self) -> None:
        """Stops the IOC by sending Ctrl-X to the procServ console."""
        if not self.is_running():
            print(f"{self.process_def.name}: not running")
            return None

        try:
            asyncio.run(_send_command(sysinfo.hostname, self.process_def.port, b"\x18"))
            print(f"{self.process_def.name}: stop signal sent")
        except Exception as e:
            print(f"{self.process_def.name}: failed to send stop signal: {e}")

    def restart(self) -> None:
        """Stops and then restarts the IOC under procServ."""
        if not self.is_running():
            print(f"{self.process_def.name}: not running, starting instead")
            self.start()
            return None

        self.stop()
        self.start()

    def status(self) -> None:
        """Prints RUNNING or STOPPED with port number."""
        state = "RUNNING" if self.is_running() else "STOPPED"
        print(f"{self.process_def.name}: {state} (port {self.process_def.port})")

    def connect(self) -> None:
        """Replaces the current process with an interactive telnet session."""
        telnet = shutil.which("telnet")
        if telnet is None:
            raise RuntimeError("telnet not found on PATH")
        os.execlp(telnet, "telnet", sysinfo.hostname, str(self.process_def.port))


async def _check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Returns True if a TCP connection to host:port succeeds within the given timeout."""
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except OSError, asyncio.TimeoutError:
        return False


async def _send_command(host: str, port: int, data: bytes, timeout: float = 3.0) -> None:
    """Opens a TCP connection, sends data, and then closes."""
    _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
    writer.write(data)
    await writer.drain()
    writer.close()
    await writer.wait_closed()
