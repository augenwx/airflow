-- Top movers: gainers and losers over the last 24 hours
with latest_per_contract as (
    -- Get the most recent snapshot per contract
    select
        *,
        row_number() over (
            partition by market_id, contract_id
            order by extraction_ts desc
        ) as rn
    from "predictit"."main_marts"."fct_contract_prices"
),

current_prices as (
    select
        contract_id,
        contract_name,
        market_id,
        market_name,
        last_trade_price as price_now,
        extraction_ts
    from latest_per_contract
    where rn = 1
),

prices_24h_ago as (
    -- Get the snapshot closest to 24h ago per contract
    select
        contract_id,
        last_trade_price as price_24h_ago,
        row_number() over (
            partition by market_id, contract_id
            order by abs(
                epoch(extraction_ts) - epoch(
                    (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '24 hours'
                )
            )
        ) as rn
    from "predictit"."main_marts"."fct_contract_prices"
    where extraction_ts <= (select max(extraction_ts) from "predictit"."main_marts"."fct_contract_prices") - interval '12 hours'
),

joined as (
    select
        c.contract_id,
        c.contract_name,
        c.market_id,
        c.market_name,
        c.price_now,
        p.price_24h_ago,
        c.price_now - p.price_24h_ago as change_abs,
        (c.price_now - p.price_24h_ago) / nullif(p.price_24h_ago, 0) as change_pct,
        case
            when c.price_now >= p.price_24h_ago then 'GAINER'
            else 'LOSER'
        end as direction,
        c.extraction_ts
    from current_prices c
    left join prices_24h_ago p
        on c.contract_id = p.contract_id
        and p.rn = 1
)

select
    contract_id,
    contract_name,
    market_id,
    market_name,
    price_now,
    price_24h_ago,
    change_abs,
    change_pct,
    direction,

    -- Rank gainers (biggest positive change first)
    row_number() over (
        order by change_abs desc
    ) as rank_gainer,

    -- Rank losers (biggest negative change first)
    row_number() over (
        order by change_abs asc
    ) as rank_loser,

    extraction_ts

from joined
where price_24h_ago is not null