WITH projects_products AS (

  SELECT 
    TRIM(projects.own_number) AS "project_number",
    TRIM(REGEXP_REPLACE(indexes.index_name, '^:product_prefix', '')) AS "product_symbol"

  FROM 
    erp.client_orders AS orders
  LEFT JOIN
    erp.client_order_items AS items
      ON orders.year = items.order_year 
      AND orders.number = items.order_number
  LEFT JOIN
    erp.indexes AS indexes
      ON indexes.id = items.material_id
  LEFT JOIN
    erp.project_links AS links
      ON links.source_type = 3
      AND links.source_id1 = orders.year
      AND links.source_id2 = orders.number
  LEFT JOIN 
    erp.projects AS projects 
      ON projects.number = links.project_number 
      AND projects.year = links.project_year

  WHERE
    TRIM(projects.own_number) IN (:project_numbers)
  AND
    EXISTS (
      SELECT 1
      FROM UNNEST(ARRAY[:product_labels]) AS pattern
      WHERE TRIM(indexes.index_name) ILIKE pattern)
  AND
    indexes.index_name NOT SIMILAR TO '% [[:lower:]]{5,}%'
)

SELECT 
  project_number, 
  ARRAY_AGG(DISTINCT product_symbol)
FROM 
  projects_products 
GROUP BY 
  project_number;
