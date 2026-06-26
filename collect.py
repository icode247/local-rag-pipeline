import json
from pathlib import Path

import requests

API_KEY = "4f36df7e-92c1-443f-a60e-09d2fba24dc7"
ZONE = "web_unlocker1"
BASE_URL = "https://api.brightdata.com/request"
RAW_DATA_PATH = "data/raw/pages.json"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

TARGETS = [
    "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
    "https://en.wikipedia.org/wiki/Vector_database",
    "https://en.wikipedia.org/wiki/Large_language_model",
]


def fetch_pages():
    results = []
    for url in TARGETS:
        print(f"Fetching: {url}")
        response = requests.post(
            BASE_URL,
            headers=HEADERS,
            json={
                "zone": ZONE,
                "url": url,
                "format": "raw",
                "data_format": "markdown",
            },
            timeout=60,
        )
        response.raise_for_status()
        brd_err = response.headers.get("x-brd-err-msg")
        if brd_err:
            raise RuntimeError(f"Bright Data error for {url}: {brd_err}")
        if not response.text.strip():
            raise RuntimeError(f"Empty response body for {url}")
        results.append({"url": url, "content": response.text})
        print(f"  -> {len(response.text)} chars")

    Path(RAW_DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_DATA_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} pages to {RAW_DATA_PATH}")


if __name__ == "__main__":
    fetch_pages()
