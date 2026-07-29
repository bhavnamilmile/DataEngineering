#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.pipeline import PipelineConfig, run_pipeline
from air_quality_pulse.india_cities import sample_location_ids


def parse_location_ids(values: list[str] | None) -> tuple[int, ...]:
    if not values:
        return (8118,)

    location_ids: list[int] = []
    for value in values:
        for part in value.split(","):
            part = part.strip()
            if part:
                location_ids.append(int(part))
    return tuple(dict.fromkeys(location_ids))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Air Quality Pulse pipeline.")
    parser.add_argument(
        "--location-id",
        action="append",
        dest="location_ids",
        help="OpenAQ location ID. Repeat it or pass comma-separated IDs.",
    )
    parser.add_argument(
        "--location-ids",
        action="append",
        dest="location_ids",
        help="Comma-separated OpenAQ location IDs.",
    )
    parser.add_argument("--database", type=Path, default=Path("data/curated/air_quality_pulse.db"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--sample", action="store_true", help="Use included sample data instead of OpenAQ.")
    parser.add_argument(
        "--india-top-cities",
        action="store_true",
        help="Load the built-in top Indian city sample locations.",
    )
    parser.add_argument("--latest-limit", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    location_ids = sample_location_ids() if args.india_top_cities else parse_location_ids(args.location_ids)
    result = run_pipeline(
        PipelineConfig(
            location_ids=location_ids,
            database_path=args.database,
            raw_dir=args.raw_dir,
            sample=args.sample,
            latest_limit=args.latest_limit,
        )
    )
    print("Air Quality Pulse pipeline complete")
    print(f"Locations loaded: {', '.join(str(location_id) for location_id in location_ids)}")
    print(f"Rows loaded: {result['row_count']}")
    print(f"Rows with quality issues: {result['invalid_row_count']}")
    mart_counts = result["mart_counts"]
    print(
        "Relational mart: "
        f"{mart_counts['location_count']} locations, "
        f"{mart_counts['parameter_count']} parameters, "
        f"{mart_counts['sensor_count']} sensors, "
        f"{mart_counts['fact_count']} facts"
    )
    print(f"Database: {result['database_path']}")
    for raw_path in result["raw_paths"]:
        print(f"Raw location file: {raw_path['raw_location_path']}")
        print(f"Raw latest file: {raw_path['raw_latest_path']}")


if __name__ == "__main__":
    main()
