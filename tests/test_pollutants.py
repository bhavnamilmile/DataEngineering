from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.pollutants import pollutant_description, pollutant_description_rows


class PollutantDescriptionTests(unittest.TestCase):
    def test_known_pollutant_has_short_description(self) -> None:
        description = pollutant_description("pm25")

        self.assertEqual(description["name"], "PM2.5")
        self.assertIn("lungs", description["what_it_is"])
        self.assertIn("heart", description["effects"])

    def test_rows_follow_selected_parameters(self) -> None:
        rows = pollutant_description_rows(("pm25", "o3"))

        self.assertEqual([row["parameter"] for row in rows], ["pm25", "o3"])
        self.assertEqual(rows[1]["name"], "Ozone")


if __name__ == "__main__":
    unittest.main()
