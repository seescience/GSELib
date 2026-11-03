# SPDX-License-Identifier: MIT

import asyncio
import socket
import threading
from contextlib import suppress

import pytest

from gselib.ioc import ProcessDefinition, ProcServManager
from gselib.ioc.procserv import _check_port


@pytest.fixture()
def proc_def() -> ProcessDefinition:
    return ProcessDefinition(name="test_ioc", command="/usr/local/iocs/test/st.cmd", port=29999, log_dir="/tmp/gselib_test_logs")


@pytest.fixture()
def manager(proc_def: ProcessDefinition) -> ProcServManager:
    return ProcServManager(proc_def)


class TestProcServManager:
    def test_is_running_returns_false_for_closed_port(self, manager: ProcServManager) -> None:
        """Tests that is_running returns False when nothing is listening on the port."""
        assert manager.is_running() is False

    def test_restart_when_not_running_calls_start(self, manager: ProcServManager, capsys: pytest.CaptureFixture[str]) -> None:
        """Tests that restart() falls back to start when the process is not running."""
        manager.start = lambda: print("start called")
        manager.restart()
        assert "start called" in capsys.readouterr().out


class TestCheckPort:
    def start_echo_server(self) -> tuple[int, threading.Thread]:
        """Starts a minimal TCP listener on an OS-assigned port."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("127.0.0.1", 0))
        port = server_socket.getsockname()[1]
        server_socket.listen(1)

        def accept_and_close() -> None:
            with suppress(Exception):
                client_conn, _ = server_socket.accept()
                client_conn.close()
            server_socket.close()

        thread = threading.Thread(target=accept_and_close, daemon=True)
        thread.start()
        return port, thread

    def test_closed_port_returns_false(self) -> None:
        """Tests that _check_port returns False when nothing is listening."""
        assert asyncio.run(_check_port("127.0.0.1", 1, timeout=0.5)) is False

    def test_open_port_returns_true(self) -> None:
        """Tests that _check_port returns Truen when a listener is accepting connections."""
        port, _ = self.start_echo_server()
        assert asyncio.run(_check_port("127.0.0.1", port, timeout=1.0)) is True
