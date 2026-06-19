select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select market_id
from "predictit"."main_staging"."stg_markets"
where market_id is null



      
    ) dbt_internal_test