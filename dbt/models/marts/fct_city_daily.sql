select
    city_name,
    date,
    avg(temperature_2m_max) as avg_temperature_max,
    avg(temperature_2m_min) as avg_temperature_min,
    avg(temperature_2m_mean) as avg_temperature_mean,
    sum(precipitation_sum) as total_precipitation,
    max(wind_speed_10m_max) as max_wind_speed
from {{ ref('stg_weather_daily') }}
group by
    city_name,
    date
