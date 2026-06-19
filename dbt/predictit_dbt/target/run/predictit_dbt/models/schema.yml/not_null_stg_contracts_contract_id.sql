select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select contract_id
from "predictit"."main_staging"."stg_contracts"
where contract_id is null



      
    ) dbt_internal_test