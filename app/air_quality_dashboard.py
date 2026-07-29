from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_quality_pulse.thresholds import (
    RISK_COLOR_DOMAIN,
    RISK_COLOR_RANGE,
    classify_measurement,
    threshold_table,
)
from air_quality_pulse.pollutants import pollutant_description_rows

DEFAULT_DATABASE = ROOT / "data" / "curated" / "air_quality_pulse.db"


st.set_page_config(
    page_title="Air Quality Pulse",
    page_icon="",
    layout="wide",
)


@st.cache_data
def load_table(database_path: str, table_name: str) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(f"select * from {table_name}", connection)


def load_data(database_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not database_path.exists():
        st.error("No local air-quality database found. Run the pipeline first.")
        st.code("python3 scripts/run_air_quality_pipeline.py --sample")
        st.stop()

    measurements = load_table(str(database_path), "air_quality_measurements")
    runs = load_table(str(database_path), "pipeline_runs")

    if measurements.empty:
        st.warning("The database exists, but no measurements have been loaded yet.")
        st.stop()

    measurements["measured_at_utc"] = pd.to_datetime(
        measurements["measured_at_utc"],
        errors="coerce",
        utc=True,
    )
    threshold_labels = measurements.apply(
        lambda row: classify_measurement(row["parameter"], row["unit"], row["value"]),
        axis=1,
        result_type="expand",
    )
    measurements = pd.concat([measurements, threshold_labels], axis=1)
    measurements["has_quality_issue"] = measurements["quality_issues"].fillna("").ne("")
    runs["started_at_utc"] = pd.to_datetime(runs["started_at_utc"], errors="coerce", utc=True)
    return measurements, runs


def render_filters(measurements: pd.DataFrame) -> pd.DataFrame:
    locations = sorted(measurements["location_name"].dropna().unique())
    parameters = sorted(measurements["parameter"].dropna().unique())

    with st.sidebar:
        st.header("Filters")
        selected_locations = st.multiselect("Location", locations, default=locations)
        selected_parameters = st.multiselect("Pollutant", parameters, default=parameters)
        issue_filter = st.radio(
            "Quality",
            ["All rows", "Only clean rows", "Only rows with issues"],
            horizontal=False,
        )
        risk_levels = ["Safe", "Caution", "Unsafe", "High Risk", "Unknown"]
        selected_risk_levels = st.multiselect("Risk level", risk_levels, default=risk_levels)

    filtered = measurements[
        measurements["location_name"].isin(selected_locations)
        & measurements["parameter"].isin(selected_parameters)
        & measurements["risk_level"].isin(selected_risk_levels)
    ].copy()

    if issue_filter == "Only clean rows":
        filtered = filtered[~filtered["has_quality_issue"]]
    elif issue_filter == "Only rows with issues":
        filtered = filtered[filtered["has_quality_issue"]]

    return filtered


def render_metrics(measurements: pd.DataFrame, runs: pd.DataFrame) -> None:
    latest_run = runs.sort_values("started_at_utc", ascending=False).head(1)
    run_status = latest_run["status"].iloc[0] if not latest_run.empty else "unknown"
    invalid_rows = int(measurements["has_quality_issue"].sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Readings", f"{len(measurements):,}")
    col2.metric("Locations", f"{measurements['location_name'].nunique():,}")
    col3.metric("Rows with issues", f"{invalid_rows:,}")
    col4.metric("High risk rows", f"{int(measurements['risk_level'].eq('High Risk').sum()):,}")

    st.caption(f"Latest pipeline run: {run_status}")


def render_latest_chart(measurements: pd.DataFrame) -> None:
    latest = (
        measurements.sort_values("measured_at_utc")
        .groupby(["location_name", "parameter", "unit"], as_index=False)
        .tail(1)
        .sort_values("value", ascending=False)
    )

    st.subheader("Latest Readings")
    render_parameter_charts(latest, x_field="location_name")
    st.dataframe(
        latest[
            [
                "location_name",
                "parameter",
                "parameter_display_name",
                "value",
                "unit",
                "risk_level",
                "category",
                "measured_at_utc",
                "quality_issues",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


def render_location_comparison(measurements: pd.DataFrame) -> None:
    latest = (
        measurements.sort_values("measured_at_utc")
        .groupby(["location_name", "parameter", "unit"], as_index=False)
        .tail(1)
    )

    st.subheader("Location Comparison")
    if latest.empty:
        st.info("No readings found for comparison.")
        return

    render_parameter_charts(latest, x_field="location_name")
    st.dataframe(
        latest.sort_values(["parameter", "value"], ascending=[True, False])[
            [
                "location_name",
                "locality",
                "country_code",
                "parameter",
                "value",
                "unit",
                "risk_level",
                "category",
                "measured_at_utc",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


def render_parameter_charts(data: pd.DataFrame, x_field: str) -> None:
    parameters = sorted(data["parameter"].dropna().unique())
    if not parameters:
        return

    for parameter in parameters:
        chart_data = data[data["parameter"].eq(parameter)].sort_values("value", ascending=False)
        if chart_data.empty:
            continue

        unit = next((str(unit) for unit in chart_data["unit"].dropna().unique()), "")
        title = f"{parameter} latest value"
        if unit:
            title = f"{title} ({unit})"

        st.altair_chart(
            _bar_chart(chart_data, x_field=x_field, title=title),
            width="stretch",
        )


def render_quality_table(measurements: pd.DataFrame) -> None:
    st.subheader("Quality Review")
    issue_rows = measurements[measurements["has_quality_issue"]]
    if issue_rows.empty:
        st.success("No quality issues found in the selected data.")
        return

    st.dataframe(
        issue_rows[
            [
                "measurement_key",
                "location_name",
                "parameter",
                "value",
                "measured_at_utc",
                "quality_issues",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


def render_pipeline_runs(runs: pd.DataFrame) -> None:
    st.subheader("Pipeline Runs")
    if runs.empty:
        st.info("No pipeline run records found.")
        return

    recent_runs = runs.sort_values("started_at_utc", ascending=False).head(20)
    st.dataframe(
        recent_runs[
            [
                "started_at_utc",
                "row_count",
                "invalid_row_count",
                "status",
                "source_url",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


def render_threshold_reference() -> None:
    st.subheader("Nominal Risk Thresholds")
    st.caption(
        "These are EPA/AirNow AQI concentration breakpoints used here as dashboard labels. "
        "Official AQI calculations use pollutant-specific averaging periods, so treat this as context for latest readings."
    )
    st.dataframe(
        pd.DataFrame(threshold_table()),
        width="stretch",
        hide_index=True,
    )


def render_safety_legend() -> None:
    st.subheader("Safety Range Legend")
    legend = pd.DataFrame(
        {
            "risk_level": RISK_COLOR_DOMAIN,
            "order": range(len(RISK_COLOR_DOMAIN)),
            "description": [
                "Good",
                "Moderate",
                "Unhealthy for sensitive groups or unhealthy",
                "Very unhealthy or hazardous",
                "No threshold available",
            ],
        }
    )
    chart = (
        alt.Chart(legend)
        .mark_bar(size=30)
        .encode(
            x=alt.X("order:O", axis=None),
            y=alt.value(30),
            color=alt.Color(
                "risk_level:N",
                scale=alt.Scale(domain=RISK_COLOR_DOMAIN, range=RISK_COLOR_RANGE),
                legend=None,
            ),
            tooltip=["risk_level", "description"],
        )
        .properties(height=70)
    )
    labels = (
        alt.Chart(legend)
        .mark_text(dy=26, fontSize=12)
        .encode(x=alt.X("order:O", axis=None), text="risk_level:N")
    )
    st.altair_chart(chart + labels, width="stretch")


def render_pollutant_guide(measurements: pd.DataFrame) -> None:
    parameters = tuple(sorted(measurements["parameter"].dropna().unique()))
    if not parameters:
        return

    st.subheader("Pollutant Guide")
    st.dataframe(
        pd.DataFrame(pollutant_description_rows(parameters)),
        width="stretch",
        hide_index=True,
    )


def render_map(measurements: pd.DataFrame) -> None:
    mapped = measurements.dropna(subset=["latitude", "longitude"]).copy()
    if mapped.empty:
        return

    latest = (
        mapped.sort_values("measured_at_utc")
        .groupby(["location_name", "parameter"], as_index=False)
        .tail(1)
    )
    risk_rank = {"High Risk": 4, "Unsafe": 3, "Caution": 2, "Safe": 1, "Unknown": 0}
    latest["risk_rank"] = latest["risk_level"].map(risk_rank).fillna(0)
    mapped = latest.sort_values("risk_rank").groupby("location_name", as_index=False).tail(1)

    st.subheader("Monitoring Locations")
    st.map(
        mapped.rename(columns={"latitude": "lat", "longitude": "lon"}),
        latitude="lat",
        longitude="lon",
        size=80,
        color="risk_color",
    )


def _bar_chart(data: pd.DataFrame, x_field: str, title: str) -> alt.Chart:
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(f"{x_field}:N", sort="-y", title=None),
            y=alt.Y("value:Q", title=title),
            color=alt.Color(
                "risk_level:N",
                scale=alt.Scale(domain=RISK_COLOR_DOMAIN, range=RISK_COLOR_RANGE),
                title="Safety range",
            ),
            tooltip=[
                "location_name",
                "parameter",
                "value",
                "unit",
                "risk_level",
                "category",
                "measured_at_utc",
            ],
        )
        .properties(height=320)
    )


def main() -> None:
    st.title("Air Quality Pulse")
    measurements, runs = load_data(DEFAULT_DATABASE)
    filtered = render_filters(measurements)

    render_safety_legend()
    render_pollutant_guide(filtered)
    render_metrics(filtered, runs)
    render_latest_chart(filtered)
    render_location_comparison(filtered)

    left, right = st.columns([2, 1])
    with left:
        render_map(filtered)
    with right:
        render_quality_table(filtered)

    render_threshold_reference()
    render_pipeline_runs(runs)


if __name__ == "__main__":
    main()
