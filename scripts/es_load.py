# scripts/es_load.py
import json
import os
import time

import requests

ES = os.getenv("ELASTIC_URL", "http://localhost:9200").rstrip("/")
INDEX = os.getenv("ES_INDEX", "movies")


def wait_es(url: str, timeout: int = 60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            r.raise_for_status()
            return
        except requests.RequestException:
            time.sleep(1)
    raise RuntimeError(f"Elasticsearch not ready at {url}")


def main():
    mapping_path = "data/movies.mapping.json"
    bulk_path = "data/movies.bulk.ndjson"

    wait_es(ES)  # дождаться подъёма

    requests.delete(f"{ES}/{INDEX}")

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    r = requests.put(f"{ES}/{INDEX}", json=mapping)
    r.raise_for_status()
    print("Index created:", r.json())

    with open(bulk_path, "rb") as f:
        r = requests.post(
            f"{ES}/_bulk", data=f, headers={"Content-Type": "application/x-ndjson"}
        )
    r.raise_for_status()
    print("Bulk loaded")

    requests.post(f"{ES}/{INDEX}/_refresh")
    print("Refreshed")


if __name__ == "__main__":
    main()
