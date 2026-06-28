-- Contract leaderboard: ranking by current price and price movement
select
    contract_id,
    contract_name,
    market_id,
    market_name,
    last_trade_price,
    last_close_price,
    abs(price_change_from_last_close) as price_change_abs,

    -- Rank by highest current price
    row_number() over (order by last_trade_price desc) as rank_by_price,

    -- Rank by largest absolute price movement
    row_number() over (order by abs(price_change_from_last_close) desc) as rank_by_movement,

    extraction_ts

from "predictit"."main_marts"."mart_market_snapshot"