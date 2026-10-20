-- Test générique : une transaction ne peut pas être datée dans le futur.
{% test not_in_future(model, column_name) %}

    select {{ column_name }}
    from {{ model }}
    where {{ column_name }} > current_timestamp

{% endtest %}
