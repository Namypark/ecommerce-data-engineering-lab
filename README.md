# E-commerce Data Engineering Lab

This project takes 50,000 sales orders through the 12-step data engineering road-map, from loading the raw CSV to a cleaned, enriched dataset saved as CSV and JSON.
The raw file contains realistic grime: `$` prices, negative prices, blank units and regions, two date formats, impossible ship dates, inconsistent country, product, channel and priority spellings, untrustworthy stored totals, and duplicate orders.
Each order is modelled as a `SalesOrder` class with `clean()`, `revenue()` and `profit()` methods, then enriched with GDP and ISO codes from a public world-GDP dataset. Country names that differ between the two sources are reconciled with an explicit alias table.
Every order kept after cleaning is checked against the untouched source file and matches it exactly.
The notebook ends with profit per item type and an insight about revenue versus profit, followed by a data dictionary merged from both sources.

## Quick start

```bash
uv sync
uv run jupyter notebook ecommerce_data_engineering.ipynb
```

Or with pip:

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook ecommerce_data_engineering.ipynb
```

Then choose **Run → Run All Cells**. The notebook writes its outputs to `data/processed/`.
It has been tested top-to-bottom with Python 3.13 + pandas 3.0.

## Repository layout

```
ecommerce_data_engineering.ipynb   the 12-step notebook (the deliverable)
data/raw/                          input files, never modified by the notebook
data/processed/                    cleaned CSV + gzipped JSON written by Step 11
scripts/add_grime.py               rebuilds data/raw/sales_records_dirty.csv from the source file
requirements.txt
```

## Data sources

- **Primary: `data/raw/sales_records_50k_source.csv`** (50,000 rows). The ["50000 Sales Records"](https://excelbianalytics.com/wp/downloads-18-sample-csv-files-data-sets-for-testing-sales/) sample file from ExcelBIAnalytics: region, country, item type, sales channel, priority, order and ship dates, units, unit price and cost, and totals. It is kept exactly as downloaded.
- **Primary, dirty copy: `data/raw/sales_records_dirty.csv`** (50,250 rows). The source file is almost clean (its only natural grime is trailing spaces in 1,973 country names), so [`scripts/add_grime.py`](scripts/add_grime.py) adds realistic problems with a fixed seed (`8245`). This is the file the notebook cleans. To regenerate it, run `python scripts/add_grime.py`.
- **Secondary: `data/raw/world_gdp_2014.csv`** (222 rows). [2014 world GDP with codes](https://github.com/plotly/datasets/blob/master/2014_world_gdp_with_codes.csv) from Plotly's open `datasets` repository: country, GDP in billions of USD, and ISO alpha-3 code.

## Other projects

- https://github.com/Namypark/anomaly-detection-lab
- https://github.com/Namypark/DATASTREAMVISUALIZATION-GROUP4
- https://github.com/Namypark/Machine-Learning-programming
