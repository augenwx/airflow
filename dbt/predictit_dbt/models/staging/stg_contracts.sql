select
    cast(market_id as varchar) as market_id,
    cast(contract_id as varchar) as contract_id,
    contract_name,
    contract_short_name,
    contract_status,
    cast(last_trade_price as double) as last_trade_price,
    cast(best_buy_yes_cost as double) as best_buy_yes_cost,
    cast(best_buy_no_cost as double) as best_buy_no_cost,
    cast(best_sell_yes_cost as double) as best_sell_yes_cost,
    cast(best_sell_no_cost as double) as best_sell_no_cost,
    cast(last_close_price as double) as last_close_price,
    cast(display_order as integer) as display_order,
    cast(extraction_ts as timestamp) as extraction_ts
from {{ source('raw', 'contracts') }}
