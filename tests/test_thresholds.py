from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.thresholds import classify_measurement


class ThresholdTests(unittest.TestCase):
    def test_pm25_classifies_sample_as_unsafe(self) -> None:
        result = classify_measurement("pm25", "ug/m3", 42.1)

        self.assertEqual(result["risk_level"], "Unsafe")
        self.assertEqual(result["category"], "Unhealthy for Sensitive Groups")

    def test_o3_ppm_classifies_sample_as_safe(self) -> None:
        result = classify_measurement("o3", "ppm", 0.031)

        self.assertEqual(result["risk_level"], "Safe")
        self.assertEqual(result["category"], "Good")

    def test_no2_ppm_is_converted_to_ppb(self) -> None:
        result = classify_measurement("no2", "ppm", 0.075)

        self.assertEqual(result["risk_level"], "Caution")
        self.assertEqual(result["threshold_unit"], "ppb")


if __name__ == "__main__":
    unittest.main()
