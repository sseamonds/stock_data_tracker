import json
import logging
import os
from stock_metrics import check_current_cef_discount

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
    logger.info("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    stock_sybol = record['stock']
    current_premium_discount = record['current_premium_discount']
    logger.info(f'Checking discount for {stock_sybol} with current premium/discount of {current_premium_discount}')

    check_current_cef_discount(stock_sybol, current_premium_discount, 
                               user_name, password, rds_host, db_name)

