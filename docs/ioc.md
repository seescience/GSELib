# IOC

The `ioc` subpackage manages IOC processes via two backends: **procServ** (TCP-based console, asyncio port check) and **GNU Screen** (named sessions,
subprocess check). Both share the same `ProcessDefinition` and expose the same interface.

## Usage
For apps that manage multiple processes, use `IOCGroup` to get list, start-all, stop-all, and status-all operations. Individual entry points call `start()` 
then `connect()` to replicate the original start-and-attach default behavior:

```python
from gselib.ioc import IOCGroup, ProcessDefinition, ProcServManager

P1 = ProcServManager(ProcessDefinition(name="process1", command="path/to/.py/or/st.cmd", port=34567, log_dir="/tmp/app_logs"))
P2 = ProcServManager(ProcessDefinition(name="process2", command="path/to/.py/or/st.cmd", port=34568, log_dir="/tmp/app_logs"))
GROUP = IOCGroup([P1, P2])


def p1_start() -> None:
    P1.start()
    P1.connect()


def p1_stop() -> None:
    P1.stop()


def p2_start() -> None:
    P2.start()
    P2.connect()


def start_all() -> None:
    GROUP.start_all()


def stop_all() -> None:
    GROUP.stop_all()


def list_all() -> None:
    GROUP.list_all()


def status_all() -> None:
    GROUP.status_all()
```

To use the GNU Screen instead, swap `ProcServManager` for `ScreenManager`, the interface is identical.

## ProcessDefinition fields

| Field | Default | Used by |
|---|---|---|
| `name` | required | both |
| `command` | required | both |
| `log_dir` | required | both |
| `port` | `None` | ProcServManager only |
| `autorestart` | `True` | ProcServManager only |

`procserv_bin` is a constructor argument on `ProcServManager(process_def, procserv_bin="procServ")`. The running user and host are taken from the 
environment at runtime via `gselib.utils.sysinfo`. `port` and `autostart` are ignore by `ScreenManager`, do not set them when using the Screen backend.

