import json
import sys
import time

import requests

ES = "http://localhost:9200"
INDEX = "movies"


def main():
    # create index with mapping
    mapping_path = "data/movies.mapping.json"
    bulk_path = "data/movies.bulk.ndjson"

    # delete old
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

    # refresh
    requests.post(f"{ES}/{INDEX}/_refresh")
    print("Refreshed")


if __name__ == "__main__":
    main()
