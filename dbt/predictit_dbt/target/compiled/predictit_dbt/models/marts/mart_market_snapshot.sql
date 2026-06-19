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
    contract_id,
    contract_name,
    last_trade_price,
    best_buy_yes_cost,
    best_sell_yes_cost,
    price_change_from_last_close
from ranked
where rn = 1