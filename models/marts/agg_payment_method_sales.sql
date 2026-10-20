-- Répartition des commandes et du CA par moyen de paiement.
select
    payment_method,
    count(*)                           as order_count,
    sum(order_amount)                  as revenue,
    round(100.0 * count(*) / sum(count(*)) over (), 2) as order_share_pct
from {{ ref('fct_orders') }}
group by payment_method
