-- Highest latest pollutant readings by location and parameter.
select
    location_name,
    parameter,
    unit,
    avg(value) as avg_value,
    max(value) as max_value,
    count(*) as reading_count
from air_quality_measurements
group by location_name, parameter, unit
order by max_value desc;

-- Rows that need review before downstream analytics.
select
    measurement_key,
    location_name,
    parameter,
    value,
    measured_at_utc,
    quality_issues
from air_quality_measurements
where quality_issues <> '';

-- Recent pipeline runs.
select
    started_at_utc,
    finished_at_utc,
    row_count,
    invalid_row_count,
    status
from pipeline_runs
order by run_id desc;

-- Relational mart: latest facts joined to location and pollutant dimensions.
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

-- Query plan check: confirm SQLite can use mart indexes for common filters.
explain query plan
select
    fact.measured_at_utc,
    fact.value
from fact_air_quality_measurement as fact
where fact.location_id = 8118
order by fact.measured_at_utc desc;
