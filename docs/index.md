# GSELib

A collection of tools for GSECARS/SEES.

## Installation

```bash
pip install gselib            # base (no extras)
pip install 'gselib[cloud]'   # with Nextcloud support
pip install 'gselib[logbook]' # with Google Docs logbook support
pip install 'gselib[all]'     # everything
```

## Modules

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Cloud
:link: cloud
:link-type: doc

Storage and share management for cloud services. Currently supports Nextcloud via REST API and `occ`.
:::

:::{grid-item-card} IOC
:link: ioc
:link-type: doc

Manages IOC processes via procServ or GNU Screen. Uses `IOCGroup` to manage multiple processes as a unit with list, start-all, stop-all,
and status-all, and wires per-process entry points for start/connect.
:::

:::{grid-item-card} Logbook
:link: logbook
:link-type: doc

Beamline logbook backed by Google Docs. Append timestamped entries, export to PDF, and share with your team in real time.
:::

:::{grid-item-card} Utils
:link: utils
:link-type: doc

Lightweight runtime helpers. Includes a pre-build `sysinfo` singleton for boolean OS and CPU architecture checks, and a cross-platform
file locking via a lock file on disk. `FileLock` can be used as a context manager to guarantee exclusive access to shared files across
processes and threads, with no extra depedencies.
:::

:::{grid-item-card} API Reference
:link: autoapi/index
:link-type: doc

Auto-generated reference for all public classes and functions.
:::

::::

```{toctree}
:maxdepth: 2
:hidden:

cloud
ioc
logbook
utils
API Reference <autoapi/index>
```
