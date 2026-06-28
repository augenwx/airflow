
  
    
    

    create  table
      "predictit"."main_marts"."mart_anomaly_detection__dbt_tmp"
  
    as (
      -- Anomaly detection: z-scores, pattern signals, and anomaly scoring
with stats_30d as (
    -- Calculate 30-day average and stddev per contract
    select
        contract_id,
        avg(last_trade_price) as avg_price_30d,
        stddev_pop(last_trade_price) as stddev_price_30d
    from "predictit"."main_marts"."fct_contract_prices"
    where extraction_ts >= (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '30 days'
    group by 1
),

current_snapshot as (
    -- Latest price per contract
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        last_trade_price as current_price,
        spread_yes,
        extraction_ts,
        row_number() over (
            partition by contract_id
            order by extraction_ts desc
        ) as rn
    from "predictit"."main_marts"."fct_contract_prices"
),

snapshot_24h_ago as (
    -- Price ~24h ago per contract for change calculation
    select
        contract_id,
        last_trade_price as price_24h_ago,
        row_number() over (
            partition by contract_id
            order by abs(
                epoch(extraction_ts) - epoch(
                    (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '24 hours'
                )
            )
        ) as rn
    from "predictit"."main_marts"."fct_contract_prices"
    where extraction_ts <= (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '12 hours'
),

change_stats as (
    -- Stddev of all 24h changes across contracts for "unusual jump" threshold
    select stddev_pop(change_24h) as stddev_all_changes
    from (
        select
            c.contract_id,
            c.current_price - p.price_24h_ago as change_24h
        from current_snapshot c
        inner join snapshot_24h_ago p
            on c.contract_id = p.contract_id and p.rn = 1
        where c.rn = 1
    ) sub
),

spread_percentile as (
    -- 90th percentile of spread_yes for liquidity risk detection
    select
        percentile_cont(0.90) within group (order by spread_yes) as p90_spread_yes
    from current_snapshot
    where rn = 1
),

base as (
    select
        c.contract_id,
        c.contract_name,
        c.market_id,
        c.market_name,
        c.current_price,
        s.avg_price_30d,
        s.stddev_price_30d,

        -- Z-score: how many stddevs the current price is from the 30d mean
        (c.current_price - s.avg_price_30d) / nullif(s.stddev_price_30d, 0) as z_score,

        -- Is anomaly: absolute z-score exceeds 2
        abs((c.current_price - s.avg_price_30d) / nullif(s.stddev_price_30d, 0)) > 2 as is_anomaly,

        -- 24h price change
        c.current_price - p.price_24h_ago as change_24h,

        -- 30d volatility (stddev)
        s.stddev_price_30d as volatility_30d,

        c.spread_yes,
        c.extraction_ts

    from current_snapshot c
    inner join stats_30d s on c.contract_id = s.contract_id
    left join snapshot_24h_ago p on c.contract_id = p.contract_id and p.rn = 1
    where c.rn = 1
)

select
    b.contract_id,
    b.contract_name,
    b.market_id,
    b.market_name,
    b.current_price,
    b.avg_price_30d,
    b.stddev_price_30d,
    b.z_score,
    b.is_anomaly,
    b.change_24h,
    b.volatility_30d,

    -- Anomaly score: combines z-score magnitude with 24h change
    abs(b.z_score) * (1 + abs(coalesce(b.change_24h, 0))) as anomaly_score,

    -- Signal type classification
    case
        when b.z_score > 2 and coalesce(b.change_24h, 0) > 0
            then 'Momentum Breakout'
        when b.z_score < -2 and coalesce(b.change_24h, 0) > 0
            then 'Mean Reversion'
        when b.spread_yes > sp.p90_spread_yes
            then 'Liquidity Risk'
        when abs(coalesce(b.change_24h, 0)) > 2 * cs.stddev_all_changes
            then 'Unusual Jump'
        else null
    end as signal_type,

    -- Signal strength classification
    case
        when abs(b.z_score) * (1 + abs(coalesce(b.change_24h, 0))) > 1 then 'STRONG'
        when abs(b.z_score) * (1 + abs(coalesce(b.change_24h, 0))) > 0.5 then 'HIGH'
        else 'MODERATE'
    end as signal_strength,

    b.extraction_ts

from base b
cross join change_stats cs
cross join spread_percentile sp
    );
  
  