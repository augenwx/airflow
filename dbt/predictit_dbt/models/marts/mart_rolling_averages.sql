-- Daily closing prices with 7d, 14d, and 30d rolling averages
with daily_prices as (
    -- Aggregate to daily level: take the last recorded price per day per contract
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        cast(extraction_ts as date) as snapshot_date,
        -- Use the last price of the day (by extraction timestamp)
        last(last_trade_price order by extraction_ts) as close_price
    from {{ ref('fct_contract_prices') }}
    group by 1, 2, 3, 4, 5
)

select
    contract_id,
    contract_name,
    market_id,
    market_name,
    snapshot_date,
    close_price,

    -- 7-day moving average
    avg(close_price) over (
        partition by contract_id
        order by snapshot_date
        rows between 6 preceding and current row
    ) as avg_7d,

    -- 14-day moving average
    avg(close_price) over (
        partition by contract_id
        order by snapshot_date
        rows between 13 preceding and current row
    ) as avg_14d,

    -- 30-day moving average
    avg(close_price) over (
        partition by contract_id
        order by snapshot_date
        rows between 29 preceding and current row
    ) as avg_30d

from daily_prices
