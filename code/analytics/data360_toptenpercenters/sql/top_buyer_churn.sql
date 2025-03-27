-- "Churn" here is defined as someone who moves out of the Top Ten Buyer (TTB) cohort from year to the next
begin

-- tables
create temp table churn_base as (
  SELECT
    mapped_user_id,
    IF(is_top_buyer_2023 AND not is_top_buyer_2024, true, false) as churned,
    coalesce((SELECT gms_gross FROM UNNEST(annual_gms_struct) WHERE year = 2024),0) as gms_2024,
    coalesce((SELECT gms_gross FROM UNNEST(annual_gms_struct) WHERE year = 2023),0) as gms_2023,
    (SELECT gms_pct_rank FROM UNNEST(annual_gms_struct) WHERE year = 2024) as pct_rank_2024,
    (SELECT gms_pct_rank FROM UNNEST(annual_gms_struct) WHERE year = 2023) as pct_rank_2023,
    -- coalesce((SELECT gms_gross FROM UNNEST(annual_gms_struct) WHERE year = 2024),0) -
    --   coalesce((SELECT gms_gross FROM UNNEST(annual_gms_struct) WHERE year = 2023),0) as gms_diff,
    -- coalesce((SELECT gms_pct_rank FROM UNNEST(annual_gms_struct) WHERE year = 2024),0) -
    --   coalesce((SELECT gms_pct_rank FROM UNNEST(annual_gms_struct) WHERE year = 2023),0) as pct_rank_diff
  FROM `etsy-data-warehouse-dev.rollups.buyer_top_metadata`
  WHERE is_top_buyer_2023
);

-- one row per transations made by buyers in the TTB class of 2023
create temp table tx_2023 as (
      SELECT
      mapped_user_id,
      date,
      new_category as category,
      receipt_id as receipt_id,
      gms_net,
      gms_gross
    FROM `etsy-data-warehouse-prod.transaction_mart.transactions_gms_by_trans` t
    where
      t.date between '2023-01-01' and '2024-01-01'
    and buyer_country = 'US'
    and exists(
      select 1
      from `etsy-data-warehouse-dev.rollups.buyer_top_metadata`
      where is_top_buyer_2023 and mapped_user_id = t.mapped_user_id
    )
);

-- one row per ttb_2023 buyer with info about number of orders, gms, and min/max purchase dates
create temp table orders_2023 as (
  SELECT
    mapped_user_id,
    count(distinct receipt_id) as orders,
    CASE
      WHEN count(distinct receipt_id) <= 6 THEN 'high' -- based on previous analysis, these people have a 75% chance of churning
      WHEN count(distinct receipt_id) between 7 and 20 THEN 'mid-high'-- these people have a 50-75% chance
      WHEN count(distinct receipt_id) between 21 and 65 THEN 'mid-low'-- these people have a 25-50% chance
      ELSE 'low' -- these people have less than a 25% chance of churning
    END AS churn_likelihood,
    SUM(gms_net) AS gms_net,
    SUM(gms_gross) AS gms_gross,
    MIN(date) as min_purchase_date,
    MAX(date) as max_purchase_date
  FROM tx_2023
  GROUP BY 1
);

create temp table visits_2023 as (
  SELECT
    mapped_user_id,
    SUM(visits) as visits,
  FROM `etsy-data-warehouse-prod.buyer360.buyer_daily` bd
  WHERE _date between "2023-01-01" and "2023-12-31"
    and exists(
      select 1
      from `etsy-data-warehouse-dev.rollups.buyer_top_metadata`
      where is_top_buyer_2023 and mapped_user_id = bd.mapped_user_id)
  GROUP BY 1
);

-------------- QUERIES ----------------------------

-- How many people churned?
-- 62% churned, 38% didn't churn, 5.59M in the TTB class of 2023
SELECT
  COUNTIF(churned)/COUNT(*) as pct_churned,
  COUNTIF(not churned)/COUNT(*) as pct_not_churned,
  COUNT(*) as num_2023_ttb
FROM churn_base;

-- For buyers who didn't churn, what was the avg difference in spend, change in rank?
-- $ -69.05, 52% dropped in rank, 48% rose in rank
SELECT
  AVG(gms_2024-gms_2023) as avg_gms_diff,
  COUNTIF(pct_rank_2024-pct_rank_2023 >= 0 OR pct_rank_2024 IS NULL)/COUNT(*) as pct_dropped_in_rank,
  COUNTIF(pct_rank_2024-pct_rank_2023 < 0)/COUNT(*) as pct_rise_in_rank
FROM churn_base
WHERE NOT churned;

-- For buyers who DID churn, what was the avg difference in GMS?
-- $ -578
SELECT AVG(gms_2024-gms_2023) as avg_gms_diff
FROM churn_base
WHERE churned

-- what is the probability of churning given order frequency?
SELECT
  orders,
  COUNTIF(churned)/COUNT(*) as pct_churned
FROM churn_base
JOIN orders_2023 USING (mapped_user_id)
GROUP BY 1
ORDER BY 1
LIMIT 100;

-- what is the probability of churning given visit frequency?
SELECT
  visits,
  COUNTIF(churned)/COUNT(*) as pct_churned
FROM churn_base
JOIN visits_2023 USING (mapped_user_id)
GROUP BY 1
ORDER BY 1
LIMIT 1000;

-- category counts for "high" churn customers
SELECT
  category,
  count(*) as cnt
FROM tx_2023
WHERE exists(
    select 1
    from orders_2023
    where churn_likelihood = 'high' and mapped_user_id = tx_2023.mapped_user_id
  )
GROUP BY 1
ORDER BY 2 desc
;

-- category counts for "mid-high" churn customers
SELECT
  category,
  count(*) as cnt
FROM tx_2023
WHERE exists(
    select 1
    from orders_2023
    where churn_likelihood = 'mid-high' and mapped_user_id = tx_2023.mapped_user_id
  )
GROUP BY 1
ORDER BY 2 desc
;

-- category counts for "mid-low" churn customers
SELECT
  category,
  count(*) as cnt
FROM tx_2023
WHERE exists(
    select 1
    from orders_2023
    where churn_likelihood = 'mid-low' and mapped_user_id = tx_2023.mapped_user_id
  )
GROUP BY 1
ORDER BY 2 desc
;

-- category counts for "low" churn customers
SELECT
  category,
  count(*) as cnt
FROM tx_2023
WHERE exists(
    select 1
    from orders_2023
    where churn_likelihood = 'low' and mapped_user_id = tx_2023.mapped_user_id
  )
GROUP BY 1
ORDER BY 2 desc
;