# SPDX-License-Identifier: MIT

import threading
import time
from contextlib import suppress
from pathlib import Path

import pytest

from gselib.utils import FileLock, FileLockException


@pytest.fixture()
def lock_path(tmp_path: Path) -> Path:
    return tmp_path / "test_file.h5"


class TestFileLockBasics:
    def test_context_manager(self, lock_path: Path) -> None:
        """Tests that the lock is held inside the context block and released on exit."""
        expected_lock_file = lock_path.parent / f"{lock_path.name}.lock"
        with FileLock(lock_path) as lock:
            assert lock.is_locked
            assert expected_lock_file.exists()
        assert not lock.is_locked
        assert not expected_lock_file.exists()

    def test_acquire_release(self, lock_path: Path) -> None:
        """Tests that acquire sets is_lock to True and release sets it back to False."""
        lock = FileLock(lock_path)
        lock.acquire()
        assert lock.is_locked
        lock.release()
        assert not lock.is_locked

    def test_lock_file_created_and_removed(self, lock_path: Path) -> None:
        """Tests that the lock file exsists on disck while locked and is removed on release."""
        lock_file = lock_path.parent / f"{lock_path.name}.lock"
        with FileLock(lock_path):
            assert lock_file.exists()
        assert not lock_file.exists()

    def test_calling_release_twice(self, lock_path: Path) -> None:
        """Tests that calling release twice doesn't raise an error."""
        lock = FileLock(lock_path)
        lock.acquire()
        lock.release()
        lock.release()


class TestFileLockBlocking:
    def test_timeout_when_already_locked(self, lock_path: Path) -> None:
        """Tests that a second lock on the same file raises FileLockException after timeout."""
        first_lock = FileLock(lock_path, timeout=0.1, delay=0.01)
        second_lock = FileLock(lock_path, timeout=0.1, delay=0.01)
        first_lock.acquire()
        try:
            with pytest.raises(FileLockException):
                second_lock.acquire()
        finally:
            first_lock.release()

    def test_second_lock_succeeds_after_release(self, lock_path: Path) -> None:
        """Tests that a second lock can be acquired once the first lock is released."""
        first_lock = FileLock(lock_path, timeout=0.1)
        second_lock = FileLock(lock_path, timeout=0.1)
        first_lock.acquire()
        first_lock.release()
        second_lock.acquire()
        assert second_lock.is_locked
        second_lock.release()

    def test_threading_mutual_exclusion(self, lock_path: Path) -> None:
        """Tests that concurrent threads acquire the lock one at a time with no overlap."""
        acquired_times = []
        errors = []

        def worker():
            try:
                with FileLock(lock_path, timeout=2.0, delay=0.01):
                    acquired_times.append(time.time())
                    time.sleep(0.05)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert not errors, f"Thread errors: {errors}"
        assert len(acquired_times) == 4
        for i in range(1, len(acquired_times)):
            assert acquired_times[i] >= acquired_times[i - 1] + 0.04, "Overlap found. Two threads held the lock at the same time."

    def test_lock_info_in_none_when_not_locked(self, lock_path: Path) -> None:
        """Tests that the lock info returns None when no lock file exists."""
        lock = FileLock(lock_path)
        assert lock.lock_info is None

    def test_exception_in_context_block_releases_lock(self, lock_path: Path) -> None:
        """Tests that if an exception is raised inside the context block the lock is still released."""
        lock_file = lock_path.parent / f"{lock_path.name}.lock"
        with suppress(ValueError):
            with FileLock(lock_path):
                assert lock_file.exists()
                raise ValueError("Intentional error")
        assert not lock_file.exists()
