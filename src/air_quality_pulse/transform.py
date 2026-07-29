from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_measurement_rows(
    location_payload: dict[str, Any],
    latest_payload: dict[str, Any],
    source_url: str,
    ingested_at_utc: datetime | None = None,
) -> list[dict[str, Any]]:
    ingested_at_utc = ingested_at_utc or datetime.now(UTC)
    location = _first_result(location_payload, "location")
    sensors = _sensor_lookup(location)

    rows: list[dict[str, Any]] = []
    for measurement in latest_payload.get("results", []):
        if not isinstance(measurement, dict):
            continue

        sensor_id = measurement.get("sensorsId")
        sensor = sensors.get(sensor_id, {})
        parameter = sensor.get("parameter", {}) if isinstance(sensor, dict) else {}
        coordinates = measurement.get("coordinates") or {}
        measured_at = measurement.get("datetime") or {}

        row = {
            "measurement_key": _measurement_key(measurement),
            "location_id": measurement.get("locationsId") or location.get("id"),
            "location_name": location.get("name"),
            "locality": location.get("locality"),
            "country_code": _nested(location, "country", "code"),
            "country_name": _nested(location, "country", "name"),
            "provider_name": _nested(location, "provider", "name"),
            "owner_name": _nested(location, "owner", "name"),
            "sensor_id": sensor_id,
            "parameter": parameter.get("name"),
            "parameter_display_name": parameter.get("displayName"),
            "unit": parameter.get("units"),
            "value": measurement.get("value"),
            "measured_at_utc": measured_at.get("utc"),
            "measured_at_local": measured_at.get("local"),
            "latitude": coordinates.get("latitude"),
            "longitude": coordinates.get("longitude"),
            "source_url": source_url,
            "ingested_at_utc": ingested_at_utc.isoformat(),
        }
        row["quality_issues"] = ",".join(validate_row(row))
        rows.append(row)

    return rows


def validate_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not row.get("measurement_key"):
        issues.append("missing_measurement_key")
    if not row.get("measured_at_utc"):
        issues.append("missing_measured_at_utc")
    if not row.get("parameter"):
        issues.append("missing_parameter")
    if row.get("value") is None:
        issues.append("missing_value")
    if not _is_number(row.get("value")):
        issues.append("non_numeric_value")
    if not _in_range(row.get("latitude"), -90, 90):
        issues.append("invalid_latitude")
    if not _in_range(row.get("longitude"), -180, 180):
        issues.append("invalid_longitude")
    return issues


def _first_result(payload: dict[str, Any], label: str) -> dict[str, Any]:
    results = payload.get("results", [])
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        raise ValueError(f"Missing {label} result in API payload")
    return results[0]


def _sensor_lookup(location: dict[str, Any]) -> dict[int, dict[str, Any]]:
    sensors = location.get("sensors", [])
    if not isinstance(sensors, list):
        return {}
    return {sensor["id"]: sensor for sensor in sensors if isinstance(sensor, dict) and "id" in sensor}


def _measurement_key(measurement: dict[str, Any]) -> str | None:
    location_id = measurement.get("locationsId")
    sensor_id = measurement.get("sensorsId")
    measured_at = (measurement.get("datetime") or {}).get("utc")
    if not location_id or not sensor_id or not measured_at:
        return None
    return f"{location_id}:{sensor_id}:{measured_at}"


def _nested(source: dict[str, Any], parent: str, child: str) -> Any:
    value = source.get(parent)
    return value.get(child) if isinstance(value, dict) else None


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _in_range(value: Any, low: float, high: float) -> bool:
    return _is_number(value) and low <= value <= high
