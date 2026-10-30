# Utils

The `utils` subpackage provies lightweight runtime helpers. Currently includes platform and architecture detection via a pre-built `sysinfo` singleton.

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
print(sysinfo.os_name)          # 'macos' | 'linux' | 'windows' | 'unknown' 
print(sysinfo.architecture)     # e.g. 'arm64', 'x86_64'
print(sysinfo.ov_version)       # full platform string
```
