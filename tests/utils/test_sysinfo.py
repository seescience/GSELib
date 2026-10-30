# SPDX-License-Identifier: MIT

import pytest

from gselib.utils.sysinfo import SysInfo, sysinfo


class TestSysinfo:

    def test_os_name_is_known_value(self) -> None:
        """Tests that os_name is one of the four recognised OS identifiers."""
        assert sysinfo.os_name in ("macos", "linux", "windows", "unknown")

    def test_exactly_one_os_flag_true(self) -> None:
        """Tests that exactly one OS flag is true at a time."""
        os_flags = [sysinfo.is_mac, sysinfo.is_linux, sysinfo.is_windows, sysinfo.is_unknown]
        assert sum(os_flags) == 1

    def test_os_flag_consistent_with_os_name(self) -> None:
        """Tests that the boolean property key matches the OS name."""
        name_to_flag = {
            "macos": sysinfo.is_mac,
            "linux": sysinfo.is_linux,
            "windows": sysinfo.is_windows,
            "unknown": sysinfo.is_unknown,
        }
        assert name_to_flag[sysinfo.os_name] is True

    def test_architecture_is_not_empty_string(self) -> None:
        """Tests that the architecture string is not empty."""
        assert isinstance(sysinfo.architecture, str) and len(sysinfo.architecture) > 0

    def test_os_version_is_not_empty_string(self) -> None:
        """Tests that the OS version string is not empty."""
        assert isinstance(sysinfo.os_version, str) and len(sysinfo.os_version) > 0

    def test_hostname_is_not_empty_string(self) -> None:
        """Tests that the hostname string is not empty."""
        assert isinstance(sysinfo.hostname, str) and len(sysinfo.hostname) > 0

    def test_username_is_not_empty_string(self) -> None:
        """Tests that the username string is not empty."""
        assert isinstance(sysinfo.username, str) and len(sysinfo.username) > 0

    def test_architecture_flags_mutually_exclusive(self) -> None:
        """Tests that the architecture flags are unique."""
        assert not (sysinfo.is_arm and sysinfo.is_x86)


class TestSysinfoLogic:

    def _make_sysinfo(self, sys_platform: str, architecture: str = "x86_64") -> SysInfo:
        """Builds a SysInfo instance with controller platform and architecture values."""
        test_sysinfo = SysInfo.__new__(SysInfo)
        test_sysinfo._sys_platform = sys_platform
        test_sysinfo._architecture = architecture
        test_sysinfo._os_version = "test-os-1.0"
        return test_sysinfo

    def test_detects_macos(self) -> None:
        """Tests that sys.platform starting with darwin will have the macos string as a result."""
        assert self._make_sysinfo(sys_platform="darwin").os_name == "macos"

    def test_detects_linux(self) -> None:
        """Tests that sys.platform starting with linux will have the linux string as a result."""
        assert self._make_sysinfo(sys_platform="linux").os_name == "linux"

    def test_detects_windows_win32(self) -> None:
        """Tests that sys.platform starting with win32 will have the windows string as a result."""
        assert self._make_sysinfo(sys_platform="win32").os_name == "windows"

    def test_detects_windows_nt(self) -> None:
        """Tests that sys.platform starting with nt will have the windows string as a result."""
        assert self._make_sysinfo(sys_platform="nt").os_name == "windows"

    def test_detects_unknown(self) -> None:
        """Tests that sys.platform starting with freebsd14 will have the unknown string as a result."""
        assert self._make_sysinfo(sys_platform="freebsd14").os_name == "unknown"

    def test_arm_architecture_sets_is_arm(self) -> None:
        """Tests that the architecture arm64 sets is_arm to True."""
        arm_platform = self._make_sysinfo(sys_platform="darwin", architecture="arm64")
        assert arm_platform.is_arm is True and arm_platform.is_x86 is False

    def test_aarch64_architecture_sets_is_arm(self) -> None:
        """Tests that the architecture aarch64 sets is_arm to True."""
        arm_platform = self._make_sysinfo(sys_platform="linux", architecture="aarch64")
        assert arm_platform.is_arm is True and arm_platform.is_x86 is False

    def test_x86_architecture_sets_is_x86(self) -> None:
        """Tests that the architecture x86_64 sets is_x86 to True."""
        arm_platform = self._make_sysinfo(sys_platform="linux", architecture="x86_64")
        assert arm_platform.is_arm is False and arm_platform.is_x86 is True

    def test_is_mac_true_for_darwin(self) -> None:
        """Tests that is_mac is set to True for darwin."""
        assert self._make_sysinfo(sys_platform="darwin").is_mac is True

    def test_is_linux_true_for_linux(self) -> None:
        """Tests that is_linux is set to True for linux."""
        assert self._make_sysinfo(sys_platform="linux2").is_linux is True

    def test_is_windows_true_for_windows(self) -> None:
        """Tests that is_windows is set to True for windows."""
        assert self._make_sysinfo(sys_platform="win32").is_windows is True

