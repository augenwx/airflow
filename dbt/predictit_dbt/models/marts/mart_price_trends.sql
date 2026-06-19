select
    market_id,
    market_name,
    contract_id,
    contract_name,
    date_trunc('hour', extraction_ts) as snapshot_hour,
    avg(last_trade_price) as avg_last_trade_price,
    min(last_trade_price) as min_last_trade_price,
    max(last_trade_price) as max_last_trade_price,
    count(*) as observations
from {{ ref('fct_contract_prices') }}
group by 1, 2, 3, 4, 5
