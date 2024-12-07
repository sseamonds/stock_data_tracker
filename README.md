# stock_data_tracker
Simple data eng project to practice some AWS flows using stock ticker data.

## Current State:
- code for pulling, cleaning, and calculating a couple basic metrics for a stock ticker
  - using pandas for transforms
  - Can be run in command line or in PyCharm/VSCode/etc with Run Configuration args
- Can persist data to local or existing S3 buckets. I follow the bronze/silver/gold paradigm 
- Persisting latest agg metrics for a stock to RDS
- Checking current nav discount against agg metrics
  - for instance, checking if the current NAV discount is lower than the yearly average NAV discount
  - in a Lambda, run manually

### To pull data from Yahoo finance :
- python stock_data_pull.py --type [price|nav] --stock_symbol <STOCK_TICKER_ALL_CAPS> --period=<TIME_LENGTH> --dest_path <LOCAL_OR_S3_PATH>
  - see NOTES below on period param
  - Example for CEF
    - python src/stock_data_pull.py --type price --stock_symbol AWF --period=1y --dest_path s3://sdt-stock-data/bronze/cef
    - python src/stock_data_pull.py --type nav --stock_symbol XAWFX --period=1y --dest_path s3://sdt-stock-data/bronze/cef
  - Example for stock
    - python src/stock_data_pull.py --type price --stock_symbol VOO --period=1y --dest_path s3://sdt-stock-data/bronze/stock
  - dest_path should be of format <s3_bronze_path>/cef for CEFs and <s3_bronze_path>/stock for stocks
### To clean data :
- python stock_data_clean_runnable.py --source_path <LOCAL_OR_S3_PATH> --dest_path <LOCAL_OR_S3_PATH>
  - Lambda trigger should be set to <s3_bronze_path>/cef for CEFs and <s3_bronze_path>/stock for stocks
### To calculate metrics :
- python stock_data_calcs_runnable.py --source_path <LOCAL_OR_S3_PATH> --dest_path <LOCAL_OR_S3_PATH>
- Lambda trigger should be set to <s3_silver_path>
### To Query/Insert stock metrics into RDS locally (must make RDS publicly accessible):
python src/rds_functions_runnable.py --action query|insert --stock_symbol <stock_ticker>
  - for CEFs, cef_data_clean_lambda.py is designed to only run when both price and nav files exist. it will clean and merge them

