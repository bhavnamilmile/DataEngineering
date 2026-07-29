from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from air_quality_pulse.openaq_client import OpenAQClient
from air_quality_pulse.sample_data import sample_payloads_for_location
from air_quality_pulse.storage import (
    connect,
    initialize_database,
    record_pipeline_run,
    upsert_measurements,
)
from air_quality_pulse.relational_mart import refresh_relational_mart
from air_quality_pulse.transform import build_measurement_rows


@dataclass(frozen=True)
class PipelineConfig:
    location_ids: tuple[int, ...] = (8118,)
    database_path: Path = Path("data/curated/air_quality_pulse.db")
    raw_dir: Path = Path("data/raw")
    sample: bool = False
    sample_dir: Path = Path("data/sample")
    latest_limit: int = 100


def run_pipeline(config: PipelineConfig) -> dict[str, Any]:
    started_at = datetime.now(UTC)
    all_rows: list[dict[str, Any]] = []
    raw_paths: list[dict[str, str]] = []

    with connect(config.database_path) as connection:
        initialize_database(connection)

        for location_id in config.location_ids:
            source_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
            location_payload, latest_payload = _load_payloads(config, location_id)
            raw_location_path = _write_raw_json(
                config.raw_dir,
                f"openaq_location_{location_id}",
                location_payload,
                started_at,
            )
            raw_latest_path = _write_raw_json(
                config.raw_dir,
                f"openaq_latest_{location_id}",
                latest_payload,
                started_at,
            )

            rows = build_measurement_rows(
                location_payload,
                latest_payload,
                source_url=source_url,
                ingested_at_utc=started_at,
            )
            loaded_count = upsert_measurements(connection, rows)
            invalid_row_count = sum(1 for row in rows if row.get("quality_issues"))
            finished_at = datetime.now(UTC)
            record_pipeline_run(
                connection,
                started_at_utc=started_at.isoformat(),
                finished_at_utc=finished_at.isoformat(),
                source_url=source_url,
                raw_location_path=raw_location_path,
                raw_latest_path=raw_latest_path,
                row_count=loaded_count,
                invalid_row_count=invalid_row_count,
                status="success",
            )
            all_rows.extend(rows)
            raw_paths.append(
                {
                    "location_id": str(location_id),
                    "raw_location_path": str(raw_location_path),
                    "raw_latest_path": str(raw_latest_path),
                }
            )

        mart_counts = refresh_relational_mart(connection)

    return {
        "database_path": str(config.database_path),
        "raw_paths": raw_paths,
        "row_count": len(all_rows),
        "invalid_row_count": sum(1 for row in all_rows if row.get("quality_issues")),
        "mart_counts": mart_counts,
        "sample": config.sample,
    }


def _load_payloads(config: PipelineConfig, location_id: int) -> tuple[dict[str, Any], dict[str, Any]]:
    if config.sample:
        generated_payloads = sample_payloads_for_location(location_id)
        if generated_payloads:
            return generated_payloads

        location_path = config.sample_dir / f"openaq_location_{location_id}.json"
        latest_path = config.sample_dir / f"openaq_latest_{location_id}.json"
        if not location_path.exists() or not latest_path.exists():
            raise FileNotFoundError(f"No sample payloads found for location {location_id}")
        return (_read_json(location_path), _read_json(latest_path))

    api_key = os.environ.get("OPENAQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAQ_API_KEY is required for live OpenAQ requests. "
            "Use --sample to run the local sample pipeline."
        )

    client = OpenAQClient(api_key=api_key)
    return (
        client.get_location(location_id),
        client.get_latest_measurements(location_id, limit=config.latest_limit),
    )


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object-shaped JSON in {path}")
    return payload


def _write_raw_json(raw_dir: Path, prefix: str, payload: dict[str, Any], run_time: datetime) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    timestamp = run_time.strftime("%Y%m%dT%H%M%SZ")
    path = raw_dir / f"{prefix}_{timestamp}.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        file.write("\n")
    return path
