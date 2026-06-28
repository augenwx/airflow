
  
    
    

    create  table
      "predictit"."main_marts"."mart_candidate_momentum__dbt_tmp"
  
    as (
      -- Candidate momentum: 30-day momentum classification and ranking
with daily_changes as (
    -- Calculate day-over-day price change per contract
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        snapshot_date,
        close_price,
        close_price - lag(close_price) over (
            partition by contract_id
            order by snapshot_date
        ) as daily_change
    from "predictit"."main_marts"."mart_rolling_averages"
),

last_30d as (
    -- Filter to last 30 days of data
    select *
    from daily_changes
    where snapshot_date >= (select max(snapshot_date) from daily_changes) - interval '30 days'
      and daily_change is not null
),

momentum as (
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        avg(daily_change) as avg_daily_change,
        sum(daily_change) as total_change_30d,
        -- Current price is the latest close
        last(close_price order by snapshot_date) as current_price,
        max(snapshot_date) as extraction_ts
    from last_30d
    group by 1, 2, 3, 4
)

select
    contract_id,
    contract_name,
    market_id,
    market_name,
    avg_daily_change,
    total_change_30d,

    -- Momentum direction classification
    case
        when abs(avg_daily_change) > 0.005 and avg_daily_change > 0 then 'Strong ▲'
        when abs(avg_daily_change) > 0.005 and avg_daily_change <= 0 then 'Strong ▼'
        when abs(avg_daily_change) > 0.001 and avg_daily_change > 0 then 'Moderate ▲'
        when abs(avg_daily_change) > 0.001 and avg_daily_change <= 0 then 'Moderate ▼'
        when avg_daily_change > 0 then 'Weak ▲'
        else 'Weak ▼'
    end as momentum_direction,

    -- Rank by absolute momentum strength
    row_number() over (order by abs(avg_daily_change) desc) as momentum_rank,

    current_price,
    extraction_ts

from momentum
    );
  
  