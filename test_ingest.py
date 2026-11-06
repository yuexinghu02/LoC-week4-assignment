"""Tests that ingest.py does what rules.md says.

Every test points to the rule or decision in rules.md it checks. Each test
loads into its own test.db and test-log.json in a new temporary folder, and
removes them afterwards, whether it passed or failed. The real books.db and
ingestion-log.json in this folder are never used (see conftest.py).

Run with:  python -m pytest
"""

import csv
import json
import shutil
import sqlite3
import tempfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

import pytest

import ingest

FOLDER = Path(__file__).resolve().parent
BOOKS = FOLDER / "books.csv"
BATCH2 = FOLDER / "books-batch2.csv"
WARNING_GROUPS = ("needs_decision", "needs_lookup", "check_this")


# ---------------------------------------------------------------------------
# Setup and teardown
# ---------------------------------------------------------------------------

@dataclass
class Workspace:
    folder: Path
    db: Path
    log: Path

    def run(self, csv_path):
        """Load a file the way `python ingest.py <file>` does, into test.db."""
        return ingest.main(["ingest.py", str(csv_path)])

    def log_entries(self):
        return json.loads(self.log.read_text(encoding="utf-8"))

    def query(self, sql, params=()):
        with closing(sqlite3.connect(self.db)) as con:
            return con.execute(sql, params).fetchall()


@pytest.fixture
def workspace(monkeypatch):
    """A temporary folder holding test.db and test-log.json, removed afterwards.

    ingest.py keeps its database and log next to itself, so its paths are
    pointed at the temporary folder for the length of the test.
    """
    folder = Path(tempfile.mkdtemp(prefix="ingest-test-"))
    space = Workspace(folder, folder / "test.db", folder / "test-log.json")
    monkeypatch.setattr(ingest, "HERE", folder)
    monkeypatch.setattr(ingest, "DB_PATH", space.db)
    monkeypatch.setattr(ingest, "LOG_PATH", space.log)
    try:
        yield space
    finally:
        space.db.unlink(missing_ok=True)
        space.log.unlink(missing_ok=True)
        shutil.rmtree(folder, ignore_errors=True)
        assert not folder.exists(), f"{folder} was not removed"


# ---------------------------------------------------------------------------
# Building small CSV files for the examples
# ---------------------------------------------------------------------------

def book_row(book_id, isbn="", isbn13="", title=None):
    """A row with the given ISBNs. The other columns are filled in so they
    cause no warnings of their own: the star counts add up to
    work_ratings_count, and average_rating matches them (Decision 23)."""
    stars = [10, 20, 30, 40, 50]  # 150 ratings, average 550 / 150 = 3.67
    row = {
        "book_id": str(book_id), "goodreads_book_id": str(800000 + book_id),
        "best_book_id": str(800000 + book_id), "work_id": str(900000 + book_id),
        "books_count": "1", "isbn": isbn, "isbn13": isbn13, "authors": "Test Author",
        "original_publication_year": "2000.0", "original_title": title or f"Test Book {book_id}",
        "title": title or f"Test Book {book_id}", "language_code": "eng",
        "average_rating": "3.67", "ratings_count": "150", "work_ratings_count": "150",
        "work_text_reviews_count": "5", "image_url": "", "small_image_url": "",
    }
    row.update({f"ratings_{i}": str(n) for i, n in enumerate(stars, start=1)})
    return row


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ingest.EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


# ---------------------------------------------------------------------------
# One test for every example in the examples table in rules.md
# ---------------------------------------------------------------------------

