-- Customer Purchase Analysis Query
-- Gets all customers with their historical purchase frequency and total spending

WITH order_with_lines AS (
    SELECT 
        o.id as order_id,
        o.customer_id,
        o.total_price,
        o.created_at,
        COALESCE(
            JSON_AGG(
                JSON_BUILD_OBJECT(
                    'product_name', COALESCE(pv.display_name, pv.title, 'Unknown Product'),
                    'product_price', ROUND(pv.price::numeric, 2),
                    'quantity', ol.quantity
                )
                ORDER BY ol.id
            ) FILTER (WHERE ol.id IS NOT NULL),
            '[]'::json
        ) AS order_lines
    FROM 
        "meama_shopify"."order" o
    LEFT JOIN 
        "meama_shopify"."order_line" ol ON o.id = ol.order_id
    LEFT JOIN 
        "meama_shopify"."product_variant" pv ON ol.variant_id = pv.id
    WHERE 
        NOT o.financial_status = 'refunded'
    GROUP BY 
        o.id, o.customer_id, o.total_price, o.created_at
)

SELECT 
    c.id,
    c.email,
    -- Historical purchase frequency (aggregated order details as JSON)
    COALESCE(
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'order_id', owl.order_id,
                'total_spent', ROUND(owl.total_price::numeric, 2),
                'order_date', owl.created_at,
                'order_lines', owl.order_lines
            ) 
            ORDER BY owl.created_at DESC
        ) FILTER (WHERE owl.order_id IS NOT NULL), 
        '[]'::json
    ) AS historical_purchase_frequency,
    -- Historical spending (total amount spent by customer)
    ROUND(COALESCE(SUM(owl.total_price), 0)::numeric, 2) AS historical_spending,
    -- Average spending per order
    ROUND(COALESCE(AVG(owl.total_price), 0)::numeric, 2) AS average_order_value,
    -- Total number of orders
    COUNT(owl.order_id) AS total_orders
FROM 
    "meama_shopify"."customer" c
LEFT JOIN 
    order_with_lines owl ON c.id = owl.customer_id
WHERE 
    c.email NOT IN ('distribution@meama.ge')
GROUP BY 
    c.id, c.email
ORDER BY 
    c.id;
