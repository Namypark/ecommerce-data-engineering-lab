"""Build data/raw/sales_records_dirty.csv from the 50,000-row sales source file.

The source file (ExcelBIAnalytics "50000 Sales Records") is almost clean: its only
natural problem is trailing spaces in some country names. Real order exports are
messier, so this script injects realistic grime into a copy, with a fixed seed, so
the notebook always finds the same problems. The source file is never modified.
Run from the repository root:

    python scripts/add_grime.py
"""

import csv
import random
from datetime import datetime
from pathlib import Path

SEED = 8245
DUPLICATE_ROWS = 250
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
SOURCE_PATH = RAW_DIR / "sales_records_50k_source.csv"
OUTPUT_PATH = RAW_DIR / "sales_records_dirty.csv"

SOURCE_DATE_FORMAT = "%m/%d/%Y"
PRIORITY_WORDS = {"C": "Critical", "H": "High", "M": "Medium", "L": "Low"}


def take(pool: list[int], count: int) -> list[int]:
    """Remove and return the first `count` indices, so groups sharing a pool never overlap."""
    taken = pool[:count]
    del pool[:count]
    return taken


def shuffled_indices(rng: random.Random, rows: list[dict]) -> list[int]:
    indices = list(range(len(rows)))
    rng.shuffle(indices)
    return indices


def respell(rng: random.Random, value: str) -> str:
    """Same value, typed differently: other case or stray spaces."""
    return rng.choice([value.lower(), value.upper(), f"  {value}", f"{value.lower()} "])


def to_iso(value: str) -> str:
    return datetime.strptime(value, SOURCE_DATE_FORMAT).strftime("%Y-%m-%d")


def inject_grime(rng: random.Random, rows: list[dict]) -> None:
    for i in shuffled_indices(rng, rows)[:1200]:
        rows[i]["Country"] = respell(rng, rows[i]["Country"].strip())
    for i in shuffled_indices(rng, rows)[:600]:
        rows[i]["Item Type"] = respell(rng, rows[i]["Item Type"])
    for i in shuffled_indices(rng, rows)[:800]:
        rows[i]["Sales Channel"] = respell(rng, rows[i]["Sales Channel"])
    for i in shuffled_indices(rng, rows)[:700]:
        code = rows[i]["Order Priority"]
        rows[i]["Order Priority"] = rng.choice([PRIORITY_WORDS[code], PRIORITY_WORDS[code].lower(), code.lower()])

    for i in shuffled_indices(rng, rows)[:150]:
        rows[i]["Region"] = ""

    price_pool = shuffled_indices(rng, rows)
    for i in take(price_pool, 900):
        rows[i]["Unit Price"] = f"${rows[i]['Unit Price']}"
    for i in take(price_pool, 40):
        rows[i]["Unit Price"] = f"-{rows[i]['Unit Price']}"

    units_pool = shuffled_indices(rng, rows)
    for i in take(units_pool, 120):
        rows[i]["Units Sold"] = ""
    for i in take(units_pool, 25):
        rows[i]["Units Sold"] = "99999"

    revenue_pool = shuffled_indices(rng, rows)
    for i in take(revenue_pool, 100):
        rows[i]["Total Revenue"] = ""
    for i in take(revenue_pool, 60):
        rows[i]["Total Revenue"] = f"{float(rows[i]['Total Revenue']) * 10:.2f}"

    date_pool = shuffled_indices(rng, rows)
    for i in take(date_pool, 2500):
        rows[i]["Order Date"] = to_iso(rows[i]["Order Date"])
        rows[i]["Ship Date"] = to_iso(rows[i]["Ship Date"])
    for i in take(date_pool, 60):
        rows[i]["Order Date"], rows[i]["Ship Date"] = rows[i]["Ship Date"], rows[i]["Order Date"]


def add_duplicates(rng: random.Random, rows: list[dict]) -> list[dict]:
    """Insert exact copies right after their originals, like an order exported twice."""
    originals = set(rng.sample(range(len(rows)), DUPLICATE_ROWS))
    result = []
    for i, row in enumerate(rows):
        result.append(row)
        if i in originals:
            result.append(dict(row))
    return result


def main() -> None:
    with SOURCE_PATH.open(newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        rows = list(reader)

    rng = random.Random(SEED)
    inject_grime(rng, rows)
    rows = add_duplicates(rng, rows)

    with OUTPUT_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