# Each example: the row's ISBN values, and what the table says should happen.
#   column:   the column the table's Result is about
#   status:   the status the table names (None when it names none, like "moved")
#   cleaned:  the cleaned value in that column (None means empty)
#   original: checked when the table says "original kept"
#   also:     other columns the table's Cleaned value names
#   warning:  True when the table's Result says "warning"
E = dict  # short alias to keep the table below readable
EXAMPLES = [
    E(n=1, isbn="0439139600", column="isbn", status="ok", cleaned="0439139600"),
    E(n=2, isbn="043965548X", column="isbn", status="ok", cleaned="043965548X"),
    E(n=3, isbn="439023483", column="isbn", status="repaired", cleaned="0439023483"),
    E(n=4, isbn="61120081", column="isbn", status="repaired", cleaned="0061120081"),
    E(n=5, isbn="0-450-19827-8", column="isbn", status="repaired", cleaned="0450198278"),
    E(n=6, isbn=" 162 001 4750 ", column="isbn", status="repaired", cleaned="1620014750"),
    E(n=7, isbn="031200009x", column="isbn", status="repaired", cleaned="031200009X"),
    E(n=8, isbn="9781982147600", column="isbn", status="repaired", cleaned="1982147601",
      also={"isbn13": "9781982147600"}, warning=True),
    E(n=9, isbn="", isbn13="9780062398123", column="isbn", status="repaired", cleaned="0062398121"),
    E(n=10, isbn="1416524797", column="isbn", status="ok", cleaned="1416524797", warning=True),
    E(n=11, isbn="385535144", column="isbn", status="rejected", cleaned=None, original="385535144"),
    E(n=12, isbn="04390A3483", column="isbn", status="rejected", cleaned=None, original="04390A3483"),
    E(n=13, isbn="15287463097", column="isbn", status="rejected", cleaned=None, original="15287463097"),
    E(n=14, isbn13="9798351220413", column="isbn13", status="ok", cleaned="9798351220413"),
    E(n=15, isbn="439023483", isbn13="9.78043902348e+12", column="isbn13", status="repaired",
      cleaned="9780439023481"),
    E(n=16, isbn13="9.78067172365e+12", column="isbn13", status="inferred", cleaned="9780671723651",
      warning=True),
    E(n=17, isbn13="9.7804251888e+12", column="isbn13", status="rejected", cleaned=None,
      original="9.7804251888e+12"),
    E(n=18, isbn="446612707", isbn13="9.78055381395e+12", column="isbn13", status="repaired",
      cleaned="9780446612708", warning=True),
    E(n=19, isbn13="2.94001623192e+12", column="isbn13", status=None, cleaned=None,
      also={"other_id": "2.94001623192e+12"}),
    E(n=20, isbn="553609416", isbn13="76783609419.0", column="isbn13", status="repaired",
      cleaned="9780553609417", also={"other_id": "076783609419"}),
    E(n=21, isbn="9380658797", isbn13="97893806587.0", column="isbn13", status="rejected", cleaned=None,
      original="97893806587.0"),
    E(n=22, column="isbn13", status=None, cleaned=None, also={"isbn": None}),
    E(n=23, isbn13="978-0-306-40615-7", column="isbn13", status="repaired", cleaned="9780306406157"),
    E(n=24, isbn13="9780306406158", column="isbn13", status="rejected", cleaned=None,
      original="9780306406158"),
    E(n=25, isbn="1234567890", column="isbn", status="rejected", cleaned=None, original="1234567890"),
    E(n=26, isbn="ISBN 0-306-40615-2", column="isbn", status="repaired", cleaned="0306406152"),
    E(n=27, isbn13="URN:ISBN:978-92-95055-12-4", column="isbn13", status="repaired",
      cleaned="9789295055124"),
    E(n=28, isbn13="ISBN 978-951-45-9693-3 (hardback)", column="isbn13", status="repaired",
      cleaned="9789514596933"),
    E(n=29, isbn13="9790007672393", column="isbn13", status=None, cleaned=None,
      also={"other_id": "9790007672393"}),
    E(n=30, isbn13="978-92-95055-12-4 90000", column="isbn13", status="rejected", cleaned=None,
      original="978-92-95055-12-4 90000"),
]

BOOK_ID = 1  # the example's own row
ANGELS_AND_DEMONS_ID = 2  # example 10's second book, with the same ISBN


