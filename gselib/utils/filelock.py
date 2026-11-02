# SPDX-License-Identifier: MIT

import errno
import os
import time
from contextlib import suppress
from pathlib import Path

from gselib.utils.sysinfo import sysinfo


class FileLockException(Exception):
    """Exception raised when a FileLock cannot be acquired within the timeout."""

    def __init__(self, file_name: Path, lock_file: Path, timeout: float, lock_info: str | None = None) -> None:
        self.file_name = file_name
        self.lock_file = lock_file
        self.timeout = timeout
        self.lock_info = lock_info

        owner = f" - held by: {lock_info}" if lock_info else ""
        super().__init__(f"Could not acquire lock on {file_name} within {timeout}s{owner}")


class FileLock:
    """Cross-platform file lock backed by a lock file on disk."""

    def __init__(self, file_name: str | Path, timeout: float = 10.0, delay: float = 0.05) -> None:
        self.file_name = Path(file_name).resolve()
        self.lock_file = self.file_name.parent / f"{self.file_name.name}.lock"
        self.timeout = timeout
        self.delay = delay
        self.is_locked = False

    @property
    def lock_info(self) -> str | None:
        """Returns the contents of the lock file if it exists, otherwise None."""
        try:
            return self.lock_file.read_text()
        except Exception:
            return None

    def acquire(self) -> None:
        """Acquires the lock, polling for the given delay seconds until the give timeout."""
        deadline = time.monotonic() + self.timeout

        while True:
            try:
                fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)

                with os.fdopen(fd, "w") as fh:
                    fh.write(f"pid={os.getpid()} host={sysinfo.hostname} user={sysinfo.username}")
                self.is_locked = True

                return None
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if time.monotonic() >= deadline:
                    raise FileLockException(self.file_name, self.lock_file, self.timeout, self.lock_info)
                time.sleep(self.delay)

    def release(self) -> None:
        """Releases the lock by removing the lock file."""
        if self.is_locked:
            with suppress(FileNotFoundError):
                self.lock_file.unlink()
            self.is_locked = False

    def __enter__(self) -> "FileLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    def __repr__(self) -> str:
        return f"FileLock(file={self.file_name}, locked={self.is_locked}, timeout={self.timeout}s)"
