# The Polite Scraper

A small Python scraping pipeline that collects 60 books from the first three catalogue pages of Books to Scrape, cleans and validates the data, and survives a broken page without crashing.

## Target Classification

The target is Books to Scrape, a public sandbox created for practising web scraping.

The scraper collects only the first 3 catalogue pages and the 60 book pages linked from them.

The collected data includes book title, product URL, price, availability, rating, description, source page, and fetch time.

I will not reuse this code on another site without checking its rules and terms first.

## Robots.txt Result

404 Not Found — no robots file found.

## How to Run

### Lane

Python

### Install

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### Run

```powershell
python src/main.py
```

The scraper produces:

```text
output/books.json
output/errors.json
output/run-report.json
```

## Record Schema

Each validated book record contains:

```json
{
  "title": "string",
  "product_url": "https://...",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "string or null",
  "source_page": "https://...",
  "fetched_at": "ISO-8601 timestamp"
}
```

Records are validated with Pydantic before being stored.

## Politeness Rules

The scraper:

- Sends an identifying User-Agent.
- Uses a request timeout.
- Waits at least 500 ms between real requests.
- Uses cached HTML during development.
- Checks HTTP status codes before parsing.
- Retries server errors once.
- Does not retry 404 or 403 responses.
- Collects only the data required for the assignment.

## Run Report Evidence

A test run with one deliberately broken URL produced:

```json
{
  "start_time": "2026-08-29T21:13:51.475926+00:00",
  "duration_seconds": 1.727522,
  "pages_fetched": 0,
  "cache_hits": 3,
  "valid_records": 60,
  "invalid_records": 1,
  "failed_pages": 1
}
```

The broken URL was skipped while all 60 valid book records survived.

## Why No Browser Was Needed

The required book data is already present in the HTML returned by the server, so a browser would only add unnecessary cost.

## Ethics Note

I will use an official API when one exists. I will never bypass logins, paywalls, or blocks, and I will collect only the data I need.

## Limitation

The scraper depends on the current HTML structure and CSS selectors of Books to Scrape. If the site's page structure changes, the selectors may need to be updated.