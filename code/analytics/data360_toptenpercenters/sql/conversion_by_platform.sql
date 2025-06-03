-- looking at visits by platform and conversion by platform
SELECT
  CASE churn_likelihood
    WHEN 'low' THEN '1-low'
    WHEN 'mid-low' THEN '2-mid-low'
    WHEN 'mid-high' THEN '3-mid-high'
    WHEN 'high' THEN '4-high'
    ELSE 'unknown'
  END AS churn_likelihood,
  SUM(desktop_visits) as desktop_visits, SUM(mw_app_visits) as mw_app_visits, SUM(boe_app_visits) as boe_app_visits,
  SUM(desktop_cart_adds) as desktop_cart_adds, SUM(mw_app_cart_adds) as mw_app_cart_adds, SUM(boe_app_cart_adds) as boe_app_cart_adds,
  SUM(desktop_conv_visits) as desktop_conv_visits, SUM(mw_app_conv_visits) as mw_app_conv_visits, SUM(boe_app_conv_visits) as boe_app_conv_visits
FROM `etsy-data-warehouse-dev.mmoy.orders_2023`
JOIN `etsy-data-warehouse-prod.buyer360.buyer_ltd` USING (mapped_user_id)
GROUP BY churn_likelihood
ORDER BY churn_likelihood
LIMIT 100;