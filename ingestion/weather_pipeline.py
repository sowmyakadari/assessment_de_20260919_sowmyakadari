import os
from datetime import date
from pathlib import Path

import psycopg2
import requests
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential


BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
CONFIG_PATH = Path("/opt/airflow/config/cities.yml")


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "de"),
        password=os.getenv("POSTGRES_PASSWORD", "de"),
        dbname=os.getenv("POSTGRES_DB", "warehouse"),
    )


def load_cities():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)["cities"]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
)
def fetch_weather(latitude, longitude, run_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": run_date,
        "end_date": run_date,
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "wind_speed_10m_max",
            ]
        ),
        "timezone": "UTC",
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def create_raw_table(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_weather_daily (
                city_name TEXT NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                date DATE NOT NULL,
                temperature_2m_max DOUBLE PRECISION,
                temperature_2m_min DOUBLE PRECISION,
                temperature_2m_mean DOUBLE PRECISION,
                precipitation_sum DOUBLE PRECISION,
                wind_speed_10m_max DOUBLE PRECISION,
                PRIMARY KEY (city_name, date)
            );
            """
        )
    connection.commit()


def load_weather(run_date):
    connection = get_db_connection()

    try:
        create_raw_table(connection)

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM raw_weather_daily WHERE date = %s;",
                (run_date,),
            )

        cities = load_cities()

        for city in cities:
            data = fetch_weather(
                city["latitude"],
                city["longitude"],
                run_date,
            )

            daily = data["daily"]

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO raw_weather_daily (
                        city_name,
                        latitude,
                        longitude,
                        date,
                        temperature_2m_max,
                        temperature_2m_min,
                        temperature_2m_mean,
                        precipitation_sum,
                        wind_speed_10m_max
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        city["name"],
                        city["latitude"],
                        city["longitude"],
                        daily["time"][0],
                        daily["temperature_2m_max"][0],
                        daily["temperature_2m_min"][0],
                        daily["temperature_2m_mean"][0],
                        daily["precipitation_sum"][0],
                        daily["wind_speed_10m_max"][0],
                    ),
                )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    import sys

    run_date = sys.argv[1] if len(sys.argv) > 1 else str(date.today())
    load_weather(run_date)
    print(f"Loaded weather data for {run_date}")
