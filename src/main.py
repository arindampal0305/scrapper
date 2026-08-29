from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime, timezone
import json
import re
import time

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError


START_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = Path("cache")
OUTPUT_DIR = Path("output")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (https://github.com/arindampal0305/scrapper)"
}


class Book(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: str
    fetched_at: str


def fetch_page(url, cache_file):
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8"), True

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed: HTTP {response.status_code}")

    content = response.text
    cache_file.write_text(content, encoding="utf-8")

    return content, False


def discover_books():
    current_url = START_URL
    all_links = []
    source_pages = {}
    catalogue_pages = 0

    while current_url and catalogue_pages < 3:
        page_number = catalogue_pages + 1
        cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

        content, cache_hit = fetch_page(current_url, cache_file)

        soup = BeautifulSoup(content, "html.parser")

        for article in soup.select("article.product_pod"):
            link = article.select_one("h3 a")

            if link and link.get("href"):
                absolute_url = urljoin(current_url, link["href"])
                all_links.append(absolute_url)
                source_pages[absolute_url] = current_url

        catalogue_pages += 1

        next_link = soup.select_one("li.next a")

        if next_link and next_link.get("href") and catalogue_pages < 3:
            current_url = urljoin(current_url, next_link["href"])

            if not cache_hit:
                time.sleep(0.5)
        else:
            current_url = None

    unique_links = list(dict.fromkeys(all_links))

    return unique_links, source_pages


def normalize_price(price_text):
    cleaned = price_text.replace("£", "").replace("Â", "").strip()
    match = re.search(r"\d+(?:\.\d+)?", cleaned)

    if not match:
        raise ValueError(f"Invalid price: {price_text}")

    return float(match.group())


def extract_book(url, source_page, index):
    cache_file = CACHE_DIR / f"book-{index}.html"

    content, cache_hit = fetch_page(url, cache_file)

    if not cache_hit:
        time.sleep(0.5)

    soup = BeautifulSoup(content, "html.parser")

    product_main = soup.select_one("article.product_page")

    title_element = product_main.select_one("h1") if product_main else None
    price_element = product_main.select_one(".price_color") if product_main else None
    availability_element = product_main.select_one(".availability") if product_main else None
    rating_element = product_main.select_one(".star-rating") if product_main else None
    description_element = soup.select_one("#product_description + p")

    title = title_element.get_text(strip=True) if title_element else None
    price_text = price_element.get_text(strip=True) if price_element else None

    availability_text = (
        availability_element.get_text(" ", strip=True)
        if availability_element
        else None
    )

    rating_text = None

    if rating_element:
        classes = rating_element.get("class", [])
        rating_classes = [item for item in classes if item != "star-rating"]
        rating_text = rating_classes[0] if rating_classes else None

    description = (
        description_element.get_text(" ", strip=True)
        if description_element
        else None
    )

    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "price_gbp": normalize_price(price_text),
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    links, source_pages = discover_books()

    valid_records = []
    errors = []
    seen_urls = set()

    for index, url in enumerate(links, start=1):
        if url in seen_urls:
            continue

        seen_urls.add(url)

        try:
            raw_record = extract_book(
                url,
                source_pages[url],
                index
            )

            book = Book.model_validate(raw_record)
            valid_records.append(book.model_dump())

        except (ValidationError, ValueError, RuntimeError) as e:
            errors.append({
                "product_url": url,
                "reason": str(e)
            })

    books_file = OUTPUT_DIR / "books.json"
    errors_file = OUTPUT_DIR / "errors.json"

    books_file.write_text(
        json.dumps(valid_records, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    errors_file.write_text(
        json.dumps(errors, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")

    if valid_records:
        print(json.dumps(valid_records[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()