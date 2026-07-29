# Data Engineering Learning Pipeline

This roadmap is organized as a beginner-to-advanced implementation path. Each stage should be learned by building a working project, not by studying concepts in isolation.

## 1. Foundations

Learn:

- Linux shell basics
- Git and GitHub
- Python fundamentals
- SQL fundamentals
- JSON, CSV, and Parquet
- APIs and file formats

Implementation:

- Ingest CSV or API data with Python.
- Clean and validate the data.
- Load the result into a local database.

## 2. Relational Databases

Learn:

- PostgreSQL
- Table design
- Joins, indexes, and constraints
- Transactions
- Query optimization basics

Implementation:

- Build a small analytics database for orders, customers, and products.

## 3. Batch ETL and ELT

Learn:

- Extract, transform, load patterns
- Idempotency
- Incremental loads
- Staging tables
- Data validation

Implementation:

- Pull data from an API on a schedule.
- Store the raw response.
- Transform the data.
- Load curated tables.

## 4. Data Modeling

Learn:

- Star schemas
- Fact and dimension tables
- Slowly changing dimensions
- Normalization vs. denormalization
- Analytics-friendly modeling

Implementation:

- Convert a transactional database into a warehouse-style model.

## 5. Workflow Orchestration

Learn:

- Apache Airflow or Dagster
- DAGs
- Retries
- Scheduling
- Task dependencies
- Backfills

Implementation:

- Orchestrate the ETL pipeline with Airflow or Dagster.

## 6. Data Lake Basics

Learn:

- Object storage concepts
- Partitioning
- Parquet
- Schema evolution
- Raw, cleaned, and curated zones

Implementation:

- Store raw API or CSV data as files.
- Transform the data into partitioned Parquet datasets.

## 7. Spark and Distributed Processing

Learn:

- PySpark
- DataFrames
- Partitioning
- Joins and shuffles
- Spark SQL
- Performance basics

Implementation:

- Process a larger dataset with Spark.
- Write curated Parquet outputs.

## 8. Cloud Data Engineering

Pick one cloud platform first.

AWS path:

- S3
- Glue
- Athena
- Redshift
- Lambda

GCP path:

- Cloud Storage
- BigQuery
- Dataflow
- Cloud Composer

Azure path:

- Azure Data Lake Storage
- Synapse
- Data Factory
- Databricks

Implementation:

- Deploy the local batch pipeline to cloud storage and a cloud warehouse.

## 9. Modern Warehouse and ELT

Learn:

- Snowflake, BigQuery, Redshift, or Databricks SQL
- dbt
- Source freshness
- Tests
- Snapshots
- Documentation

Implementation:

- Use dbt to model raw data into analytics tables with tests and generated documentation.

## 10. Streaming Data

Learn:

- Kafka or Redpanda
- Producers and consumers
- Topics and partitions
- Event schemas
- Windowing basics
- Exactly-once vs. at-least-once processing concepts

Implementation:

- Stream fake user events into Kafka or Redpanda.
- Process the events.
- Store aggregates for analytics.

## 11. Data Quality and Observability

Learn:

- Great Expectations or Soda
- Data contracts
- Anomaly detection
- Lineage
- Logging and alerting
- Service-level expectations

Implementation:

- Add validation, alerts, and failure handling to the batch pipeline.

## 12. CI/CD and Infrastructure

Learn:

- Docker
- Docker Compose
- Terraform basics
- GitHub Actions
- Environment variables and secrets
- Automated testing

Implementation:

- Containerize the pipeline.
- Add automated checks before deployment.

## 13. Advanced Architecture

Learn:

- Medallion architecture
- Lakehouse design
- Change data capture
- Orchestration at scale
- Cost optimization
- Data governance
- Privacy and security

Implementation:

- Build an end-to-end lakehouse-style pipeline with raw ingestion, transformation, warehouse modeling, dashboard-ready tables, tests, and monitoring.

## Recommended Learning Order

```text
Python + SQL
PostgreSQL
ETL basics
Data modeling
Airflow or Dagster
Parquet + data lake
Spark
Cloud storage + warehouse
dbt
Kafka or Redpanda
Data quality
Docker + CI/CD
Capstone platform
```

## Capstone Project

Build an e-commerce data platform.

Include:

- API ingestion
- Batch file ingestion
- PostgreSQL source database
- Object storage data lake
- Spark transformation
- dbt warehouse models
- Airflow or Dagster orchestration
- Data quality checks
- Dashboard-ready tables
- Dockerized local environment
- Cloud deployment version

## Implementation Mindset

Start small, but make each project production-shaped:

- Use clear folder structure.
- Add logging.
- Make jobs retryable where possible.
- Keep configuration outside business logic.
- Make ingestion idempotent.
- Write focused tests.
- Document assumptions and run steps.
- Track failures and data quality issues.
