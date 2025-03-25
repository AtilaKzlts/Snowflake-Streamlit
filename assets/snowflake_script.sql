-- Weekly Campaign Data Fetch and Calculation

CREATE OR REPLACE STAGE s3_campaingn
  STORAGE_INTEGRATION = aws_sf_data
  URL = 's3://snow-frakfurt/campaign_customers.csv';

CREATE OR REPLACE TASK load_campaign_data_from_stage
  WAREHOUSE = COMPUTE_WH
  SCHEDULE = 'USING CRON 0 0 * * 1 UTC' -- Will run every Monday at 00:00 UTC
AS
  -- Step 1: Load data from S3 into your table
  COPY INTO campaign_customers
  FROM @s3_campaingn
  FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"')
  ON_ERROR = 'SKIP_FILE';  -- Skip files with errors.

  -- Step 2: Data Cleaning - Remove null or invalid data
  -- For example, remove rows with null AD_SPEND or REVENUE
  DELETE FROM campaign_customers
  WHERE AD_SPEND IS NULL OR REVENUE IS NULL;

  -- Step 3: Remove rows with zero CLICKS or IMPRESSIONS
  DELETE FROM campaign_customers
  WHERE CLICKS = 0 OR IMPRESSIONS = 0;

  -- Step 4: Calculate Key Metrics
  -- Calculate ROAS (Return on Ad Spend)
  UPDATE campaign_customers
  SET ROAS = REVENUE / AD_SPEND
  WHERE REVENUE IS NOT NULL AND AD_SPEND > 0;

  -- Calculate CTR (Click-Through Rate)
  UPDATE campaign_customers
  SET CTR = (CLICKS / IMPRESSIONS) * 100
  WHERE IMPRESSIONS > 0;

  -- Calculate AOV (Average Order Value)
  UPDATE campaign_customers
  SET AVG_ORDER_VALUE = REVENUE / CONVERSIONS
  WHERE CONVERSIONS > 0;

  -- Calculate Conversion Rate
  UPDATE campaign_customers
  SET CONVERSION_RATE = (CONVERSIONS / CLICKS) * 100
  WHERE CLICKS > 0;

ALTER TASK load_campaign_data_from_stage RESUME;
