# Air Quality Pulse Visual Guide

<div style="border:1px solid #e6e9ef;border-radius:10px;padding:22px 24px;background:#ffffff;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
  <div style="font-size:13px;font-weight:700;color:#ff4b4b;text-transform:uppercase;letter-spacing:.04em;">Learning Project</div>
  <h2 style="margin:6px 0 8px 0;">Air Quality Pulse</h2>
  <p style="margin:0;color:#4b5563;font-size:15px;line-height:1.5;">
    A local data engineering pipeline that ingests public air-quality readings, preserves raw responses,
    creates curated analytics tables, validates rows, and visualizes city-level pollutant risk.
  </p>
</div>

<br>

<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;">
  <div style="border:1px solid #e6e9ef;border-radius:10px;padding:14px;background:#fff;">
    <div style="font-size:12px;color:#6b7280;font-weight:700;">FLOW</div>
    <div style="font-size:22px;font-weight:700;color:#262730;">5 stages</div>
    <div style="font-size:13px;color:#6b7280;">source to dashboard</div>
  </div>
  <div style="border:1px solid #e6e9ef;border-radius:10px;padding:14px;background:#fff;">
    <div style="font-size:12px;color:#6b7280;font-weight:700;">DATA</div>
    <div style="font-size:22px;font-weight:700;color:#262730;">raw + curated</div>
    <div style="font-size:13px;color:#6b7280;">JSON and SQLite</div>
  </div>
  <div style="border:1px solid #e6e9ef;border-radius:10px;padding:14px;background:#fff;">
    <div style="font-size:12px;color:#6b7280;font-weight:700;">TOOLS</div>
    <div style="font-size:22px;font-weight:700;color:#262730;">Python stack</div>
    <div style="font-size:13px;color:#6b7280;">SQLite, pandas, Altair, Streamlit</div>
  </div>
  <div style="border:1px solid #e6e9ef;border-radius:10px;padding:14px;background:#fff;">
    <div style="font-size:12px;color:#6b7280;font-weight:700;">OUTCOME</div>
    <div style="font-size:22px;font-weight:700;color:#262730;">DE basics</div>
    <div style="font-size:13px;color:#6b7280;">ingest, validate, serve, explain</div>
  </div>
</div>

## 1. Pipeline Flow

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#ffffff", "primaryBorderColor": "#e6e9ef", "primaryTextColor": "#262730", "lineColor": "#ff4b4b", "tertiaryColor": "#f8fafc", "fontFamily": "Inter, Arial"}}}%%
flowchart LR
    A["Source<br/><b>OpenAQ API</b><br/>or sample payloads"] --> B["Extract<br/><b>Python runner</b><br/>one or many locations"]
    B --> C["Raw<br/><b>JSON files</b><br/>replayable source responses"]
    C --> D["Transform<br/><b>Clean + validate</b><br/>typed curated rows"]
    D --> E["Store<br/><b>SQLite</b><br/>analytics-ready tables"]
    E --> F["Visualize<br/><b>Streamlit</b><br/>charts, map, guides"]

    D -.-> Q["Quality flags<br/>missing fields<br/>bad coordinates<br/>non-numeric values"]
    D -.-> S["Safety labels<br/>EPA/AirNow-style<br/>nominal ranges"]

    classDef stage fill:#ffffff,stroke:#e6e9ef,stroke-width:1px,color:#262730;
    classDef accent fill:#fff1f2,stroke:#ff4b4b,stroke-width:1px,color:#262730;
    class A,B,C,D,E,F stage;
    class Q,S accent;
```

**How to read it:** the pipeline keeps source data and analytics data separate. Raw JSON is retained first, then curated rows are created for SQL and dashboard use.

## 2. Data Shape

<div style="display:grid;grid-template-columns:1.15fr .85fr;gap:14px;">
  <div style="border:1px solid #e6e9ef;border-radius:10px;padding:16px;background:#fff;">
    <h3 style="margin-top:0;">Main curated table</h3>
    <p style="color:#4b5563;">The dashboard reads from <code>air_quality_measurements</code>. Each row is one latest pollutant reading at one monitoring location.</p>
    <table>
      <tr><th>Field group</th><th>Examples</th></tr>
      <tr><td>Location</td><td><code>location_id</code>, <code>location_name</code>, <code>country_code</code>, coordinates</td></tr>
      <tr><td>Pollutant</td><td><code>parameter</code>, <code>unit</code>, <code>value</code></td></tr>
      <tr><td>Time</td><td><code>measured_at_utc</code>, <code>measured_at_local</code></td></tr>
      <tr><td>Quality</td><td><code>quality_issues</code></td></tr>
      <tr><td>Lineage</td><td><code>source_url</code>, <code>ingested_at_utc</code></td></tr>
    </table>
  </div>
  <div style="border:1px solid #e6e9ef;border-radius:10px;padding:16px;background:#fff;">
    <h3 style="margin-top:0;">Run log table</h3>
    <p style="color:#4b5563;"><code>pipeline_runs</code> records each load so you can tell when it ran, what source URL was used, and how many rows were loaded.</p>
    <p style="color:#ff4b4b;font-weight:700;margin-bottom:0;">This is the beginning of observability.</p>
  </div>
</div>

## 3. Layered Data Flow

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#ffffff", "primaryBorderColor": "#e6e9ef", "primaryTextColor": "#262730", "lineColor": "#ff4b4b", "tertiaryColor": "#f8fafc", "fontFamily": "Inter, Arial"}}}%%
flowchart TB
    subgraph L1["Input"]
        A1["OpenAQ locations"]
        A2["OpenAQ latest measurements"]
        A3["Sample India city payloads"]
    end

    subgraph L2["Raw zone"]
        B1["data/raw/openaq_location_*.json"]
        B2["data/raw/openaq_latest_*.json"]
    end

    subgraph L3["Curated zone"]
        C1["air_quality_measurements"]
        C2["pipeline_runs"]
    end

    subgraph L4["Serving"]
        D1["separate pollutant charts"]
        D2["city comparison"]
        D3["risk-colored map"]
        D4["pollutant guide"]
    end

    A1 --> B1 --> C1 --> D1
    A2 --> B2 --> C1 --> D2
    A3 --> B1
    A3 --> B2
    C1 --> D3
    C1 --> D4
    C2 --> D2

    classDef box fill:#ffffff,stroke:#e6e9ef,color:#262730;
    classDef important fill:#fff1f2,stroke:#ff4b4b,color:#262730;
    class A1,A2,A3,B1,B2,C1,C2,D1,D2,D3,D4 box;
    class C1,C2 important;
```

