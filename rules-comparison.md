# Rules comparison

This compares two week 3 `rules.md` files, decision by decision. It describes what each one says and where they differ. It doesn't judge which rules are better.

| | File | Version compared |
|---|---|---|
| **A** | [yuexinghu02/LoC-week3-assignment `rules.md`](https://github.com/yuexinghu02/LoC-week3-assignment/blob/assignment/rules.md) | commit `def15ca`, 31 Oct 2026 |
| **B** | [hhickerson-design/language-of-computation-week3-assignment `rules.md`](https://github.com/hhickerson-design/language-of-computation-week3-assignment/blob/assignment/rules.md) | commit `71c3758`, 1 Nov 2026 |

A is organized as Rules 1–13, then Decisions 1–33. B is organized as rules 1–16 with "Clarified" notes, then rules 17–24. References like "A Rule 8", "A D24" (Decision 24) or "B 9" point to those.

Each point gets one of four verdicts:

- **Agree:** both say the same thing, or lead to the same result.
- **Disagree:** both say something, and the results differ.
- **Only A** or **Only B:** only one file says anything. Where the other file's general rules still decide the case, the table says what they lead to.

## Summary

| Area | Agree | Disagree | Only A | Only B |
|---|---:|---:|---:|---:|
| ISBN problems | 18 | 9 | 5 | 0 |
| What makes two rows the same book | 1 | 4 | 1 | 0 |
| When a book arrives again | 3 | 4 | 2 | 0 |
| The log and the report | 4 | 1 | 6 | 2 |
| **Total** | **26** | **18** | **14** | **2** |

## 1. How each one handles every kind of ISBN problem

| Problem | A | B | Verdict |
|---|---|---|---|
| Storing ISBNs | Always text (Rule 1) | Always text (B 4) | Agree |
| Keeping the file's value | Keeps both columns, plus each one's original value and a status (Rule 8, D9) | Keeps both columns (B 5), plus the original whenever the stored value differs from the file (B 8) | Agree |
| Form of the stored value | Digits only: hyphens, spaces and labels removed (Rule 5, D7) | The printed form: hyphens and inner spaces are kept, spaces at the ends are trimmed. Rebuilt values are plain digits (B 6, 7, 9) | Disagree |
| ISBN-10 check digit | Must pass; the method (weights 10 to 1, divisible by 11) is written out (Rule 2) | Must be correct; no method given (B 1) | Agree |
| ISBN-13 check digit | Must pass; the method (weights 1 and 3, multiple of 10) is written out (Rule 3) | Must be correct; no method given (B 1) | Agree |
| ISBN-13 prefix | Must be `978` or `979` (Rule 3) | Must be `978` or `979` (B 1–3) | Agree |
| `9790…` numbers (ISMNs, for printed music) | Not an ISBN; moved to `other_id` (Rule 3, D12) | Not mentioned. They start with `979`, so B's rules accept them as ISBNs | Only A |
| Missing leading zeros (ISBN-10) | Added back only if the result passes the checksum (Rule 5) | Always added back; the check digit must then be correct (B 1, 7, 16). B doesn't say what's stored if the padded value fails | Agree |
| Hyphens and spaces | Removed from the stored value (Rule 5) | Ignored when checking and comparing, but kept in the stored value (B 6, 7) | Disagree |
| Lowercase `x` | Changed to `X` (Rule 5) | Capitalized (B 7) | Agree |
| An "ISBN", "ISBN-13" or "URN:ISBN:" label, or a format label like "(hardback)" | Removed; the value is repaired (D8) | A letter isn't allowed, so the value is unrecoverable and flagged (B 11) | Disagree |
| Five-digit price code after an ISBN | Rejected (D8) | Wrong number of digits, so flagged (B 11) | Agree |
| Wrong check digit | Rejected: cleaned value empty, original kept, "needs a lookup" (Rule 8) | Unrecoverable: loaded and flagged with the reason (B 11) | Agree |
| A letter in the middle, or the wrong number of digits | Rejected (Rule 6) | Unrecoverable and flagged (B 11) | Agree |
| An ISBN-13 in the ISBN-10 column | Moved to `isbn13`, and the ISBN-10 is calculated from it, with a warning (Rule 8) | Not mentioned. B 1 allows 10 or 13 digits without naming a column, so it's unclear whether this value is accepted or flagged | Only A |
| The ISBN-10 in the ISBN-13 column (like `195170342.0`) | Recognized; the ISBN-13 is calculated from the ISBN-10, with a warning (D11) | Not mentioned. A `.0` ending is unrecoverable (B 11), but B 9 rebuilds the ISBN-13 from a valid ISBN-10 anyway, so the stored value comes out the same | Only A |
| Rounded ISBN-13 (like `9.78043902348e+12`) with a valid ISBN-10 | Rebuilt from the ISBN-10, but only if the result rounds to the stored value; otherwise "needs a decision" (Rule 8, D10) | Always rebuilt from the ISBN-10 (B 9) | Agree |
| How the rounding works | 12 significant digits, with ties going to the even ten (D10) | Not mentioned | Only A |
| Rounded ISBN-13, no usable ISBN-10, and exactly one valid ISBN-13 fits | Filled in with status `inferred`, plus a warning (Rule 8, D5). 45 rows in `books.csv` | Left blank, original kept, flagged (B 10) | Disagree |
| Rounded ISBN-13, no usable ISBN-10, and two or no valid ISBN-13s fit | Rejected: empty, "needs a lookup" (Rule 8). 86 rows in `books.csv` | Left blank, flagged (B 10) | Agree |
| Valid ISBN-10 and a valid ISBN-13 that don't match | Keeps the ISBN-10, calculates the ISBN-13 from it, keeps the old ISBN-13 as the original, and flags "needs a decision" (Rule 8) | The ISBN-10 always rebuilds the ISBN-13 (B 9), and the old value is kept as the original (B 8). No flag is mentioned | Disagree |
| 13-digit codes that don't start with `978` or `979` (store IDs, barcodes) | Moved to `other_id`. If there's a valid ISBN-10, the ISBN-13 is calculated from it (D12) | Unrecoverable and flagged (B 11). There's no `other_id`; B 9 still rebuilds from a valid ISBN-10 | Disagree |
| UPC barcodes (11–12 digits, like `76783609419.0`) | Checked with the UPC checksum and moved to `other_id` (D11) | A `.0` ending or the wrong number of digits is unrecoverable and flagged (B 11) | Disagree |
| ISBN-13 cut short (like `97893806587.0`) | Rejected (D11) | Unrecoverable and flagged (B 11) | Agree |
| Empty ISBN-10 with a valid `978` ISBN-13 | ISBN-10 calculated (Rule 6) | ISBN-10 rebuilt (B 9) | Agree |
| Empty ISBN-13 with a valid ISBN-10 | ISBN-13 calculated (Rule 8) | ISBN-13 rebuilt (B 9) | Agree |
| Rejected ISBN-10 with a valid ISBN-13 | ISBN-10 calculated from the ISBN-13, with a warning (D13) | "No usable ISBN-10", so it's rebuilt from the ISBN-13 (B 9) | Agree |
| Calculating from an inferred value | Never (D14) | B has no inferred values | Only A |
| No usable ISBN at all | Stays empty with no warning: "missing isn't the same as wrong" (Rule 6, Rule 10). 565 rows in `books.csv` have neither ISBN | ISBNs are required: the book is loaded but flagged (B 12) | Disagree |
| How a problem is labeled | Each ISBN column gets a status (`ok`, `repaired`, `inferred`, `rejected`, `empty`), plus a summary for the row (D9) | A book is "flagged", with a reason (B 11) | Disagree |
| The same ISBN on two different books | Both books get a warning, checking the file and the database (Rule 7, D16) | Both books are flagged; ISBNs are compared by digits only (B 13, 14) | Agree |
| Checking the publisher and country parts of an ISBN | Not checked: "a valid checksum isn't proof" (Rule 7) | Only the prefix can be checked without the international registry (B 2–3) | Agree |

## 2. What makes two rows the same book

| Point | A | B | Verdict |
|---|---|---|---|
| The ID that identifies a book | `work_id`; if it's empty, then `goodreads_book_id`, then `book_id`, then the cleaned ISBN. The database makes its own key (Rule 9, D19, D21) | `book_id` (B 17) | Disagree |
| Does a shared ISBN make two rows the same book? | No: an ISBN identifies one edition and format, not the book (Rule 9) | No: two `book_id`s with the same ISBN are flagged as duplicates, not merged (B 13) | Agree |
| A row without a usable ID | Matched on the next ID. If nothing matches, it's added as a new book with a "needs a decision" warning (D19, D20) | Rejected if `book_id` is blank or not a whole number (B 19) | Disagree |
| Matching on title, author and year | Only flags a possible match; never merges (Rule 10) | Not mentioned | Only A |
| An exact duplicate row in the same file | Rejected: "exact duplicate of line N" (D2, D17) | The same `book_id` again in a file is treated like a book that already exists, so it's skipped (B 20) | Disagree |
| The same book twice in one file with different values | Every copy is rejected and goes under "needs a decision" (D18) | The second row is handled as the book arriving again: it can fill in a blank ISBN, or a different ISBN is flagged as a conflict (B 20) | Disagree |

## 3. When a book that's already loaded arrives again

| Point | A | B | Verdict |
|---|---|---|---|
| Nothing has changed | Skipped, already exists; the run still records that it saw the book (Rule 12, D26) | Skipped, already exists (B 20) | Agree |
| The incoming ISBN is blank | The stored ISBN is kept (Rule 12, D24) | The stored ISBN is kept (B 15) | Agree |
| The incoming row fills in a blank ISBN | Applied and counted as updated, with a warning (D24, D25) | Applied and counted as updated (B 20) | Agree |
| A different, non-blank ISBN | The new value replaces the stored one, it's flagged, and the history keeps the old one. Counted as updated (D24) | The stored value stays, it's flagged as a conflict, and the row counts as skipped (B 15, 20) | Disagree |
| Columns other than the ISBNs | Depends on the kind of column: IDs never change; titles and other descriptive columns are applied and flagged; rating counts take the newer value and are flagged if they go down (Rule 12, D22) | Never changed (B 20) | Disagree |
| `average_rating` and `work_ratings_count` | Recalculated from the star counts for every row, on every run (D23) | Loaded as given (B 18) and never changed (B 20) | Disagree |
| What counts as "updated" | Any stored value changed, including a recalculated one (D25) | Only filling in a blank ISBN (B 20) | Disagree |
| A history of changes | Every change is saved with its old value, new value, run and reason (Rule 12, D27) | Only the original values in the ISBN columns are kept (B 8) | Only A |
| Which file is newer | The one loaded later (D6) | Not needed, since non-ISBN columns never change | Only A |

The two sets of rules give different counts for loading `books-batch2.csv` after `books.csv`. A's numbers come from actually running A's script. B's come from reading B's rules, not from running any code.

| | Loaded | Updated | Skipped (already exist) | Rejected |
|---|---:|---:|---:|---:|
| A | 14 | 4 | 12 | 1 |
| B | 14 | 0 | 17 | 0 |

- **The 4 books with more ratings:** A updates them. B never changes ratings, so it skips them.
- **The duplicate copy of book 10001:** A rejects it. B skips it as already existing.

## 4. What the log and the report must say

| Point | A | B | Verdict |
|---|---|---|---|
| A log entry for every run, never overwriting earlier runs | Yes (D28) | Yes (B 23) | Agree |
| When it ran, which file, and how many rows were read, loaded, updated, skipped and rejected | Yes (Rule 13, D29) | Yes (B 23) | Agree |
| Every row that wasn't loaded, with its reason | Yes (D1, D30) | Yes (B 23) | Agree |
| Flagged rows | Grouped as "needs a decision", "needs a lookup" and "check this", each listed. Automatic repairs and skipped rows are only counted (D30) | Every flagged row is listed with its reason (B 23) | Disagree |
| `report.html` opens the log with a button | Yes, with a file picker, or by dragging the file onto the page (D31) | Yes (B 24) | Agree |
| Runs shown newest first | Not stated in `rules.md` | Yes (B 24) | Only B |
| One-line result for each run (loaded, loaded with warnings, or failed) | Yes (Rule 13) | Not mentioned | Only A |
| A check that the counts add up, and books before and after | Yes (Rule 13) | Not mentioned | Only A |
| ISBN status counts compared with the previous run | Yes (Rule 13, D3) | Not mentioned | Only A |
| What changed, with old and new values; assumptions; a CSV download of the problems | Yes (Rule 13, D3) | Not mentioned | Only A |
| Failed runs: when a run fails, it changes nothing and is still logged | Yes (D4, D28) | Not mentioned | Only A |
| Times in UTC, and a fingerprint of the file | Yes (D29) | Not mentioned | Only A |
| No AI or internet; the same file always gives the same result | Not stated. `rules.md` still lists "Should I look up ISBNs online?" as an open question. Rule 12 only says loading the same file twice changes nothing | Yes (B 21, 22) | Only B |
## 5. The examples tables

Only A has an examples table (30 examples). B's `rules.md` has none, so there's nothing from B to check against A's rules.

Below, each of A's 30 examples is run through B's rules by reading them, not by running B's code. "Flagged" means B loads the book and marks it with a reason.

| # | Column | Value | A's result | Under B's rules | Ends up differently? |
|---|---|---|---|---|---|
| 1 | `isbn` | `0439139600` | ok, `0439139600` | Valid, stored as is | No |
| 2 | `isbn` | `043965548X` | ok, `043965548X` | Valid, stored as is | No |
| 3 | `isbn` | `439023483` | repaired, `0439023483` | Zero added back: `0439023483` | No |
| 4 | `isbn` | `61120081` | repaired, `0061120081` | Zeros added back: `0061120081` | No |
| 5 | `isbn` | `0-450-19827-8` | repaired, `0450198278` | Valid; stored with hyphens: `0-450-19827-8` | **Yes:** different stored value |
| 6 | `isbn` | `␣162 001 4750␣` | repaired, `1620014750` | Valid; ends trimmed, inner spaces kept: `162 001 4750` | **Yes:** different stored value |
| 7 | `isbn` | `031200009x` | repaired, `031200009X` | Capitalized: `031200009X` | No |
| 8 | `isbn` | `9781982147600` | repaired: ISBN-10 `1982147601`, moved to `isbn13` | Unclear: B doesn't cover a value in the wrong column | **Unclear** |
| 9 | `isbn` | *(empty)*, with `isbn13` = `9780062398123` | repaired, `0062398121` | Rebuilt from the ISBN-13: `0062398121` | No |
| 10 | `isbn` | `1416524797` (*Paper Moons*) | ok, with a warning on both books | Valid; both books flagged as duplicates | No |
| 11 | `isbn` | `385535144` | rejected: empty, original kept | Zero added back; the check digit is wrong, so flagged | No (both mark it as a problem; B doesn't say which value is stored) |
| 12 | `isbn` | `04390A3483` | rejected | Flagged | No |
| 13 | `isbn` | `15287463097` | rejected | Flagged | No |
| 14 | `isbn13` | `9798351220413` | ok | Valid | No |
| 15 | `isbn13` | `9.78043902348e+12`, with `isbn` = `439023483` | repaired, `9780439023481` | Rebuilt from the ISBN-10: `9780439023481` | No |
| 16 | `isbn13` | `9.78067172365e+12`, no ISBN-10 | inferred, `9780671723651` | Rounded with nothing to rebuild from: blank, flagged | **Yes** |
| 17 | `isbn13` | `9.7804251888e+12`, no ISBN-10 | rejected: empty | Blank, flagged | No |
| 18 | `isbn13` | `9.78055381395e+12`, with `isbn` = `446612707` | repaired, `9780446612708`, "needs a decision" | Rebuilt from the ISBN-10: `9780446612708`, no flag | **Partly:** same value, but only A flags it |
| 19 | `isbn13` | `2.94001623192e+12` | rejected; moved to `other_id` | Rounded, nothing to rebuild from: blank, flagged; original kept | **Partly:** same empty `isbn13`, but only A fills `other_id` |
| 20 | `isbn13` | `76783609419.0`, with `isbn` = `553609416` | `9780553609417`; the UPC goes to `other_id` | Rebuilt from the ISBN-10: `9780553609417`; original kept | **Partly:** same `isbn13`, but only A fills `other_id` |
| 21 | `isbn13` | `97893806587.0` | rejected; the ISBN-10 is rejected too | `.0` ending is unrecoverable, and the ISBN-10's check digit is wrong; both flagged | No |
| 22 | both | *(empty)* | stays empty, no warning | ISBNs are required, so flagged | **Yes** |
| 23 | `isbn13` | `978-0-306-40615-7` | repaired, `9780306406157` | Valid; stored with hyphens: `978-0-306-40615-7` | **Yes:** different stored value |
| 24 | `isbn13` | `9780306406158` | rejected | Wrong check digit, flagged | No |
| 25 | `isbn` | `1234567890` | rejected | Wrong check digit, flagged | No |
| 26 | `isbn` | `ISBN 0-306-40615-2` | repaired, `0306406152` | Letters aren't allowed: flagged | **Yes** |
| 27 | `isbn13` | `URN:ISBN:978-92-95055-12-4` | repaired, `9789295055124` | Letters aren't allowed: flagged | **Yes** |
| 28 | `isbn13` | `ISBN 978-951-45-9693-3 (hardback)` | repaired, `9789514596933` | Letters aren't allowed: flagged | **Yes** |
| 29 | `isbn13` | `9790007672393` | not an ISBN; moved to `other_id` | Starts with `979` and the check digit is right: accepted as an ISBN | **Yes** |
| 30 | `isbn13` | `978-92-95055-12-4 90000` | rejected | Wrong number of digits, flagged | No |

**In total:**

- **No difference:** 16 examples (1–4, 7, 9–15, 17, 21, 24, 25, 30). Example 11 counts here because both mark the value as a problem, even though B doesn't say which value ends up stored.
- **Different:** 9 examples (5, 6, 16, 22, 23, 26–29).
- **Partly different:** 3 examples (18–20). The ISBN-13 ends up the same, but a flag or `other_id` differs.
- **Unclear:** 1 example (8), because B doesn't cover it.
