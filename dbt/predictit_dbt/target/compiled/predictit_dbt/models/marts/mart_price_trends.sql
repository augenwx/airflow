-- Hourly price trends with spread averages and date dimension
select
    market_id,
    market_name,
    contract_id,
    contract_name,
    date_trunc('hour', extraction_ts) as snapshot_hour,
    cast(date_trunc('hour', extraction_ts) as date) as snapshot_date,
    avg(last_trade_price) as avg_last_trade_price,
    min(last_trade_price) as min_last_trade_price,
    max(last_trade_price) as max_last_trade_price,
    max(last_trade_price) - min(last_trade_price) as price_range,
    avg(spread_yes) as avg_spread_yes,
    count(*) as observations
from "predictit"."main_marts"."fct_contract_prices"
group by 1, 2, 3, 4, 5, 6