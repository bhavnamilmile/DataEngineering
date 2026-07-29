#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query Air Quality Pulse results.")
    parser.add_argument("--database", type=Path, default=Path("data/curated/air_quality_pulse.db"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.database.exists():
        raise SystemExit(f"Database not found: {args.database}. Run the pipeline first.")

    with sqlite3.connect(args.database) as connection:
        connection.row_factory = sqlite3.Row
        print("Highest latest readings")
        print("-----------------------")
        for row in connection.execute(
            """
            select
                location_name,
                parameter,
                unit,
                value,
                measured_at_utc,
                quality_issues
            from air_quality_measurements
            order by value desc
            limit 10
            """
        ):
            issue_text = row["quality_issues"] or "ok"
            print(
                f"{row['location_name']} | {row['parameter']} | "
                f"{row['value']} {row['unit']} | {row['measured_at_utc']} | {issue_text}"
            )

        print()
        print("Relational mart: latest facts joined to dimensions")
        print("--------------------------------------------------")
        for row in connection.execute(
            """
            select
                location.location_name,
                parameter.parameter_display_name,
                parameter.unit,
                fact.value,
                fact.measured_at_utc
            from fact_air_quality_measurement as fact
            join dim_location as location
                on location.location_id = fact.location_id
            join dim_parameter as parameter
                on parameter.parameter_key = fact.parameter_key
            order by fact.value desc
            limit 10
            """
        ):
            print(
                f"{row['location_name']} | {row['parameter_display_name']} | "
                f"{row['value']} {row['unit']} | {row['measured_at_utc']}"
            )

        print()
        print("Pipeline runs")
        print("-------------")
        for row in connection.execute(
            """
            select started_at_utc, row_count, invalid_row_count, status
            from pipeline_runs
            order by run_id desc
            limit 5
            """
        ):
            print(
                f"{row['started_at_utc']} | rows={row['row_count']} | "
                f"issues={row['invalid_row_count']} | {row['status']}"
            )


if __name__ == "__main__":
    main()
