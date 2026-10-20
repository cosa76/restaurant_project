-- Performance de chaque plat : volume, CA et part du CA total.
with item_sales as (

    select
        food_item,
        category,
        count(*)                       as order_count,
        sum(quantity)                  as items_sold,
        sum(order_amount)              as revenue
    from {{ ref('fct_orders') }}
    group by food_item, category

)

select
    *,
    round(100.0 * revenue / sum(revenue) over (), 2) as revenue_share_pct,
    rank() over (order by revenue desc)              as revenue_rank
from item_sales
