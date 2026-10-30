# SPDX-License-Identifier: MIT

import getpass
import platform
import socket
import sys
from functools import cached_property


class SysInfo:
    """Creates an immutable snapshot of the current runtime platform."""
    
    def __init__(self) -> None:
        self._sys_platform = sys.platform
        self._architecture = platform.machine().lower()
        self._os_version = platform.platform()

    @cached_property
    def os_name(self) -> str:
        """Returns a human-readable OS name (macos, linux, windows, or unknown)."""
        if self._sys_platform.startswith("linux"):
            return "linux"
        if self._sys_platform.startswith("darwin"):
            return "macos"
        if self._sys_platform.startswith("win") or self._sys_platform.startswith("nt"):
            return "windows"
        return "unknown"

    @cached_property
    def architecture(self) -> str:
        """Returns the CPU architecture (e.g. arm64, x86_64, amd64)."""
        return self._architecture

    @cached_property
    def os_version(self) -> str:
        """Returns the full OS version string."""
        return self._os_version

    @cached_property
    def is_mac(self) -> bool:
        """Returns true when running on macOS."""
        return self.os_name == "macos"

    @cached_property
    def is_linux(self) -> bool:
        """Returns true when running on linux."""
        return self.os_name == "linux"

    @cached_property
    def is_windows(self) -> bool:
        """Returns true when running on windows."""
        return self.os_name == "windows"
    
    @cached_property
    def is_unknown(self) -> bool:
        """Returns true when the platform is not macos, linux, or windows."""
        return self.os_name == "unknown"

    @cached_property
    def is_arm(self) -> bool:
        """Returns true when running on an ARM processor."""
        return self.architecture.startswith("arm") or self.architecture == "aarch64"

    @cached_property
    def is_x86(self) -> bool:
        """Returns true when running on an x86/x86_64 processor."""
        return self.architecture in ("x86_64", "amd64", "i386", "i686")

    @cached_property
    def hostname(self) -> str:
        """Returns the hostname."""
        return socket.gethostname()

    @cached_property
    def username(self) -> str:
        """Returns the current OS user."""
        return getpass.getuser()

    def __repr__(self) -> str:
        return f"SysInfo(os_name={self.os_name!r}, os_version={self.os_version!r}, architecture={self.architecture!r}), {self.hostname=}, {self.username=}"


sysinfo = SysInfo()

