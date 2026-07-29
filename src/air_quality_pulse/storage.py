from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


MEASUREMENT_COLUMNS = [
    "measurement_key",
    "location_id",
    "location_name",
    "locality",
    "country_code",
    "country_name",
    "provider_name",
    "owner_name",
    "sensor_id",
    "parameter",
    "parameter_display_name",
    "unit",
    "value",
    "measured_at_utc",
    "measured_at_local",
    "latitude",
    "longitude",
    "source_url",
    "ingested_at_utc",
    "quality_issues",
]


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("pragma foreign_keys = on")
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        create table if not exists air_quality_measurements (
            measurement_key text primary key,
            location_id integer,
            location_name text,
            locality text,
            country_code text,
            country_name text,
            provider_name text,
            owner_name text,
            sensor_id integer,
            parameter text,
            parameter_display_name text,
            unit text,
            value real,
            measured_at_utc text,
            measured_at_local text,
            latitude real,
            longitude real,
            source_url text,
            ingested_at_utc text,
            quality_issues text
        );

        create table if not exists pipeline_runs (
            run_id integer primary key autoincrement,
            started_at_utc text not null,
            finished_at_utc text not null,
            source_url text not null,
            raw_location_path text not null,
            raw_latest_path text not null,
            row_count integer not null,
            invalid_row_count integer not null,
            status text not null
        );
        """
    )
    connection.commit()


def upsert_measurements(connection: sqlite3.Connection, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    placeholders = ", ".join(["?"] * len(MEASUREMENT_COLUMNS))
    assignments = ", ".join(
        f"{column}=excluded.{column}"
        for column in MEASUREMENT_COLUMNS
        if column != "measurement_key"
    )
    sql = f"""
        insert into air_quality_measurements ({", ".join(MEASUREMENT_COLUMNS)})
        values ({placeholders})
        on conflict(measurement_key) do update set {assignments}
    """
    values = [[row.get(column) for column in MEASUREMENT_COLUMNS] for row in rows]
    connection.executemany(sql, values)
    connection.commit()
    return len(rows)


def record_pipeline_run(
    connection: sqlite3.Connection,
    *,
    started_at_utc: str,
    finished_at_utc: str,
    source_url: str,
    raw_location_path: Path,
    raw_latest_path: Path,
    row_count: int,
    invalid_row_count: int,
    status: str,
) -> None:
    connection.execute(
        """
        insert into pipeline_runs (
            started_at_utc,
            finished_at_utc,
            source_url,
            raw_location_path,
            raw_latest_path,
            row_count,
            invalid_row_count,
            status
        )
        values (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            started_at_utc,
            finished_at_utc,
            source_url,
            str(raw_location_path),
            str(raw_latest_path),
            row_count,
            invalid_row_count,
            status,
        ),
    )
    connection.commit()
