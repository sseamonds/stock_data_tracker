'''Stock level metrics such as all time discount average, 1 year discount average, etc. 
are calculated and saved to RDS.'''

import json
import logging
import os
import awswrangler as wr
from urllib.parse import unquote_plus
from utils import get_symbol_from_full_path
from rds_functions import upsert_stock_metrics
from stock_metrics import get_nav_metrics_from_df

# Configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    logger.debug("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    logger.debug(f'{bucket=}')
    key = unquote_plus(record['s3']['object']['key'])
    logger.debug(f'{key=}')

    try:
        input_path = f's3://{bucket}/{key}'
        logger.info(f'{input_path=}')
        symbol = get_symbol_from_full_path(input_path)
        
        calc_df = wr.s3.read_parquet(input_path)
    
        # differentiate transformations based on the type of data
        if key.find('cef') != -1:
            # Persist summary metrics to RDS
            user_name = os.environ['USER_NAME']
            password = os.environ['PASSWORD']
            rds_host = os.environ['RDS_HOST']
            db_name = os.environ['DB_NAME']

            nav_discount_avg_1y, nav_discount_avg_alltime = get_nav_metrics_from_df(calc_df)

            insert_return_value = upsert_stock_metrics(symbol, nav_discount_avg_1y, nav_discount_avg_alltime, 
                                 user_name, password, rds_host, db_name) 
            if insert_return_value:
                logger.info(f'inserted stock metrics data for {symbol}')
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json"
                        },
                        "body":f"Successfuly saved stock metrics data for ${symbol}"
                    }
            else:
                logger.error(f'Failed to insert stock metrics data for {symbol}')
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json"
                        },
                        "body":f"Successfuly saved stock metrics data for ${symbol}"
                    }
        else:
            # eventually we'll support stock path, but not now
            raise ValueError(f"Invalid path format: {key}")
    except Exception as e:
        logger.info(f"An exception occurred generating calculations for stock data: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":f"An exception occurred generating calculations for stock data: {e}"
        }

