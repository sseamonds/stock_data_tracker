"""Receive current price/metrics for a stock from SQS 
and check the current trailing metrics."""
import json
import logging
import os
from current_stock_metrics import check_current_cef_discount

# configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)

# postgres settings
db_params = {'rds_host': os.environ['RDS_HOST'], 
            'user_name': os.environ['USER_NAME'], 
            'password': os.environ['PASSWORD'], 
            'db_name': os.environ['DB_NAME']}

alert_mode = os.getenv('ALERT_MODE', default = 'LOG')


def lambda_handler(event, context):
    logger.debug("Received event: " + json.dumps(event, indent=2))
    message = json.loads(event['Records'][0]['body'])
    stock_symbol = message['stock_symbol']
    current_premium_discount = message['current_premium_discount']
    logger.debug(f'Checking discount for {stock_symbol} with current premium/discount of {current_premium_discount}.  {alert_mode=}')

    try:
        check_current_cef_discount(stock_symbol, current_premium_discount, 
                                   db_params=db_params,
                                   alert_mode=alert_mode)
    except Exception as e:
        logger.error(f'Error checking discount for {stock_symbol}: {e}')
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "Error"
        }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "Success"
    }