## NOTES:
- see docs/stock_tracker_overview.png for high level flow diagram
- see [yfinance](https://github.com/ranaroussi/yfinance) docs for general info on using the module
- for nav data for CEF's, we call yfinance with and 'X' on both sides of the ticker
  - eg : XDSLX, XAWFX
  - this will cause the NAV (net asset value) to be populated in the 'Close' field and is how we get NAV data for CEF's
  - pricing and nav data go to separate prefixes named 'price' and 'nav'
- see [Ticker class](https://github.com/ranaroussi/yfinance/wiki/Ticker#interface) for valid values for period arg above
- S3 paths seem to be recognized and credentials picked up automagically using the s3fs module
  - assuming you have credentials set up in ~/.aws

## Running cleaning/calcs scripts as lambdas:
#### The Lambda version of the code is in the lambdas directory
#### Setting up with S3-based triggers for lambdas will cause the cleaning and calcs scripts to run when you put a new raw stock file in the s3://<base_bucket>/bronze/ folder. 
- This can be done manually OR via stock_data_pull.py as described above but with an S3 destination
#### To setup lambdas for each process: 
- Create a lambda and 'deploy' the code : copy the lambdas/*.py file and all imported dependency src/*.py files to the lambda
  - Up your timeout (default is 3 seconds, I did a minute, currently the scripts typically run in 30 seconds or less)
- Create a trigger for lambdas which operate on files :
  - service : S3
  - event type : All object create events
  - bucket : your source data bucket (I use sdt-stock-data)
  - prefix : any subfolders (I use bronze/ and silver/ for my clean and calcs lambdas)
  - this will automatically add a [resource-based policy](https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html) allowing S3 to invoke your lambda function
    - or you can choose en existing role with a cloudWatch log policy, S3 write policy and select it
- Add a layer for awswrangler/pandas
  - I use 'AWSSDKPandas-Python312' which is one of the available options when adding a layer
  - the layer should contain any non-core python modules that you'd need
    - in this case we needed awswrangler, numpy, pandas
- Create a Policy to allow the lambda to write to CloudWatch and S3
  - Assign this policy to a role
  - Assign this role to the Lambda
  - Policy would look something like this:
```json
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:PutLogEvents",
                "logs:CreateLogGroup",
                "logs:CreateLogStream"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::<your_s3_bucket>",
                "arn:aws:s3:::<your_s3_bucket>/*"
            ]
        }
    ]
  }
```
- For the lambda to write high level stock metrics to RDS :
  - Setup RDS:
    - create an instance
    - connect to an EC2 instance to perform psql actions
    - connect to the lambda described below
    - create table using sql/create_stock_tables.sql
  - Setup the Lambda
    - use lambdas/stock_metrics_lambda.py
    - upload utils.py, rds_functions.py, and stock_metrics.py
    - run the scripts/build_psycopg_layer.sh to generate a psycopg layer in the form of a zip file 
    - add the psycopg zip as a layer and attach to the lambda
    - attach to the same VPC as the RDS instance
    - setup an VPC endpoint for S3 (https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html)
    - ensure the right security groups are attached with the VPC
      - for me it was the SG for the rds instance (outbound) and the default group (to allow to connect to S3)
- For lambdas which hit yfinance
  - use scripts/build_yfinance_layer.sh to build a yfinance layer
  - add the layer to the lambda
  - note that the zip should have "python/lib/python3.6/site-packages" as it's base dir
    - though it didn't seem to matter for the psycopg2 layer
- For lambdas which write to SQS:
  - create an SQS queue
  - create a role with policies to allow writing to SQS
    - I used the AWS managed policy AWSLambdaBasicExecutionRole and made a new policy allowing "sqs:SendMessage" actions for the SQS queue
    - trust relationship for "lambda.amazonaws.com" with action "sts:AssumeRole"
- For lambdas which read from SQS:
  - Create a role which allows consuming from sqs
    - I used the AWS managed policies AWSLambdaBasicExecutionRole and AWSLambdaSQSQueueExecutionRole
    - trust relationship for "lambda.amazonaws.com" with action "sts:AssumeRole"
  - add a trigger based on the SQS queue
 

## Future plans:
- BI views, visualization for gold data
  - Multiple metrics at once, nav/price for instance
  - Ability to change timescale as needed
  - Ability to view as percentage growth, div growth vs price growth for instance
  - STD Dev lines
  - Quicksight or tableau? Athena?
- Stock metadata 
  - type : stock, bond, CEF
  - average NAV all-time
  - average div yield all-time
  - div schedule, used to properly calculate yield
  - last updated date for the above
- More Calculations/Features
    - stock technical indicators (maybe : https://github.com/ta-lib/ta-lib-python)
    - full logic for calculating div yield
    - update 1 yr, 5 yr, overall calcs for each and store somewhere
    - Global indicators, M2, CAPE, VIX, etc
    - Historical PE for individual stocks
    - Overall gains for a period taking divs into account
- Store silver/gold data in database?
    - For BI dashboards
    - also for time series analysis
    - also for recalculating agg metrics on a periodic basis
    - or would OTF or parquet work with Athena or BI tool?
- Alerts
    - stock goes above/below moving avg
    - CEF nav discount above/below 1 year, multi-year, all-time average 
    - other tech indicator thresholds
    - email, sms?
- Auto update
    - daily pull of individual metrics for each stock
    - write to central store
    - recheck/trigger alerts
- Dashboard or api lookup for current snapshot view of stock calcs for a symbol:
  - current discount, pe, relation to 50/200 day avg and other indicators, etc
- Observations by the hour/minute
  - stream in, recheck alerts
- Containerize and automate with AWS batch, if load increases or maybe just for learning's sake
- DuckDB, Pyspark, ??? for silver -> gold transform if pandas can't handle the load
- LSTM predictive model