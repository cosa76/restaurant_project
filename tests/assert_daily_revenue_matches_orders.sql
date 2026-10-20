-- Réconciliation : le CA agrégé par jour doit égaler la somme des commandes.
-- Le test échoue s'il renvoie une ligne.
with daily as (
    select sum(revenue) as total from {{ ref('agg_daily_sales') }}
),

orders as (
    select sum(order_amount) as total from {{ ref('fct_orders') }}
)

select
    daily.total as daily_total,
    orders.total as orders_total
from daily
cross join orders
where daily.total != orders.total
