from __future__ import annotations

import json
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.transform import build_measurement_rows, validate_row


class TransformTests(unittest.TestCase):
    def test_build_measurement_rows_enriches_latest_measurements(self) -> None:
        location = json.loads((ROOT / "data/sample/openaq_location_8118.json").read_text())
        latest = json.loads((ROOT / "data/sample/openaq_latest_8118.json").read_text())

        rows = build_measurement_rows(
            location,
            latest,
            source_url="https://api.openaq.org/v3/locations/8118/latest",
            ingested_at_utc=datetime(2026, 7, 29, 14, 5, tzinfo=UTC),
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["measurement_key"], "8118:23534:2026-07-29T14:00:00Z")
        self.assertEqual(rows[0]["location_name"], "New Delhi")
        self.assertEqual(rows[0]["parameter"], "pm25")
        self.assertEqual(rows[0]["unit"], "ug/m3")
        self.assertEqual(rows[0]["quality_issues"], "")

    def test_validate_row_flags_bad_values(self) -> None:
        issues = validate_row(
            {
                "measurement_key": None,
                "measured_at_utc": None,
                "parameter": None,
                "value": "bad",
                "latitude": 200,
                "longitude": -200,
            }
        )

        self.assertIn("missing_measurement_key", issues)
        self.assertIn("missing_measured_at_utc", issues)
        self.assertIn("missing_parameter", issues)
        self.assertIn("non_numeric_value", issues)
        self.assertIn("invalid_latitude", issues)
        self.assertIn("invalid_longitude", issues)


if __name__ == "__main__":
    unittest.main()
