-- Volatility analysis across 7, 30, and 90 day windows
with latest_info as (
    -- Get current price and extraction_ts per contract
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        last_trade_price as current_price,
        extraction_ts,
        row_number() over (
            partition by contract_id
            order by extraction_ts desc
        ) as rn
    from "predictit"."main_marts"."fct_contract_prices"
),

current_state as (
    select * from latest_info where rn = 1
),

-- 7-day window
window_7d as (
    select
        f.contract_id,
        7 as window_days,
        avg(f.last_trade_price) as avg_price,
        stddev_pop(f.last_trade_price) as stddev_price,
        max(f.last_trade_price) - min(f.last_trade_price) as price_range
    from "predictit"."main_marts"."fct_contract_prices" f
    where f.extraction_ts >= (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '7 days'
    group by 1, 2
),

-- 30-day window
window_30d as (
    select
        f.contract_id,
        30 as window_days,
        avg(f.last_trade_price) as avg_price,
        stddev_pop(f.last_trade_price) as stddev_price,
        max(f.last_trade_price) - min(f.last_trade_price) as price_range
    from "predictit"."main_marts"."fct_contract_prices" f
    where f.extraction_ts >= (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '30 days'
    group by 1, 2
),

-- 90-day window
window_90d as (
    select
        f.contract_id,
        90 as window_days,
        avg(f.last_trade_price) as avg_price,
        stddev_pop(f.last_trade_price) as stddev_price,
        max(f.last_trade_price) - min(f.last_trade_price) as price_range
    from "predictit"."main_marts"."fct_contract_prices" f
    where f.extraction_ts >= (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '90 days'
    group by 1, 2
),

-- Union all windows together
all_windows as (
    select * from window_7d
    union all
    select * from window_30d
    union all
    select * from window_90d
)

select
    c.contract_id,
    c.contract_name,
    c.market_id,
    c.market_name,
    w.window_days,
    w.avg_price,
    w.stddev_price,

    -- Volatility score: percentile rank of stddev within each window
    percent_rank() over (
        partition by w.window_days
        order by w.stddev_price
    ) as volatility_score,

    w.price_range,
    c.current_price,
    c.extraction_ts

from all_windows w
inner join current_state c
    on w.contract_id = c.contract_id