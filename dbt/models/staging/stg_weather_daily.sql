with source_data as (

    select *
    from {{ source('raw', 'raw_weather_daily') }}

)

select
    city_name,
    latitude::double precision as latitude,
    longitude::double precision as longitude,
    date::date as date,
    temperature_2m_max::double precision as temperature_2m_max,
    temperature_2m_min::double precision as temperature_2m_min,
    temperature_2m_mean::double precision as temperature_2m_mean,
    precipitation_sum::double precision as precipitation_sum,
    wind_speed_10m_max::double precision as wind_speed_10m_max

from source_data
