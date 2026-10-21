# Data

Local data artifacts for development live here.

- `downloads/` holds raw source files fetched from SEC EDGAR, grouped by year.
- `download.py` fetches the corpus and writes `downloads/manifest.json`.
- Downloaded payloads are gitignored because the corpus can get large.
- Fetch a sample corpus with `uv run data/download.py` (edit `TICKERS` /
  `FILINGS_PER_COMPANY` / `USER_AGENT` at the top of the script first).
