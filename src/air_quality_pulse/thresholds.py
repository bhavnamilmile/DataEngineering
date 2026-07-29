from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Breakpoint:
    label: str
    risk_level: str
    low: float
    high: float
    color: str


AQI_COLORS = {
    "green": "#00e400",
    "yellow": "#ffff00",
    "orange": "#ff7e00",
    "red": "#ff0000",
    "purple": "#8f3f97",
    "maroon": "#7e0023",
    "gray": "#8a8a8a",
}

RISK_COLOR_DOMAIN = [
    "Safe",
    "Caution",
    "Unsafe",
    "High Risk",
    "Unknown",
]

RISK_COLOR_RANGE = [
    "#00e400",
    "#ffff00",
    "#ff7e00",
    "#ff0000",
    "#8a8a8a",
]


BREAKPOINTS: dict[str, list[Breakpoint]] = {
    "pm25": [
        Breakpoint("Good", "Safe", 0.0, 9.0, "green"),
        Breakpoint("Moderate", "Caution", 9.1, 35.4, "yellow"),
        Breakpoint("Unhealthy for Sensitive Groups", "Unsafe", 35.5, 55.4, "orange"),
        Breakpoint("Unhealthy", "Unsafe", 55.5, 125.4, "red"),
        Breakpoint("Very Unhealthy", "High Risk", 125.5, 225.4, "purple"),
        Breakpoint("Hazardous", "High Risk", 225.5, 325.4, "maroon"),
    ],
    "pm10": [
        Breakpoint("Good", "Safe", 0.0, 54.0, "green"),
        Breakpoint("Moderate", "Caution", 55.0, 154.0, "yellow"),
        Breakpoint("Unhealthy for Sensitive Groups", "Unsafe", 155.0, 254.0, "orange"),
        Breakpoint("Unhealthy", "Unsafe", 255.0, 354.0, "red"),
        Breakpoint("Very Unhealthy", "High Risk", 355.0, 424.0, "purple"),
        Breakpoint("Hazardous", "High Risk", 425.0, 604.0, "maroon"),
    ],
    "o3": [
        Breakpoint("Good", "Safe", 0.0, 0.054, "green"),
        Breakpoint("Moderate", "Caution", 0.055, 0.070, "yellow"),
        Breakpoint("Unhealthy for Sensitive Groups", "Unsafe", 0.071, 0.085, "orange"),
        Breakpoint("Unhealthy", "Unsafe", 0.086, 0.105, "red"),
        Breakpoint("Very Unhealthy", "High Risk", 0.106, 0.200, "purple"),
    ],
    "co": [
        Breakpoint("Good", "Safe", 0.0, 4.4, "green"),
        Breakpoint("Moderate", "Caution", 4.5, 9.4, "yellow"),
        Breakpoint("Unhealthy for Sensitive Groups", "Unsafe", 9.5, 12.4, "orange"),
        Breakpoint("Unhealthy", "Unsafe", 12.5, 15.4, "red"),
        Breakpoint("Very Unhealthy", "High Risk", 15.5, 30.4, "purple"),
        Breakpoint("Hazardous", "High Risk", 30.5, 50.4, "maroon"),
    ],
    "so2": [
        Breakpoint("Good", "Safe", 0.0, 35.0, "green"),
        Breakpoint("Moderate", "Caution", 36.0, 75.0, "yellow"),
        Breakpoint("Unhealthy for Sensitive Groups", "Unsafe", 76.0, 185.0, "orange"),
        Breakpoint("Unhealthy", "Unsafe", 186.0, 304.0, "red"),
        Breakpoint("Very Unhealthy", "High Risk", 305.0, 604.0, "purple"),
        Breakpoint("Hazardous", "High Risk", 605.0, 1004.0, "maroon"),
    ],
    "no2": [
        Breakpoint("Good", "Safe", 0.0, 53.0, "green"),
        Breakpoint("Moderate", "Caution", 54.0, 100.0, "yellow"),
        Breakpoint("Unhealthy for Sensitive Groups", "Unsafe", 101.0, 360.0, "orange"),
        Breakpoint("Unhealthy", "Unsafe", 361.0, 649.0, "red"),
        Breakpoint("Very Unhealthy", "High Risk", 650.0, 1249.0, "purple"),
        Breakpoint("Hazardous", "High Risk", 1250.0, 2049.0, "maroon"),
    ],
}


def classify_measurement(parameter: Any, unit: Any, value: Any) -> dict[str, Any]:
    parameter_key = _normalize_parameter(parameter)
    value_float = _to_float(value)
    canonical_value = _canonical_value(parameter_key, unit, value_float)

    if parameter_key not in BREAKPOINTS or canonical_value is None:
        return _unknown(parameter_key, value_float)

    for breakpoint in BREAKPOINTS[parameter_key]:
        if breakpoint.low <= canonical_value <= breakpoint.high:
            return {
                "category": breakpoint.label,
                "risk_level": breakpoint.risk_level,
                "threshold_low": breakpoint.low,
                "threshold_high": breakpoint.high,
                "threshold_unit": _canonical_unit(parameter_key),
                "threshold_color": breakpoint.color,
                "risk_color": _risk_color(breakpoint.risk_level),
                "aqi_color": AQI_COLORS[breakpoint.color],
            }

    highest = BREAKPOINTS[parameter_key][-1]
    return {
        "category": f"Above {highest.label}",
        "risk_level": "High Risk",
        "threshold_low": highest.high,
        "threshold_high": None,
        "threshold_unit": _canonical_unit(parameter_key),
        "threshold_color": "maroon",
        "risk_color": _risk_color("High Risk"),
        "aqi_color": AQI_COLORS["maroon"],
    }


def threshold_table() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for parameter, breakpoints in BREAKPOINTS.items():
        for breakpoint in breakpoints:
            rows.append(
                {
                    "parameter": parameter,
                    "risk_level": breakpoint.risk_level,
                    "category": breakpoint.label,
                    "low": breakpoint.low,
                    "high": breakpoint.high,
                    "unit": _canonical_unit(parameter),
                }
            )
    return rows


def _normalize_parameter(parameter: Any) -> str:
    return str(parameter or "").lower().replace(".", "").replace("_", "").strip()


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _canonical_value(parameter: str, unit: Any, value: float | None) -> float | None:
    if value is None:
        return None

    unit_key = str(unit or "").lower().replace("μ", "u").replace("µ", "u").strip()
    if parameter in {"so2", "no2"} and unit_key == "ppm":
        return value * 1000
    if parameter == "o3" and unit_key == "ppb":
        return value / 1000
    return value


def _canonical_unit(parameter: str) -> str:
    return {
        "pm25": "ug/m3",
        "pm10": "ug/m3",
        "o3": "ppm",
        "co": "ppm",
        "so2": "ppb",
        "no2": "ppb",
    }.get(parameter, "")


def _unknown(parameter: str, value: float | None) -> dict[str, Any]:
    return {
        "category": "Not classified",
        "risk_level": "Unknown",
        "threshold_low": None,
        "threshold_high": None,
        "threshold_unit": _canonical_unit(parameter),
        "threshold_color": "gray",
        "risk_color": _risk_color("Unknown"),
        "aqi_color": AQI_COLORS["gray"],
    }


def _risk_color(risk_level: str) -> str:
    return {
        "Safe": "#00e400",
        "Caution": "#ffff00",
        "Unsafe": "#ff7e00",
        "High Risk": "#ff0000",
        "Unknown": "#8a8a8a",
    }.get(risk_level, "#8a8a8a")
