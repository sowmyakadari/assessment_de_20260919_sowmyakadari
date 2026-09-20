-- Fails if weather measurements contain physically invalid values.
select *
from {{ ref('stg_weather_daily') }}
where temperature_2m_min > temperature_2m_max
   or precipitation_sum < 0
   or wind_speed_10m_max < 0
