# Week 4 Assignment

This is my Module 4 assignment for MSAI-5523.

## Running the tests

The tests in `test_ingest.py` check that `ingest.py` does what `rules.md` says. They need Python 3 and pytest.

Open a terminal (PowerShell, Command Prompt or Git Bash) and go to this folder:

```
cd ~/workspace/language-of-computation/week4-assignment
```

In Command Prompt, use `cd %USERPROFILE%\workspace\language-of-computation\week4-assignment` instead.

Install pytest. You only need to do this once:

```
python -m pip install --user pytest
```

Run the tests:

```
python -m pytest
```

All 34 tests should pass. Each test uses its own `test.db` and `test-log.json` in a temporary folder and deletes them afterwards. The tests never touch `books.db` or `ingestion-log.json` in this folder.

## Running ingest.py

From the same folder, load `books.csv`:

```
python ingest.py books.csv
```

Load `books.csv` again. No books are added a second time, so all 10,000 rows are skipped:

```
python ingest.py books.csv
```

Load `books-batch2.csv`:

```
python ingest.py books-batch2.csv
```

The first run creates `books.db` and `ingestion-log.json` in this folder, and each run adds an entry to the log. To see the results, open `report.html` in a browser, click **Open ingestion-log.json** and choose the log.

If `python` isn't recognized, or opens the Microsoft Store, use `py` instead of `python` in every command above.
