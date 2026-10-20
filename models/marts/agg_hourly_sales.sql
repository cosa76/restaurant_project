-- Activité par heure de la journée, pour repérer les pics de service.
select
    order_hour,
    count(*)                           as order_count,
    sum(order_amount)                  as revenue
from {{ ref('fct_orders') }}
group by order_hour
