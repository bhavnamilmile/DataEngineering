# Data Engineering Projects

This workspace contains hands-on data engineering learning projects.

## Air Quality Pulse

Air Quality Pulse is a local beginner pipeline for public OpenAQ air-quality data.

It does four things:

- extracts a location and its latest measurements from OpenAQ
- saves the raw API responses for debugging and replay
- cleans and validates measurement records
- loads analytics-ready rows into a local SQLite database
- rebuilds a small relational analytics mart with dimensions, facts, constraints, and indexes

OpenAQ v3 uses API keys. Create one in OpenAQ Explorer, then set it locally:

```bash
cp .env.example .env
export OPENAQ_API_KEY="your-key"
```

Run with live data:

```bash
python3 scripts/run_air_quality_pipeline.py --location-id 8118
```

Run with multiple live locations:

```bash
python3 scripts/run_air_quality_pipeline.py --location-ids 8118,12345,67890
```

Run with the included sample data:

```bash
python3 scripts/run_air_quality_pipeline.py --sample
```

Run with multiple sample locations:

```bash
python3 scripts/run_air_quality_pipeline.py --sample --location-ids 8118,999001
```

Run the built-in top Indian city comparison sample:

```bash
python3 scripts/run_air_quality_pipeline.py --sample --india-top-cities
```

Find nearby live OpenAQ monitor IDs for the top Indian cities:

```bash
python3 scripts/discover_india_locations.py
```

Query the local database:

```bash
python3 scripts/query_air_quality.py
```

Inspect the relational model:

```bash
sqlite3 data/curated/air_quality_pulse.db ".tables"
sqlite3 data/curated/air_quality_pulse.db ".schema dim_location"
sqlite3 data/curated/air_quality_pulse.db < sql/air_quality_analysis.sql
```

Open the dashboard:

```bash
pip install -r requirements.txt
streamlit run app/air_quality_dashboard.py
```

Outputs:

- raw responses: `data/raw/`
- local database: `data/curated/air_quality_pulse.db`
- curated landing table: `air_quality_measurements`
- relational mart tables: `dim_location`, `dim_parameter`, `dim_sensor`, `fact_air_quality_measurement`

Learning home:

- [Browser Learning Home](docs/index.html)
- GitHub Pages URL after publish: <https://bhavnamilmile.github.io/DataEngineering/>

GitHub Pages is published from the `gh-pages` branch. If GitHub asks for a Pages source,
choose **Deploy from a branch**, then select `gh-pages` and `/ (root)`.

Learning visuals:

- [Browser-friendly Streamlit-style Visual Guide](docs/air-quality-pulse-visual-guide.html)
- [Markdown Visual Guide](docs/air-quality-pulse-visual-guide.md)

Learning tasks:

- Task 01: local foundations and batch ingestion, documented in [Learning Notes](docs/learning-notes-and-industry-tools.md)
- [Task 02: Relational Modeling Visual Guide](docs/tasks/02-relational-modeling.html)
- [Task 02: Relational Modeling Markdown](docs/tasks/02-relational-modeling.md)

Task-specific code is kept separate where it helps trace the learning:

- relational mart module: `src/air_quality_pulse/relational_mart.py`
- relational modeling queries: `sql/task_02_relational_modeling_queries.sql`
- relational modeling tests: `tests/task_02/test_relational_mart.py`

Dashboard views:

- latest readings chart
- side-by-side location comparison by pollutant
- monitoring location map
- green-to-red safety legend used by charts and map points
- short pollutant guide with common health effects
- quality issue review
- nominal EPA/AirNow risk thresholds for `pm25`, `pm10`, `o3`, `co`, `so2`, and `no2`
- pipeline run history

Threshold labels are meant to help interpret latest readings:

- Safe: Good
- Caution: Moderate
- Unsafe: Unhealthy for Sensitive Groups or Unhealthy
- High Risk: Very Unhealthy or Hazardous

Official AQI calculations use pollutant-specific averaging periods, so these labels are dashboard context rather than a full regulatory AQI calculation.

References:

- [OpenAQ API documentation](https://docs.openaq.org/)
- [OpenAQ API key quick start](https://docs.openaq.org/using-the-api/quick-start)
- [OpenAQ API overview](https://docs.openaq.org/about/about)
- [AirNow AQI basics](https://www.airnow.gov/aqi/aqi-basics)
- [EPA particulate matter health effects](https://www.epa.gov/pm-pollution/health-and-environmental-effects-particulate-matter-pm)
- [EPA ozone health effects](https://www.epa.gov/ground-level-ozone-pollution/health-effects-ozone-pollution)
- [EPA nitrogen dioxide basics](https://www.epa.gov/no2-pollution/basic-information-about-no2)
