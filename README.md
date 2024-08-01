# stock_data_tracker
Simple data eng project to practice some AWS flows using stock ticker data.

## Current State:
- code for pulling, cleaning, and calculating a couple basic metrics for a stock ticker
- using pandas for transforms
- can be in command line or in pycharm with Run Configuration args
- can persist data to local or existing S3 buckets. I follow the bronze/silver/gold paradigm 

### To pull data from Yahoo finance :
- python stock_data_pull.py --stock_symbol <STOCK_TICKER_ALL_CAPS> --period=<TIME_LENGTH> --dest_path <LOCAL_OR_S3_PATH>
### To clean data :
- python stock_data_clean.py --source_path <LOCAL_OR_S3_PATH> --dest_path <LOCAL_OR_S3_PATH>
### To calculate metrics :
- python stock_data_calcs.py --source_path <LOCAL_OR_S3_PATH> --dest_path <LOCAL_OR_S3_PATH>

## NOTES:
- see [yfinance](https://github.com/ranaroussi/yfinance) docs for general info on using the module
- see [Ticker class](https://github.com/ranaroussi/yfinance/wiki/Ticker#interface) for valid values for period arg above
- S3 paths seem to be recognized and credentials picked up automagically using the s3fs module
  - assuming you have credentials set up in ~/.aws

## Running cleaning/calcs scripts as lambdas
### The Lambda version of the code is in the lambdas directory\
### In addition to this code you will need to :

- create a trigger for each lambda :
  - service : S3
  - event type : All object create events
  - bucket : your source data bucket (I use sdt-stock-data)
  - prefix : any subfolders (I use bronze/ and silver/ for my clean and calcs lambdas)
  - this will automatically add a [resource-based policy](https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html) allowing S3 to invoke your lambda function
- Add a layer
  - I use 'AWSSDKPandas-Python312' which is one of the available options when adding a layer
  - should container any non-core python modules that you'd need
  - in this case we needed awswrangler, numpy, pandas
- Create a Policy to allow the lambda to write to CloudWatch and S3
  - Assign this policy to a role
  - Assign this role to the Lambda
  - Policy would look omething like this:
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
                "arn:aws:s3:::sdt-stock-data",
                "arn:aws:s3:::sdt-stock-data/*"
            ]
        }
    ]
  }
```
- up your timeout (I did a minute, currently they run in 20 seconds or less)


## Future plans:
- BI views, visualization for gold data
    - Multiple metrics at once, nav/price for instance
    - Ability to change timescale as needed
    - Ability to view as percentage growth, div growth vs price growth for instance
    - STD Dev lines
    - Quicksight or tableau?
- More Calculations/Features
    - stock technical indicators (maybe : https://github.com/ta-lib/ta-lib-python)
    - CEF NAV discount for various time periods
    - update 1 yr, 5 yr, overall calcs for each and store somewhere
    - Historical CAPE, VIX, etc
    - Historical PE for individual stocks
    - Overall gains for a period taking divs into account
- Store silver/gold data in database?
    - point BI tool here
- Alerts
    - stock goes above/below moving avg
    - CEF nav discount above/below 1 year, multi-year, all-time average 
    - other tech indicator thresholds
    - email, sms?
- Auto update
    - daily pull of individual metrics for each stock
    - write to central store
    - recheck/trigger alerts
- Dashboard or api lookup for current snapshot view of stock calcs
    (current discount, pe, relation to 50/200 day avg and other indicators, etc)
- Observations by the hour/minute
  - stream in, check alerts
- Containerize and automate with AWS batch, if load increases or maybe just for learning's sake
- DuckDB, Pyspark, ??? for silver -> gold transform if pandas can't handle the load
- LSTM predictive model