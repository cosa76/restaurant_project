-- Une ligne par commande. Renomme les colonnes en snake_case,
-- type les champs et calcule le montant de la ligne.
with source as (

    select * from {{ ref('restaurant_orders') }}

),

renamed as (

    select
        "Order ID"                         as order_id,
        trim("Customer Name")              as customer_name,
        trim("Food Item")                  as food_item,
        trim(category)                     as category,
        "Payment Method"                   as payment_method,
        cast(quantity as integer)          as quantity,
        cast(price as decimal(10, 2))      as unit_price,
        cast("Order Time" as timestamp)    as ordered_at
    from source

)

select
    *,
    cast(quantity * unit_price as decimal(12, 2)) as order_amount
from renamed
