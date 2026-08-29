from pathlib import Path
import requests

URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_FILE = Path("cache/catalogue-page-1.html")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (https://github.com/arindampal0305/scrapper)"
}


def fetch_page():
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists():
        content = CACHE_FILE.read_text(encoding="utf-8")
        print(f"CACHE HIT size={len(content)}")
        return content

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=10
    )

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed: HTTP {response.status_code}")

    content = response.text
    CACHE_FILE.write_text(content, encoding="utf-8")

    print(f"FETCH size={len(content)}")
    return content


if __name__ == "__main__":
    fetch_page()