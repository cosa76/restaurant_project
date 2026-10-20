-- Une ligne par client, avec son historique de commandes.
-- Le CSV n'a pas d'identifiant client : on dérive une clé du nom.
with orders as (

    select * from {{ ref('stg_restaurant_orders') }}

)

select
    md5(customer_name)                 as customer_id,
    customer_name,
    count(*)                           as order_count,
    sum(quantity)                      as items_ordered,
    sum(order_amount)                  as lifetime_revenue,
    min(ordered_at)                    as first_order_at,
    max(ordered_at)                    as last_order_at
from orders
group by customer_name
