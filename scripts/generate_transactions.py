"""Generate the synthetic raw e-commerce file at data/raw/transactions.csv.

Every dirty value is injected on purpose, with a fixed seed, so the notebook
always finds the same grime. Run from the repository root:

    python scripts/generate_transactions.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 8245
CLEAN_ROWS = 490
DUPLICATE_ROWS = 10
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "transactions.csv"

FIRST_DATE = date(2025, 1, 1)
LAST_DATE = date(2025, 6, 30)
CUSTOMER_COUNT = 150

PRODUCTS = {
    "Wireless Mouse": 24.99,
    "Mechanical Keyboard": 89.99,
    "USB-C Hub": 39.99,
    "27in Monitor": 249.99,
    "Laptop Stand": 34.99,
    "Noise-Cancelling Headphones": 199.99,
    "1080p Webcam": 59.99,
    "LED Desk Lamp": 29.99,
}

CITY_WEIGHTS = {
    "New York": 14,
    "Los Angeles": 11,
    "Chicago": 9,
    "Houston": 7,
    "Phoenix": 5,
    "Philadelphia": 6,
    "San Diego": 5,
    "Dallas": 6,
    "Austin": 7,
    "Seattle": 8,
    "Denver": 6,
    "Boston": 7,
    "Miami": 4,
    "Atlanta": 5,
    "Portland": 6,
}

COUPON_WEIGHTS = {"": 55, "SAVE10": 15, "SAVE15": 10, "SAVE20": 6, "WELCOME5": 8, "FREESHIP": 6}
QUANTITY_WEIGHTS = {1: 55, 2: 25, 3: 12, 4: 5, 5: 3}

FIELDNAMES = ["order_id", "date", "customer_id", "product", "price", "quantity", "coupon_code", "shipping_city"]


def weighted_choice(rng: random.Random, weights: dict) -> object:
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def make_clean_rows(rng: random.Random) -> list[dict]:
    day_span = (LAST_DATE - FIRST_DATE).days
    dates = sorted(FIRST_DATE + timedelta(days=rng.randint(0, day_span)) for _ in range(CLEAN_ROWS))
    rows = []
    for number, order_date in enumerate(dates, start=10001):
        product = rng.choice(list(PRODUCTS))
        rows.append({
            "order_id": f"ORD-{number}",
            "date": order_date.isoformat(),
            "customer_id": f"C{rng.randint(1, CUSTOMER_COUNT):04d}",
            "product": product,
            "price": f"{PRODUCTS[product]:.2f}",
            "quantity": str(weighted_choice(rng, QUANTITY_WEIGHTS)),
            "coupon_code": weighted_choice(rng, COUPON_WEIGHTS),
            "shipping_city": weighted_choice(rng, CITY_WEIGHTS),
        })
    return rows


def take(pool: list[int], count: int) -> list[int]:
    """Remove and return the first `count` indices, so groups sharing a pool never overlap."""
    taken = pool[:count]
    del pool[:count]
    return taken


def shuffled_indices(rng: random.Random, rows: list[dict], condition=lambda row: True) -> list[int]:
    indices = [i for i, row in enumerate(rows) if condition(row)]
    rng.shuffle(indices)
    return indices


def inject_grime(rng: random.Random, rows: list[dict]) -> None:
    for i in shuffled_indices(rng, rows)[:60]:
        city = rows[i]["shipping_city"]
        rows[i]["shipping_city"] = rng.choice([city.lower(), city.upper(), f"  {city}", f"{city} "])

    price_pool = shuffled_indices(rng, rows)
    for i in take(price_pool, 20):
        rows[i]["price"] = f"${rows[i]['price']}"
    for i in take(price_pool, 6):
        rows[i]["price"] = f"-{rows[i]['price']}"

    for i in shuffled_indices(rng, rows)[:12]:
        rows[i]["customer_id"] = ""

    quantity_pool = shuffled_indices(rng, rows)
    for i in take(quantity_pool, 8):
        rows[i]["quantity"] = ""
    for i in take(quantity_pool, 3):
        rows[i]["quantity"] = "999"

    for i in shuffled_indices(rng, rows)[:40]:
        rows[i]["date"] = date.fromisoformat(rows[i]["date"]).strftime("%m/%d/%Y")

    for i in shuffled_indices(rng, rows, lambda row: row["coupon_code"] != "")[:25]:
        code = rows[i]["coupon_code"]
        rows[i]["coupon_code"] = rng.choice([code.lower(), f" {code}", f"{code} ", code.title()])
    for i in shuffled_indices(rng, rows, lambda row: row["coupon_code"] == "")[:15]:
        rows[i]["coupon_code"] = rng.choice(["N/A", "none", "NULL"])


def add_duplicates(rng: random.Random, rows: list[dict]) -> list[dict]:
    """Insert exact copies right after their originals, like a double-submitted order."""
    originals = set(rng.sample(range(len(rows)), DUPLICATE_ROWS))
    result = []
    for i, row in enumerate(rows):
        result.append(row)
        if i in originals:
            result.append(dict(row))
    return result


def main() -> None:
    rng = random.Random(SEED)
    rows = make_clean_rows(rng)
    inject_grime(rng, rows)
    rows = add_duplicates(rng, rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
