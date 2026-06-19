select
    c.extraction_ts,
    c.market_id,
    m.market_name,
    c.contract_id,
    c.contract_name,
    c.last_trade_price,
    c.best_buy_yes_cost,
    c.best_sell_yes_cost,
    c.best_buy_no_cost,
    c.best_sell_no_cost,
    c.last_close_price,
    c.last_trade_price - c.last_close_price as price_change_from_last_close
from "predictit"."main_staging"."stg_contracts" c
left join "predictit"."main_staging"."stg_markets" m
    on c.market_id = m.market_id