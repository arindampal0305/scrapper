from pathlib import Path
from urllib.parse import urljoin
import time

import requests
from bs4 import BeautifulSoup

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = Path("cache")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (https://github.com/arindampal0305/scrapper)"
}


def fetch_page(url, cache_file):
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        content = cache_file.read_text(encoding="utf-8")
        return content, True

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
    catalogue_pages = 0

    while current_url and catalogue_pages < 3:
        page_number = catalogue_pages + 1
        cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

        content, cache_hit = fetch_page(current_url, cache_file)

        if not cache_hit and catalogue_pages > 0:
            time.sleep(0.5)

        soup = BeautifulSoup(content, "html.parser")

        for article in soup.select("article.product_pod"):
            link = article.select_one("h3 a")

            if link and link.get("href"):
                absolute_url = urljoin(current_url, link["href"])
                all_links.append(absolute_url)

        catalogue_pages += 1

        next_link = soup.select_one("li.next a")

        if next_link and next_link.get("href") and catalogue_pages < 3:
            current_url = urljoin(current_url, next_link["href"])

            if not cache_hit:
                time.sleep(0.5)
        else:
            current_url = None

    unique_links = list(dict.fromkeys(all_links))

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_links)}")
    print(f"unique_urls={len(unique_links)}")

    return unique_links


if __name__ == "__main__":
    discover_books()