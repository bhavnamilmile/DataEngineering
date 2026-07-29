from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class City:
    rank: int
    name: str
    state: str
    population_2011: int
    latitude: float
    longitude: float
    sample_location_id: int


INDIA_TOP_CITIES: tuple[City, ...] = (
    City(1, "Mumbai", "Maharashtra", 12442373, 19.0760, 72.8777, 910001),
    City(2, "Delhi", "Delhi", 11034555, 28.6139, 77.2090, 910002),
    City(3, "Bengaluru", "Karnataka", 8443675, 12.9716, 77.5946, 910003),
    City(4, "Hyderabad", "Telangana", 6993262, 17.3850, 78.4867, 910004),
    City(5, "Ahmedabad", "Gujarat", 5577940, 23.0225, 72.5714, 910005),
    City(6, "Chennai", "Tamil Nadu", 4646732, 13.0827, 80.2707, 910006),
    City(7, "Kolkata", "West Bengal", 4496694, 22.5726, 88.3639, 910007),
    City(8, "Surat", "Gujarat", 4467797, 21.1702, 72.8311, 910008),
    City(9, "Pune", "Maharashtra", 3124458, 18.5204, 73.8567, 910009),
    City(10, "Jaipur", "Rajasthan", 3046163, 26.9124, 75.7873, 910010),
)


def sample_location_ids() -> tuple[int, ...]:
    return tuple(city.sample_location_id for city in INDIA_TOP_CITIES)


def city_by_sample_location_id(location_id: int) -> City | None:
    return next((city for city in INDIA_TOP_CITIES if city.sample_location_id == location_id), None)
