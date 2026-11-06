"""Shared pytest setup for test_ingest.py.

- No __pycache__ folders are left in this folder.
- The real books.db and ingestion-log.json in this folder must be exactly the
  same after the tests as before them (including "still doesn't exist").
"""

import hashlib
import sys
from pathlib import Path

import pytest

# Stop Python from writing .pyc files for ingest.py and test_ingest.py.
sys.dont_write_bytecode = True

FOLDER = Path(__file__).resolve().parent
REAL_FILES = [FOLDER / "books.db", FOLDER / "ingestion-log.json"]
PYCACHE = FOLDER / "__pycache__"


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


@pytest.fixture(scope="session", autouse=True)
def real_files_untouched():
    before = {path.name: fingerprint(path) for path in REAL_FILES}
    yield
    after = {path.name: fingerprint(path) for path in REAL_FILES}
    assert after == before, "the tests changed the real books.db or ingestion-log.json"


def pytest_sessionfinish(session, exitstatus):
    # pytest compiles this file before sys.dont_write_bytecode takes effect,
    # so remove the compiled copies of these files, and the folder if it's empty.
    if PYCACHE.exists():
        for compiled in PYCACHE.glob("*.pyc"):
            if compiled.name.split(".")[0] in ("conftest", "test_ingest", "ingest"):
                compiled.unlink()
        if not any(PYCACHE.iterdir()):
            PYCACHE.rmdir()
