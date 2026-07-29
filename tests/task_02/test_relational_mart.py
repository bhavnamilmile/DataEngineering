from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.pipeline import PipelineConfig, run_pipeline


class RelationalMartTests(unittest.TestCase):
    def test_sample_pipeline_builds_joinable_dimensions_and_fact(self) -> None:
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

            self.assertEqual(
                result["mart_counts"],
                {
                    "location_count": 2,
                    "parameter_count": 2,
                    "sensor_count": 4,
                    "fact_count": 4,
                },
            )

            with sqlite3.connect(database_path) as connection:
                connection.row_factory = sqlite3.Row
                rows = connection.execute(
                    """
                    select
                        location.location_name,
                        parameter.parameter_display_name,
                        parameter.unit,
                        fact.value
                    from fact_air_quality_measurement as fact
                    join dim_location as location
                        on location.location_id = fact.location_id
                    join dim_parameter as parameter
                        on parameter.parameter_key = fact.parameter_key
                    order by fact.value desc
                    """
                ).fetchall()

            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["location_name"], "New Delhi")
            self.assertEqual(rows[0]["parameter_display_name"], "PM2.5")
            self.assertEqual(rows[0]["unit"], "ug/m3")

    def test_relational_mart_refresh_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database_path = temp_path / "air_quality.db"
            config = PipelineConfig(
                location_ids=(8118,),
                database_path=database_path,
                raw_dir=temp_path / "raw",
                sample=True,
                sample_dir=ROOT / "data/sample",
            )

            first_result = run_pipeline(config)
            second_result = run_pipeline(config)

            self.assertEqual(first_result["mart_counts"], second_result["mart_counts"])
            self.assertEqual(second_result["mart_counts"]["fact_count"], 2)


if __name__ == "__main__":
    unittest.main()
