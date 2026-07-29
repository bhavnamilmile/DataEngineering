from __future__ import annotations

from typing import Any


POLLUTANT_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "pm25": {
        "name": "PM2.5",
        "what_it_is": "Fine particles small enough to travel deep into the lungs.",
        "effects": "Can worsen asthma and breathing symptoms and is linked with heart and lung problems.",
        "watch_for": "Higher risk for children, older adults, and people with heart or lung disease.",
    },
    "pm10": {
        "name": "PM10",
        "what_it_is": "Inhalable particles such as dust, smoke, and larger airborne particles.",
        "effects": "Can irritate airways, cause coughing, and worsen existing respiratory conditions.",
        "watch_for": "Outdoor dust, smoke, construction, and road pollution can raise levels.",
    },
    "o3": {
        "name": "Ozone",
        "what_it_is": "Ground-level ozone, a gas formed when other pollutants react in sunlight.",
        "effects": "Can cause coughing, wheezing, shortness of breath, and worsen asthma or bronchitis.",
        "watch_for": "Often worse on hot, sunny afternoons.",
    },
    "co": {
        "name": "Carbon monoxide",
        "what_it_is": "A colorless gas from combustion sources such as vehicles and fuel burning.",
        "effects": "Reduces the blood's ability to carry oxygen; high exposure can be dangerous.",
        "watch_for": "Headache, dizziness, exhaustion, and flu-like symptoms can occur at elevated exposure.",
    },
    "so2": {
        "name": "Sulfur dioxide",
        "what_it_is": "A gas mainly from burning sulfur-containing fuels and some industrial sources.",
        "effects": "Can irritate airways and make breathing harder, especially for people with asthma.",
        "watch_for": "Can also contribute to particle pollution and haze.",
    },
    "no2": {
        "name": "Nitrogen dioxide",
        "what_it_is": "A traffic- and combustion-related gas that is part of nitrogen oxides.",
        "effects": "Can irritate airways and aggravate asthma and other respiratory diseases.",
        "watch_for": "Often elevated near busy roads and combustion sources.",
    },
}


def pollutant_description(parameter: Any) -> dict[str, str]:
    key = str(parameter or "").lower().replace(".", "").replace("_", "").strip()
    return POLLUTANT_DESCRIPTIONS.get(
        key,
        {
            "name": str(parameter or "Unknown"),
            "what_it_is": "No short description is available yet.",
            "effects": "No health-effect summary is available yet.",
            "watch_for": "Check the source documentation for this pollutant.",
        },
    )


def pollutant_description_rows(parameters: list[str] | tuple[str, ...]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for parameter in parameters:
        description = pollutant_description(parameter)
        rows.append(
            {
                "parameter": parameter,
                "name": description["name"],
                "what_it_is": description["what_it_is"],
                "effects": description["effects"],
                "watch_for": description["watch_for"],
            }
        )
    return rows
