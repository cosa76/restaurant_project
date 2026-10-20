-- Test générique : échoue s'il existe une valeur nulle ou négative.
{% test positive(model, column_name) %}

    select {{ column_name }}
    from {{ model }}
    where {{ column_name }} <= 0

{% endtest %}
