from __future__ import annotations

from typing import Any

from air_quality_pulse.india_cities import city_by_sample_location_id


SAMPLE_READINGS = {
    "Mumbai": {"pm25": 24.8, "o3": 0.038},
    "Delhi": {"pm25": 86.2, "o3": 0.064},
    "Bengaluru": {"pm25": 18.4, "o3": 0.041},
    "Hyderabad": {"pm25": 31.6, "o3": 0.052},
    "Ahmedabad": {"pm25": 44.9, "o3": 0.073},
    "Chennai": {"pm25": 16.2, "o3": 0.035},
    "Kolkata": {"pm25": 57.7, "o3": 0.048},
    "Surat": {"pm25": 28.5, "o3": 0.057},
    "Pune": {"pm25": 20.1, "o3": 0.044},
    "Jaipur": {"pm25": 63.4, "o3": 0.069},
}


def sample_payloads_for_location(location_id: int) -> tuple[dict[str, Any], dict[str, Any]] | None:
    city = city_by_sample_location_id(location_id)
    if city is None:
        return None

    pm25_sensor_id = location_id * 10 + 1
    o3_sensor_id = location_id * 10 + 2
    readings = SAMPLE_READINGS[city.name]

    location_payload = {
        "meta": {"name": "openaq-api", "website": "/", "page": 1, "limit": 100, "found": 1},
        "results": [
            {
                "id": location_id,
                "name": city.name,
                "locality": city.state,
                "timezone": "Asia/Kolkata",
                "country": {"id": 9, "code": "IN", "name": "India"},
                "owner": {"id": 910, "name": "Sample Data"},
                "provider": {"id": 910, "name": "Sample Provider"},
                "isMobile": False,
                "isMonitor": True,
                "sensors": [
                    {
                        "id": pm25_sensor_id,
                        "name": "pm25 ug/m3",
                        "parameter": {
                            "id": 2,
                            "name": "pm25",
                            "units": "ug/m3",
                            "displayName": "PM2.5",
                        },
                    },
                    {
                        "id": o3_sensor_id,
                        "name": "o3 ppm",
                        "parameter": {
                            "id": 10,
                            "name": "o3",
                            "units": "ppm",
                            "displayName": "Ozone",
                        },
                    },
                ],
                "coordinates": {"latitude": city.latitude, "longitude": city.longitude},
            }
        ],
    }
    latest_payload = {
        "meta": {"name": "openaq-api", "website": "/", "page": 1, "limit": 100, "found": 2},
        "results": [
            {
                "datetime": {
                    "utc": "2026-07-29T14:00:00Z",
                    "local": "2026-07-29T19:30:00+05:30",
                },
                "value": readings["pm25"],
                "coordinates": {"latitude": city.latitude, "longitude": city.longitude},
                "sensorsId": pm25_sensor_id,
                "locationsId": location_id,
            },
            {
                "datetime": {
                    "utc": "2026-07-29T14:00:00Z",
                    "local": "2026-07-29T19:30:00+05:30",
                },
                "value": readings["o3"],
                "coordinates": {"latitude": city.latitude, "longitude": city.longitude},
                "sensorsId": o3_sensor_id,
                "locationsId": location_id,
            },
        ],
    }
    return location_payload, latest_payload
