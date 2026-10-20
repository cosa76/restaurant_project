-- Chiffre d'affaires et volume par jour.
select
    order_date,
    count(*)                           as order_count,
    sum(quantity)                      as items_sold,
    sum(order_amount)                  as revenue,
    cast(avg(order_amount) as decimal(10, 2)) as avg_order_value
from {{ ref('fct_orders') }}
group by order_date
