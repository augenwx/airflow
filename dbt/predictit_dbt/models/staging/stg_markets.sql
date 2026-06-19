select
    cast(market_id as varchar) as market_id,
    market_name,
    market_short_name,
    market_url,
    market_status,
    cast(market_time_stamp as timestamp) as market_time_stamp,
    cast(extraction_ts as timestamp) as extraction_ts
from {{ source('raw', 'markets') }}
