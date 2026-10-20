-- Une ligne par plat de la carte, avec sa catégorie et ses prix observés.
with orders as (

    select * from {{ ref('stg_restaurant_orders') }}

)

select
    food_item,
    category,
    min(unit_price)                    as min_unit_price,
    max(unit_price)                    as max_unit_price,
    cast(avg(unit_price) as decimal(10, 2)) as avg_unit_price
from orders
group by food_item, category
