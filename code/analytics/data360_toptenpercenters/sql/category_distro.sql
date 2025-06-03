-- prep the aiq table to be matchable to the transaction table
WITH aiq_prepped AS (
SELECT
  mapped_user_id,
  ARRAY_CONCAT(
    IF(aiq_jewelry_purchaser, ['jewelry'], []),
    IF((aiq_online_purch_clothing > 5 OR aiq_apparel_children OR aiq_apparel_women OR aiq_apparel_young_men OR aiq_apparel_young_women OR aiq_male_merch_buyer), ['clothing'], []),
    IF(aiq_shop_shoes_specialty > 5, ['shoes'], []),
    IF(aiq_online_purch_books > 5 OR aiq_online_purch_music > 5, ['books_movies_and_music'], []),
    IF(aiq_spendex_furnish > 20 OR aiq_home_furnishings_deco OR aiq_home_improvement OR aiq_lt_home_garden > 5, ['home_and_living'], []),
    IF(aiq_pet_owner, ['pet_supplies'], []),
    IF(aiq_online_purch_beauty > 5, ['bath_and_beauty'], []),
    IF(aiq_art_antique_art OR aiq_arts_fan, ['art_and_collectibles'], []),
    IF(aiq_online_purch_electronics > 5, ['electronics_and_accessories'], []),
    IF(aiq_crafts_fan, ['craft_supplies_and_tools'], []),
    IF(aiq_children_learning_toys OR aiq_board_games_puzzles OR aiq_children_in_hh > 0, ['toys_and_games'], [])
  ) AS interests
FROM `etsy-data-warehouse-dev.mmoy.tx_2023`
JOIN `etsy-data-warehouse-prod.buyer360.aiq` USING (mapped_user_id)
),

aiq_exp AS (
  SELECT DISTINCT mapped_user_id, interest
  FROM
    aiq_prepped,
  UNNEST(interests) AS interest
),

user_purchased_cats AS (
SELECT DISTINCT mapped_user_id, category
FROM `etsy-data-warehouse-dev.mmoy.tx_2023`
WHERE gms_net > 0
),

num_cats_per_user AS (
SELECT
  CASE churn_likelihood
    WHEN 'low' THEN '1-low'
    WHEN 'mid-low' THEN '2-mid-low'
    WHEN 'mid-high' THEN '3-mid-high'
    WHEN 'high' THEN '4-high'
    ELSE 'unknown'
  END AS churn_likelihood,
  mapped_user_id,
  COUNT (DISTINCT category) as num_cats
FROM user_purchased_cats c
JOIN `etsy-data-warehouse-dev.mmoy.orders_2023` USING (mapped_user_id)
GROUP BY 1, 2
)

SELECT churn_likelihood, AVG(num_cats) as avg_num_cats
FROM num_cats_per_user
GROUP BY 1
ORDER BY 1;
