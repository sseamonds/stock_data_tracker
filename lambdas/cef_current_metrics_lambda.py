import json
import logging
import os
import stock_data_functions as sdf

# Configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)

# rds settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_host = os.environ['RDS_HOST']
db_name = os.environ['DB_NAME']


def lambda_handler(event, context):
    '''Get current metrics for a cef'''
    logger.info("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    stock_symbol = record['stock']

    logger.info(f'Checking discount for {stock_symbol}')
    current_premium_discount = sdf.get_current_cef_discount(stock_symbol)
    logger.info(f'Discount for {stock_symbol} is {current_premium_discount}')

    return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "{\"stock\":\"{stock_symbol}\", \"discount\":{current_premium_discount}}"
#            "body":f'{"stock":{stock_symbol}, "discount": {current_premium_discount}}'
        }
    

