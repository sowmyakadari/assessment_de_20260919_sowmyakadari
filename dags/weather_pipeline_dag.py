import sys
from datetime import datetime, timedelta

sys.path.insert(0, "/opt/airflow")

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingestion.weather_pipeline import load_weather


def run_weather_load(**context):
    run_date = context["ds"]
    load_weather(run_date)


default_args = {
    "owner": "sowmya",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="weather_pipeline",
    default_args=default_args,
    description="Daily weather extraction, loading, dbt transformation and testing",
    schedule="0 6 * * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["weather", "etl", "dbt"],
) as dag:

    extract_and_load = PythonOperator(
        task_id="extract_and_load",
        python_callable=run_weather_load,
        execution_timeout=timedelta(minutes=10),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt",
        execution_timeout=timedelta(minutes=10),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir /opt/airflow/dbt",
        execution_timeout=timedelta(minutes=10),
    )

    extract_and_load >> dbt_run >> dbt_test
