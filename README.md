# stock_data_tracker
Simple data eng project to practice some AWS flows using stock ticker data.

## Current State:
- Code for pulling, cleaning, and calculating a couple basic metrics for a stock ticker
- Can persist data to local or existing S3 buckets. I follow the bronze/silver/gold paradigm 
- Persisting latest agg metrics for a stock to RDS
- Checking current nav discount against agg metrics
  - for instance, checking if the current NAV discount is lower than the yearly average NAV discount
  - can run manually or schedule in say EventBridge and pass a stock symbol to check
- IN PROGRESS : Writing historical price/nav and historical metrics to postgres.  
  - This will serves as the source for historical price/nav and historical trailing/moving metrics (nav discount, price moving average, etc).  
  - This will be appended to with a daily run and current metrics (latest overall price average, 1 yr moving average, latest div yield, etc) will be recalculated.

### To pull data from Yahoo finance :
- python src/runnable/get_historical_stock_data.py --type [price|nav] --stock_symbol <STOCK_TICKER_ALL_CAPS> --period=<TIME_LENGTH> --output_path <LOCAL_OR_S3_PATH>
  - see NOTES below on period param
  - Example for CEF
    - python src/get_historical_stock_data.py --type price --stock_symbol AWF --period=1y --output_path s3://sdt-stock-data/bronze/cef
    - python src/get_historical_stock_data.py --type nav --stock_symbol XAWFX --period=1y --output_path s3://sdt-stock-data/bronze/cef
    - pulls price AND nav separately which will be merged in cleaning process
  - Example for stock
    - python src/get_historical_stock_data.py --type price --stock_symbol VOO --period=1y --output_path s3://sdt-stock-data/bronze/stock
  - output_path should be of format <s3_bronze_path>/cef for CEFs and <s3_bronze_path>/stock for stocks

### To clean data :
- python clean_stock_data_runnable.py --source_path <LOCAL_OR_S3_PATH> --output_path <LOCAL_OR_S3_PATH>
  - Lambda trigger should be set to <s3_bronze_path>/cef for CEFs and <s3_bronze_path>/stock for stocks

### To calculate metrics :
- python save_stock_data_calcs_runnable.py --source_path <LOCAL_OR_S3_PATH> --output_path <LOCAL_OR_S3_PATH>
- Lambda trigger should be set to <s3_silver_path>

### To Query/Insert stock metrics into RDS locally (can simply use a local postgres for testing instead):
1. RDS instance must be on a subnet group with public subnets.
- NOTE: If the RDS instance was created on a private subnet group, this cannot be changed after the fact and you'd need to create a new instance or new VPC (with public subnets) and switch to that!!! There are other ways too documented in the knowledge-center link below
2. Need a security group attached to the RDS instance which allows inbound Postgres/TCP/5432 access from your IP
3. RDS's VPC must have an internet gateway
4. route table has entry for destination : 0.0.0.0/0 and target <internet gateway attached to your VPC>
see:
	- https://repost.aws/knowledge-center/rds-connectivity-instance-subnet-vpc
	- https://medium.com/overlander/connecting-to-rds-from-local-over-tcp-operation-timed-out-5cfc819f402c


