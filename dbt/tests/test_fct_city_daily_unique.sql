-- Fails if the mart contains duplicate city/date combinations.
select
    city_name,
    date,
    count(*) as row_count
from {{ ref('fct_city_daily') }}
group by city_name, date
having count(*) > 1
