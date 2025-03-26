-- "Churn" here is defined as someone who moves out of the Top Ten Buyer (TTB) cohort from year to the next
with churn_base as (
  SELECT
    mapped_user_id,
    IF(is_top_buyer_2023 AND not is_top_buyer_2024, true, false) as churned,
    coalesce((SELECT gms_gross FROM UNNEST(annual_gms_struct) WHERE year = 2024),0) -
      coalesce((SELECT gms_gross FROM UNNEST(annual_gms_struct) WHERE year = 2023),0) as gms_diff,
--    coalesce((SELECT gms_pct_rank FROM UNNEST(annual_gms_struct) WHERE year = 2024),0) -
--      coalesce((SELECT gms_pct_rank FROM UNNEST(annual_gms_struct) WHERE year = 2023),0) as pct_rank_diff
  FROM `etsy-data-warehouse-dev.rollups.buyer_top_metadata`
)

-- How many people churned?
SELECT
  COUNTIF(churned)/COUNT(*) as pct_churned,
  COUNTIF(not churned)/COUNT(*) as pct_not_churned
FROM churn_base

-- For buyers who didn't churn, what was the avg difference in spend, change in rank?
SELECT
  AVG(gms_diff) as avg_gms_diff,
  COUNTIF(pct_rank_diff >= 0)/COUNT(*) as pct_dropped_in_rank,
  COUNTIF(pct_rank_diff < 0)/COUNT(*) as pct_rise_in_rank
FROM churn_base
WHERE NOT churned