@pytest.mark.parametrize("ex", EXAMPLES, ids=[f"example-{ex['n']:02d}" for ex in EXAMPLES])
def test_example(workspace, ex):
    """rules.md "Examples" table: each value ends up as its row says."""
    rows = [book_row(BOOK_ID, ex.get("isbn", ""), ex.get("isbn13", ""))]
    if ex["n"] == 10:
        # The table: "it's also Angels & Demons' ISBN, so both rows get a warning".
        rows.append(book_row(ANGELS_AND_DEMONS_ID, "1416524797", title="Angels & Demons"))
    assert workspace.run(write_csv(workspace.folder / "example.csv", rows)) == 0

    column = ex["column"]
    stored = workspace.query(
        f"SELECT {column}, {column}_status, {column}_original, isbn, isbn13, other_id "
        "FROM books WHERE book_id = ?", (BOOK_ID,))
    assert len(stored) == 1, "the example's book should be loaded exactly once"
    cleaned, status, original, isbn, isbn13, other_id = stored[0]
    columns = {"isbn": isbn, "isbn13": isbn13, "other_id": other_id}

    assert cleaned == ex["cleaned"]
    if ex["status"] is not None:
        assert status == ex["status"]
    if "original" in ex:
        assert original == ex["original"]
    for name, value in ex.get("also", {}).items():
        assert columns[name] == value, f"{name}"

    if ex.get("warning"):
        warned = isbn_warnings(workspace.log_entries()[-1])
        assert str(BOOK_ID) in warned, "the table says this value gets a warning"
        if ex["n"] == 10:
            assert str(ANGELS_AND_DEMONS_ID) in warned, "both rows get a warning"


def isbn_warnings(entry):
    """book_ids with a warning about an ISBN column in one log entry."""
    return {w["book_id"] for group in WARNING_GROUPS for w in entry[group]
            if w["column"] in ("isbn", "isbn13")}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def test_same_file_twice_creates_no_duplicates(workspace):
    """Rule 12.5: loading the same file twice changes nothing. Decision 17:
    an exact duplicate row in the file (book 10001 appears twice) is loaded once."""
    workspace.run(BATCH2)
    books_after_first = workspace.query("SELECT COUNT(*) FROM books")[0][0]
    workspace.run(BATCH2)
    books_after_second = workspace.query("SELECT COUNT(*) FROM books")[0][0]

    assert books_after_second == books_after_first
    assert workspace.log_entries()[-1]["counts"]["loaded"] == 0
    assert workspace.query("SELECT work_id FROM books GROUP BY work_id HAVING COUNT(*) > 1") == []
    assert workspace.query("SELECT COUNT(*) FROM books WHERE book_id = 10001")[0][0] == 1


def test_every_run_adds_a_log_entry_without_overwriting(workspace):
    """Decision 28: each run adds its entry to the end of ingestion-log.json, and
    earlier entries are never changed. Decision 4: failed runs are logged too."""
    workspace.run(BATCH2)
    first = workspace.log_entries()
    assert len(first) == 1

    workspace.run(BATCH2)
    second = workspace.log_entries()
    assert len(second) == 2
    assert second[0] == first[0]

    workspace.run(workspace.folder / "no-such-file.csv")
    third = workspace.log_entries()
    assert len(third) == 3
    assert third[:2] == second
    assert third[2]["status"] == "failed"


def test_counts_add_up_to_rows_read(workspace):
    """Rule 13 section 2 and Decision 1: loaded + updated + skipped + rejected
    equals the rows read. Loading batch 2 after books.csv gives Rule 13's table:
    14 new, 4 updated, 12 already loaded, 1 duplicate skipped, 31 in total."""
    workspace.run(BOOKS)
    workspace.run(BATCH2)
    entries = workspace.log_entries()
    assert len(entries) == 2

    for entry in entries:
        counts = entry["counts"]
        total = (counts["loaded"] + counts["updated"]
                 + counts["skipped_already_exist"] + counts["rejected"])
        assert total == counts["rows_read"], entry["file"]["given"]
        assert entry["adds_up"] is True

    assert entries[1]["counts"] == {"rows_read": 31, "loaded": 14, "updated": 4,
                                    "skipped_already_exist": 12, "rejected": 1}


def database_contents(db):
    """Every table's rows, without the run times (Decision 29), which differ on every run."""
    contents = {}
    with closing(sqlite3.connect(db)) as con:
        tables = [t for (t,) in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
        for table in tables:
            columns = [c[1] for c in con.execute(f"PRAGMA table_info({table})")
                       if c[1] not in ("started_at", "finished_at")]
            contents[table] = con.execute(
                f"SELECT {', '.join(columns)} FROM {table} ORDER BY rowid").fetchall()
    return contents


def test_same_file_on_an_empty_database_gives_the_same_database(workspace):
    """Decision 34: the same file always gives the same result."""
    workspace.run(BATCH2)
    first = database_contents(workspace.db)

    # Start again from an empty test.db and an empty log.
    workspace.db.unlink()
    workspace.log.unlink()

    workspace.run(BATCH2)
    second = database_contents(workspace.db)

    assert first["books"], "the first run should have loaded books"
    assert second == first
