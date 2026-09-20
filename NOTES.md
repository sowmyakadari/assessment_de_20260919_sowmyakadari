# Notes

## Time spent

Approximately 7 hours, including setup, extract/load, dbt, Airflow, notebook, testing, and final verification.

## What I would do with more time

- Add broader historical data coverage and additional data-quality checks.
- Further improve production-oriented configuration and monitoring.

## Known gaps

- The pipeline currently processes the configured cities for a logical run date, with different dates supported for backfills.
- The setup is designed for the assessment environment rather than a production deployment.

## AI-usage declaration

Used ChatGPT for technical guidance, troubleshooting, and reviewing implementation approaches during development. I implemented and verified the solution locally and validated the pipeline outputs, DAG runs, and dbt tests.

| Where (file / area) | What the tool did | What I changed afterwards |
| --- | --- | --- |
| Project setup | Helped troubleshoot Docker and environment configuration issues. | Applied the configuration and verified the services locally. |
| Python ingestion | Provided guidance on API handling, PostgreSQL loading, retries, and idempotency. | Implemented and tested the ingestion pipeline. |
| Airflow / notebook | Helped troubleshoot orchestration and notebook execution. | Ran and verified the DAG and executed notebook outputs. |