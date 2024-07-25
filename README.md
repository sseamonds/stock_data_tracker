# stock_data_tracker
Simple data eng project to practice some AWS flows using stock ticker data.

## Current State:
- code for pulling, cleaning, and calculating a couple basic metrics for a stock ticker
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

## Future plans:
- Automate bronze -> silver (cleaning) and silver -> gold (calculations) processes
    - lambda which detects new files in bronze bucket
      - should work as this is < 15 minutes currently
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