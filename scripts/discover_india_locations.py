#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.india_cities import INDIA_TOP_CITIES
from air_quality_pulse.openaq_client import OpenAQClient


def main() -> None:
    api_key = os.environ.get("OPENAQ_API_KEY")
    if not api_key:
        raise SystemExit("OPENAQ_API_KEY is required to discover live OpenAQ locations.")

    client = OpenAQClient(api_key=api_key)
    found_ids: list[int] = []
    print("Nearest OpenAQ monitor candidates for top Indian cities")
    print("------------------------------------------------------")
    for city in INDIA_TOP_CITIES:
        payload = client.get_locations(
            {
                "coordinates": f"{city.latitude},{city.longitude}",
                "radius": 25000,
                "iso": "IN",
                "monitor": "true",
                "limit": 10,
            }
        )
        results = payload.get("results", [])
        if not results:
            print(f"{city.rank}. {city.name}: no nearby monitor found")
            continue

        location = results[0]
        found_ids.append(location["id"])
        print(
            f"{city.rank}. {city.name}: {location['name']} "
            f"(OpenAQ location {location['id']})"
        )

    if found_ids:
        print()
        print("Run live comparison:")
        print(f"python3 scripts/run_air_quality_pipeline.py --location-ids {','.join(map(str, found_ids))}")


if __name__ == "__main__":
    main()
