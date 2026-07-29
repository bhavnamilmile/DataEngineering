from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.pipeline import PipelineConfig, run_pipeline


class PipelineTests(unittest.TestCase):
    def test_sample_pipeline_loads_multiple_locations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database_path = temp_path / "air_quality.db"
            result = run_pipeline(
                PipelineConfig(
                    location_ids=(8118, 999001),
                    database_path=database_path,
                    raw_dir=temp_path / "raw",
                    sample=True,
                    sample_dir=ROOT / "data/sample",
                )
            )

            self.assertEqual(result["row_count"], 4)
            self.assertEqual(result["invalid_row_count"], 0)

            with sqlite3.connect(database_path) as connection:
                location_count = connection.execute(
                    "select count(distinct location_id) from air_quality_measurements"
                ).fetchone()[0]

            self.assertEqual(location_count, 2)


if __name__ == "__main__":
    unittest.main()