## NOTES:
- See docs/stock_tracker_overview.drawio.png for overall flow
  - docs/stock_tracker_overview.drawio is the source, created via free giaram tool at: [draw.io](https://app.diagrams.net/)
- see [yfinance](https://github.com/ranaroussi/yfinance) docs for general info on using the module
  - see [Ticker class](https://github.com/ranaroussi/yfinance/wiki/Ticker#interface) for valid values for period arg above
- *_runnable.py files are for local runs and and can operate on local dirs and postgres instance for testing. Each should have a corresponding lambdas/*.py file for running as lamndas in AWS
- for nav data for CEF's, we call yfinance with and 'X' on both sides of the ticker
  - eg : XDSLX, XAWFX
  - this will cause the NAV (net asset value) to be populated in the 'Close' field and is how we get NAV data for CEF's
  - pricing and nav data go to separate prefixes named 'price' and 'nav'
- S3 paths seem to be recognized and credentials picked up automagically having the s3fs module installed
  - assuming you have credentials set up in ~/.aws in a default profile
- The scripts dir has json files which can be used to manually trigger lambdas
  - for instance, instead of having a lambda trigger on a file upload, you can simulate it using bronze_bucket_event.json (assuming the file in reference is actually there)
- When running code loclly which talks to postgres you'll need to set up USER_NAME, RDS_HOST (set to localhost), and DB_NAME env vars in a .env file

## Running cleaning/calcs scripts as lambdas:
#### The Lambda version of the code is in the lambdas directory
#### Setting up with S3-based triggers for lambdas will cause the cleaning and calcs scripts to run when you put a new raw stock file in the s3://<base_bucket>/bronze/ folder. 
- This can be done manually OR via get_historical_stock_data.py as described above but with an S3 destination
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
- Add a layer for awswrangler/pandas (if a lambda operates on parquet data in S3, or if lambda imports pandas/numpy (which rds_functions.py does...))
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
- For the lambda to write to RDS (and consume from S3):
  - Setup RDS:
    - create an instance
    - connect to an EC2 instance to perform psql actions
    - connect to the lambda described below
    - create table using sql/create_stock_tables.sql
  - Setup the Lambda
    - use lambdas/stock_metrics_lambda.py
    - upload utils.py, rds_functions.py, and stock_metrics.py
    - run the scripts/build_psycopg2_sqlalchemy_layer.sh to generate a psycopg/sqlalchemy layer in the form of a zip file 
    - add the psycopg2-layer.zip as a layer and attach to the lambda
    - attach to the same VPC as the RDS instance
    - setup a VPC endpoint for S3 access (https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html)
      - SEE : https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html
	    - type : AWS services
	    - Service Name : com.amazonaws.us-west-2.s3
		    - or similar name depending on your region
		    - Type : pick the gateway option
	    - VPC : same VPC that Lambda is attached to already
	    - Policy : Full access, or define your own more granular VP endpoint policy
      - Post creation : Go to VPC Endpoints, pick the one you just created, and add a VPC route table (I already had a private one for RDS, and used that one)
    - ensure the right security groups are attached with the VPC
      - for me it was the SG for the rds instance (generated when adding a Lambda to the RDS instance, named something like "lambda-rds-1")
      - if the Lambda also consumes from S3 you need the default SG as well.  A Lambda doesn't normally need this for S3 access, but one with a VPC attached does need it
- For the lambdas that invoke other lambdas :
  - pass a payload of format :
  {
    "Records": [
      {
          "var": var_val
          ....etc....
      }
    ]
  }
  - call next lambda by it's arn
  - set up an interface VPC endpoint for lambda in desired region
    - see instructions for SNS under "To log alerts to SNS...". Key difference is that you will choose the option AWS Service, and enter lambda, then choose lambda.<region> (mine is com.amazonaws.us-west-2.lambda for instance)
- For lambdas which hit yfinance
  - use scripts/build_yfinance_layer.sh to build a yfinance layer
  - add the layer to the lambda
  - note that the zip for a layer should have "python/lib/python3.6/site-packages" as it's base dir
  - I've separated the lambda which hits yfinance from others which operate on S3 as it needs internet access and the others are operating internally to AWS
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
- for CEFs, cef_data_clean_lambda.py is designed to only run when both price and nav files exist. it will clean and merge them
## Dockerization of Lambdas:
Capability has been added for and tested on one lambda, lambdas/cef_data_clean_lambdas.py.  
I might in the future do this for the remaining lambdas. 
- For now the Dockerfile is for cef_data_clean_lambda.py, though it would be easy to adjust for any other lambda by running COPY for the desired lambda file and all related dependencies
- Ideally we could genericize the process to run for any (or all?) local lambda without having to customize the Dockerfile
### To build and run the docker image locally:
- From the base directory build the docker image :
  - `docker build --no-cache --platform linux/amd64 -t cef-clean-image:test .`
    - `--platform linux/amd64` is necessary for Mac environments
      - you will likely get an "invalid entrypoint" error if this is left out, on local and on AWS
- Start the lambda as a container locally:
  - see : https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-base
  - run container pulling creds ENV vars from local .aws/credentials file :
	- `docker run --mount type=bind,source=$HOME/.aws/credentials,target=/root/.aws/credentials  -e AWS_REGION=us-west-2 --platform linux/amd64 -p 9000:8080 cef-clean-image:test`
- test the lambda by hitting it as a service with a payload :
  - `curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d "{\"Records\": [{\"s3\": {\"bucket\": {\"name\": \"sdt-stock-data\"},\"object\": {\"key\": \"bronze/cef/nav//AWF_1y.parquet\"}}}]}"`
### Building and pushing to ECR:
1. get ECR login password:
`aws ecr get-login-password --region <region_where_lambda_exists> | docker login --username AWS --password-stdin <your_account_number>.dkr.ecr.<your_region>.amazonaws.com`
  - Should see "Login Succeeded" in console
[OPTIONAL] Create repo if you haven't already (in AWS console or via this command):
`aws ecr create-repository --repository-name <repo_namespace>/<repo_name> --region <lambdas_region> --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE`
2. build your docker image (if already built for local testing above, skip this step):
NOTE: for MAC you need the "--platform linux/amd64" flag, if building on linux you will not need it
docker build --platform linux/amd64 -t sdt/cef_data_clean_lambda .
3. tag your image :
docker tag sdt/cef_data_clean_lambda:latest <your_account_number>.dkr.ecr.<your_region>.amazonaws.com/<repo_namespace>/<repo_name>:latest
  - using tag 'latest' will make this build the latest, erasing tags of the previous image.  You can instead use a numbering or versioning scheme to keep each new build's tag unique
4. push docker image to ECR:
docker push <your_account_number>.dkr.ecr.<your_region>.amazonaws.com/<repo_namespace>/<repo_name>:latest
5. Check your ECR repo for this image
6. test the lambda in AWS with a payload like the one for the local test above
### To schedule daily checks
- EventBridge Rule, schedule type, with cron format something like : 0 22 ? * 2-6 *
- target lambda : current_stock_metrics
- pass message to current_stock_metrics lambda of format:
		{"Records": [{"stock": "AWF"}]}
- current_stock_metrics which will get the current nav/price and send the premium/discount to the cef_metrics_check lambda
- cef_metrics_check will log to CloudWatch if values exceed values from RDS
### To log alerts to SNS for cef_metrics_check lambda :
1. create security group allowing all inbound access for VPC CIDR (if doesn't exist)
2. New VPC Endpoint for SNS (necessary for a Lambda which is in a VPC as cef_metrics_check is)
	- pick same VPC lambda is in
	- pick 'AWS Services' and SNS url in desired region (for example : sns.us-west-2.amazonaws.com)
	- Security Groups : attach SG from step 1
	- subnets : at least one private subnet in the same VPC as the lambda
	- Endpoint type will be 'Interface' by default
3. Create Security group which allows HTTP traffic from VPC CIDR as well
	- attach to Lambda
3. associate default security group to endpoint
4. SNS access policy added to lambda role
5. set ALERT_MODE to 'SNS' to publish to SNS and enter a topic arn for the SNS_TOPIC env var

## Future plans/ideas:
- BI views, visualization for gold data
  - Multiple metrics at once, nav/price for instance
  - Ability to change timescale as needed
  - Ability to view as percentage growth, div growth vs price growth for instance
  - STD Dev lines
  - Quicksight or tableau? Athena?
- Stock metadata store
  - type : stock, bond, CEF
  - average NAV all-time
  - average div yield all-time
  - div schedule, used to properly calculate yield
  - last updated date for the above
- More Calculations/Features
    - stock technical indicators (maybe : https://github.com/ta-lib/ta-lib-python)
    - full logic for calculating div yield
    - update 1 yr, 5 yr, overall calcs for each and store somewhere
    - Global indicators, M2, CAPE, VIX, etc for comparison against individual stocks
    - Historical PE ratio for individual stocks (would like to know if PE drops below it's 1yr, all time avg)
    - Overall gains for a period taking divs into account
- Auto update
    - daily pull of individual metrics for each stock
    - write to central store
    - recheck/trigger alerts
- Dashboard or on-demand api lookup for current snapshot view of stock calcs for a symbol:
  - current discount, current PE, 50/200 day avg price in relation to current price, etc
- Observations by the hour/minute
  - stream in, recheck alerts
- LSTM predictive model