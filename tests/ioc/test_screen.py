# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock, patch

import pytest

from gselib.ioc import ProcessDefinition, ScreenManager


_PATCH = "gselib.ioc.screen.subprocess.run"


@pytest.fixture()
def proc_def() -> ProcessDefinition:
    return ProcessDefinition(name="test_ioc", command="/usr/local/iocs/test/st.cmd", log_dir="/tmp/gselib_test_logs")


@pytest.fixture()
def manager(proc_def) -> ScreenManager:
    return ScreenManager(proc_def)


def _ls_running() -> MagicMock:
    return MagicMock(stdout="12345.test_ioc\t(Detached)\n")


def _ls_stopped() -> MagicMock:
    return MagicMock(stdout="No Sockets found.\n")


class TestScreenManager:
    def test_returns_false_when_session_absent(self, manager: ScreenManager) -> None:
        """Tests that is_running returns False when the session name is not in the screen -ls."""
        with patch(_PATCH, return_value=_ls_stopped()):
            assert manager.is_running() is False

    def test_returns_true_when_session_present(self, manager: ScreenManager) -> None:
        """Tests that is_running returns True when the session name appears in the screen -ls."""
        with patch(_PATCH, return_value=_ls_running()):
            assert manager.is_running() is True

    def test_stop_when_running_sends_quit(self, manager: ScreenManager, capsys: pytest.CaptureFixture[str]) -> None:
        """Tests that stop() sends 'screen -X quit' when the session exists."""
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return _ls_running()

        with patch(_PATCH, side_effect=fake_run):
            manager.stop()
        assert any("quit" in cmd for cmd in calls)

    def test_stopped_status(self, manager: ScreenManager, capsys: pytest.CaptureFixture[str]) -> None:
        """Tests that status() prints STOPPED when no session exists."""
        with patch(_PATCH, return_value=_ls_stopped()):
            manager.status()
        assert "STOPPED" in capsys.readouterr().out

    def test_running_status(self, manager: ScreenManager, capsys: pytest.CaptureFixture[str]) -> None:
        """Tests that status() prints RUNNING when the session exists."""
        with patch(_PATCH, return_value=_ls_running()):
            manager.status()
        assert "RUNNING" in capsys.readouterr().out