## 4. Tools And Responsibilities

| Layer | Tool | Responsibility |
| --- | --- | --- |
| Source | OpenAQ API | Public location metadata and air-quality measurements. |
| Extract | Python | Calls API endpoints or loads sample payloads. |
| Raw storage | JSON files | Preserves original responses before transformation. |
| Transform | Python modules | Enriches readings with sensor metadata, validates values, adds safety context. |
| Store | SQLite | Local analytics database for measurements and run logs. |
| Visualize | Streamlit, pandas, Altair | Interactive filters, separate pollutant plots, maps, guides, and reference tables. |
| Verify | unittest | Protects transformation, threshold, pollutant, and multi-location behavior. |

## 5. Best Practices Checklist

<div style="border:1px solid #e6e9ef;border-radius:10px;padding:16px;background:#fff;">

| Best Practice | Why It Matters |
| --- | --- |
| Keep raw responses | Lets you debug and replay without calling the API again. |
| Create curated tables | Makes analytics easier than querying nested API JSON. |
| Use idempotent keys | Prevents duplicate rows when the same reading is loaded again. |
| Log each run | Gives visibility into row counts, source URLs, and load status. |
| Validate rows | Catches missing timestamps, invalid coordinates, and non-numeric readings. |
| Separate pollutant scales | PM2.5 and ozone use different units, so each needs its own plot. |
| Document thresholds | Safety labels need a clear source and caveat. |

</div>

## 6. Learning Outcomes

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#ffffff", "primaryBorderColor": "#e6e9ef", "primaryTextColor": "#262730", "lineColor": "#ff4b4b", "tertiaryColor": "#f8fafc", "fontFamily": "Inter, Arial"}}}%%
flowchart LR
    A["API ingestion"] --> B["Raw-to-curated modeling"]
    B --> C["Data quality checks"]
    C --> D["Local database serving"]
    D --> E["Unit-aware visualization"]
    E --> F["Data storytelling"]

    classDef outcome fill:#ffffff,stroke:#e6e9ef,color:#262730;
    classDef final fill:#fff1f2,stroke:#ff4b4b,color:#262730;
    class A,B,C,D,E outcome;
    class F final;
```

By the end of this project, you can explain not just the chart, but the engineering system behind it: where the data came from, how it was shaped, how it was checked, and why the visualization choices are trustworthy.

## 7. Project File Map

| File or Folder | Purpose |
| --- | --- |
| `scripts/run_air_quality_pipeline.py` | Runs sample or live ingestion for one or many locations. |
| `scripts/discover_india_locations.py` | Finds nearby live OpenAQ monitors for top Indian cities. |
| `src/air_quality_pulse/openaq_client.py` | Handles OpenAQ API requests. |
| `src/air_quality_pulse/pipeline.py` | Coordinates extraction, raw writes, transformation, and database load. |
| `src/air_quality_pulse/transform.py` | Builds curated measurement rows and quality issues. |
| `src/air_quality_pulse/storage.py` | Creates and writes SQLite tables. |
| `src/air_quality_pulse/thresholds.py` | Adds nominal EPA/AirNow safety labels. |
| `src/air_quality_pulse/pollutants.py` | Adds short pollutant effect descriptions. |
| `app/air_quality_dashboard.py` | Displays readings, comparisons, map, legend, and guides. |
| `tests/` | Verifies transformation, threshold, pollutant, and pipeline behavior. |

## References

- [OpenAQ API documentation](https://docs.openaq.org/)
- [OpenAQ API overview](https://docs.openaq.org/about/about)
- [OpenAQ quick start](https://docs.openaq.org/using-the-api/quick-start)
- [OpenAQ locations endpoint](https://docs.openaq.org/api/operations/locations_get_v3_locations_get)
- [AirNow AQI basics](https://www.airnow.gov/aqi/aqi-basics)
- [AirNow AQI colors](https://docs.airnowapi.org/aq101)
- [EPA particulate matter health effects](https://www.epa.gov/pm-pollution/health-and-environmental-effects-particulate-matter-pm)
- [EPA ozone health effects](https://www.epa.gov/ground-level-ozone-pollution/health-effects-ozone-pollution)
- [EPA nitrogen dioxide basics](https://www.epa.gov/no2-pollution/basic-information-about-no2)
