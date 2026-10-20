-- Table de faits : une ligne par commande, enrichie des axes de temps
-- et de la clé client pour les jointures.
with orders as (

    select * from {{ ref('stg_restaurant_orders') }}

)

select
    order_id,
    md5(customer_name)                 as customer_id,
    food_item,
    category,
    payment_method,
    quantity,
    unit_price,
    order_amount,
    ordered_at,
    cast(ordered_at as date)           as order_date,
    date_trunc('month', ordered_at)::date as order_month,
    dayname(ordered_at)                as order_weekday,
    hour(ordered_at)                   as order_hour
from orders
