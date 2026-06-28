-- Spread and liquidity analysis over the last 30 days
with last_30d as (
    select *
    from "predictit"."main_marts"."fct_contract_prices"
    where extraction_ts >= (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '30 days'
),

spread_stats as (
    -- Aggregate spread metrics per contract over 30 days
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        avg(spread_yes) as avg_spread_yes,
        avg(spread_no) as avg_spread_no,
        max(spread_yes) as max_spread_yes,
        stddev_pop(last_trade_price) as implied_volatility
    from last_30d
    group by 1, 2, 3, 4
),

current_snapshot as (
    -- Get current spread values
    select
        contract_id,
        spread_yes as current_spread_yes,
        spread_no as current_spread_no,
        extraction_ts,
        row_number() over (
            partition by contract_id
            order by extraction_ts desc
        ) as rn
    from "predictit"."main_marts"."fct_contract_prices"
)

select
    s.contract_id,
    s.contract_name,
    s.market_id,
    s.market_name,
    s.avg_spread_yes,
    s.avg_spread_no,
    s.max_spread_yes,
    c.current_spread_yes,
    c.current_spread_no,
    s.implied_volatility,

    -- Spread-to-volatility ratio: how much of the spread is explained by volatility
    s.avg_spread_yes / nullif(s.implied_volatility, 0) as spread_volatility_ratio,

    c.extraction_ts

from spread_stats s
inner join current_snapshot c
    on s.contract_id = c.contract_id
    and c.rn = 1