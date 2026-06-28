-- Latest snapshot per market-contract combination with contract counts
with ranked as (
    select
        *,
        row_number() over (
            partition by market_id, contract_id
            order by extraction_ts desc
        ) as rn
    from "predictit"."main_marts"."fct_contract_prices"
)

select
    extraction_ts,
    market_id,
    market_name,
    market_status,
    contract_id,
    contract_name,
    last_trade_price,
    best_buy_yes_cost,
    best_sell_yes_cost,
    best_buy_no_cost,
    best_sell_no_cost,
    last_close_price,
    price_change_from_last_close,
    spread_yes,
    spread_no,

    -- Number of contracts in this market (window function across snapshot)
    count(*) over (partition by market_id) as contract_count

from ranked
where rn = 1