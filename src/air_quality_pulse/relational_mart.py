from __future__ import annotations

import sqlite3


MART_SCHEMA_SQL = """
create table if not exists dim_location (
    location_id integer primary key,
    location_name text not null,
    locality text,
    country_code text,
    country_name text,
    provider_name text,
    owner_name text,
    latitude real,
    longitude real,
    updated_at_utc text not null
);

create table if not exists dim_parameter (
    parameter_key text primary key,
    parameter text not null,
    parameter_display_name text,
    unit text not null,
    updated_at_utc text not null
);

create table if not exists dim_sensor (
    sensor_id integer primary key,
    location_id integer not null references dim_location(location_id),
    parameter_key text not null references dim_parameter(parameter_key),
    updated_at_utc text not null
);

create table if not exists fact_air_quality_measurement (
    measurement_key text primary key
        references air_quality_measurements(measurement_key),
    location_id integer not null references dim_location(location_id),
    sensor_id integer not null references dim_sensor(sensor_id),
    parameter_key text not null references dim_parameter(parameter_key),
    measured_at_utc text not null,
    measured_at_local text,
    value real not null,
    source_url text,
    ingested_at_utc text not null,
    quality_issues text not null default ''
);

create index if not exists idx_measurements_location_parameter_time
    on air_quality_measurements(location_id, parameter, measured_at_utc);
create index if not exists idx_fact_air_quality_location_time
    on fact_air_quality_measurement(location_id, measured_at_utc);
create index if not exists idx_fact_air_quality_parameter_time
    on fact_air_quality_measurement(parameter_key, measured_at_utc);
"""


MART_REFRESH_SQL = """
delete from fact_air_quality_measurement;
delete from dim_sensor;
delete from dim_parameter;
delete from dim_location;

insert into dim_location (
    location_id,
    location_name,
    locality,
    country_code,
    country_name,
    provider_name,
    owner_name,
    latitude,
    longitude,
    updated_at_utc
)
select
    location_id,
    coalesce(location_name, 'Unknown location') as location_name,
    max(locality) as locality,
    max(country_code) as country_code,
    max(country_name) as country_name,
    max(provider_name) as provider_name,
    max(owner_name) as owner_name,
    max(latitude) as latitude,
    max(longitude) as longitude,
    max(ingested_at_utc) as updated_at_utc
from air_quality_measurements
where location_id is not null
group by location_id, coalesce(location_name, 'Unknown location');

insert into dim_parameter (
    parameter_key,
    parameter,
    parameter_display_name,
    unit,
    updated_at_utc
)
select
    parameter || '|' || unit as parameter_key,
    parameter,
    max(parameter_display_name) as parameter_display_name,
    unit,
    max(ingested_at_utc) as updated_at_utc
from air_quality_measurements
where parameter is not null
    and unit is not null
group by parameter, unit;

insert into dim_sensor (
    sensor_id,
    location_id,
    parameter_key,
    updated_at_utc
)
select
    sensor_id,
    location_id,
    parameter || '|' || unit as parameter_key,
    max(ingested_at_utc) as updated_at_utc
from air_quality_measurements
where sensor_id is not null
    and location_id is not null
    and parameter is not null
    and unit is not null
group by sensor_id, location_id, parameter, unit;

insert into fact_air_quality_measurement (
    measurement_key,
    location_id,
    sensor_id,
    parameter_key,
    measured_at_utc,
    measured_at_local,
    value,
    source_url,
    ingested_at_utc,
    quality_issues
)
select
    measurement_key,
    location_id,
    sensor_id,
    parameter || '|' || unit as parameter_key,
    measured_at_utc,
    measured_at_local,
    value,
    source_url,
    ingested_at_utc,
    coalesce(quality_issues, '') as quality_issues
from air_quality_measurements
where measurement_key is not null
    and location_id is not null
    and sensor_id is not null
    and parameter is not null
    and unit is not null
    and measured_at_utc is not null
    and value is not null;
"""


def initialize_relational_mart(connection: sqlite3.Connection) -> None:
    connection.executescript(MART_SCHEMA_SQL)
    connection.commit()


def refresh_relational_mart(connection: sqlite3.Connection) -> dict[str, int]:
    """Rebuild analytics dimensions and facts from the curated landing table."""
    initialize_relational_mart(connection)
    connection.executescript(MART_REFRESH_SQL)
    connection.commit()
    return {
        "location_count": _table_count(connection, "dim_location"),
        "parameter_count": _table_count(connection, "dim_parameter"),
        "sensor_count": _table_count(connection, "dim_sensor"),
        "fact_count": _table_count(connection, "fact_air_quality_measurement"),
    }


def _table_count(connection: sqlite3.Connection, table_name: str) -> int:
    return int(connection.execute(f"select count(*) from {table_name}").fetchone()[0])
