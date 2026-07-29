-- Task 02: Relational Modeling
-- Run with:
-- sqlite3 data/curated/air_quality_pulse.db < sql/task_02_relational_modeling_queries.sql

-- Tables created by this learning task.
select
    name
from sqlite_schema
where type = 'table'
    and name in (
        'dim_location',
        'dim_parameter',
        'dim_sensor',
        'fact_air_quality_measurement'
    )
order by name;

-- Relational mart row counts.
select 'dim_location' as table_name, count(*) as row_count from dim_location
union all
select 'dim_parameter', count(*) from dim_parameter
union all
select 'dim_sensor', count(*) from dim_sensor
union all
select 'fact_air_quality_measurement', count(*) from fact_air_quality_measurement;

-- Sample rows: use these to understand what each new table stores.
select
    location_id,
    location_name,
    country_code,
    provider_name,
    latitude,
    longitude
from dim_location
order by location_id
limit 3;

select
    parameter_key,
    parameter,
    parameter_display_name,
    unit
from dim_parameter
order by parameter_key;

select
    sensor_id,
    location_id,
    parameter_key
from dim_sensor
order by sensor_id
limit 4;

select
    measurement_key,
    location_id,
    sensor_id,
    parameter_key,
    measured_at_utc,
    value
from fact_air_quality_measurement
order by value desc
limit 4;

-- Dimension grain check: one row per monitoring location.
select
    location_id,
    location_name,
    provider_name,
    latitude,
    longitude
from dim_location
order by location_name;

-- Fact grain check: one row per sensor reading at a timestamp.
select
    fact.measurement_key,
    location.location_name,
    sensor.sensor_id,
    parameter.parameter,
    fact.measured_at_utc,
    fact.value
from fact_air_quality_measurement as fact
join dim_sensor as sensor
    on sensor.sensor_id = fact.sensor_id
join dim_location as location
    on location.location_id = sensor.location_id
join dim_parameter as parameter
    on parameter.parameter_key = sensor.parameter_key
order by fact.measured_at_utc desc, location.location_name, parameter.parameter;

-- Analytics query: latest facts joined to dimensions.
select
    location.location_name,
    location.country_code,
    parameter.parameter_display_name,
    parameter.unit,
    fact.value,
    fact.measured_at_utc
from fact_air_quality_measurement as fact
join dim_location as location
    on location.location_id = fact.location_id
join dim_parameter as parameter
    on parameter.parameter_key = fact.parameter_key
order by fact.value desc;

-- Query plan check: confirm SQLite can use the location/time index.
explain query plan
select
    fact.measured_at_utc,
    fact.value
from fact_air_quality_measurement as fact
where fact.location_id = 8118
order by fact.measured_at_utc desc;
