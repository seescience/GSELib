# Utils

The `utils` subpackage provies lightweight runtime helpers. Currently includes platform and architecture detection via a pre-built `sysinfo` singleton,
and a simple cross-platform file lock backed by a lock file on disk.

## Usage

### SysInfo
```python
from gselib.utils import sysinfo

# OS checks
if sysinfo.is_mac:
    ...
elif sysinfo.is_linux:
    ...
elif sysinfo.is_windows:
    ...


# Architecture checks
if sysinfo.is_arm:
    ...
elif sysinfo.is_x86:
    ...


# Raw values
print(sysinfo.os_name)  # 'macos' | 'linux' | 'windows' | 'unknown'
print(sysinfo.architecture)  # e.g. 'arm64', 'x86_64'
print(sysinfo.ov_version)  # full platform string
```

### FileLock
```python
from gselib.utils import FileLock, FileLockException

# Context manager (recommened)
with FileLock("/data/project.h5"):
    # exclusive access here
    ...

# Manual acquire/release
lock = FileLock("/data/project.h5", timeout=30.0, delay=0.1)
lock.acquire()
try:
    ...
finally:
    lock.release()

# Inspect who holds the lock
print(lock.lock_info)
```

#### Handling timeouts
```python
try:
    with FileLock('data/project.h5', timeout=5.0)
        ...
except FileLockException:
    print("Could not acquire lock within 5 seconds")
```

