-- Turning points: detect significant daily price changes (> 2 stddev)
with daily_changes as (
    -- Get daily prices and compute day-over-day changes
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        snapshot_date,
        lag(close_price) over (
            partition by contract_id
            order by snapshot_date
        ) as price_before,
        close_price as price_after,
        close_price - lag(close_price) over (
            partition by contract_id
            order by snapshot_date
        ) as impact
    from {{ ref('mart_rolling_averages') }}
),

with_stats as (
    -- Calculate per-contract stddev of daily changes for significance threshold
    select
        *,
        impact / nullif(price_before, 0) as impact_pct,
        stddev_pop(impact) over (partition by contract_id) as stddev_impact
    from daily_changes
    where impact is not null
)

select
    contract_id,
    contract_name,
    market_id,
    market_name,
    snapshot_date,
    price_before,
    price_after,
    impact,
    impact_pct,

    -- A change is significant if it exceeds 2 standard deviations
    abs(impact) > 2 * nullif(stddev_impact, 0) as is_significant,

    -- Direction of the price move
    case
        when impact > 0 then 'UP'
        else 'DOWN'
    end as trend_direction

from with_stats
