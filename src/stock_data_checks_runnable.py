import stock_data_functions as sdf
import rds_functions as rf
import logging
import os
from dotenv import load_dotenv
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Load the environment variables from the .env file
load_dotenv()

# rds settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_host = os.environ['RDS_HOST']
db_name = os.environ['DB_NAME']

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--stock', required=True, help='Stock symbol to get discount for')
    args = parser.parse_args()

    stock = args.stock
    prem_disc = sdf.get_current_cef_discount(stock)
    stock_info = rf.get_metrics_by_stock(stock, user_name, password, rds_host, db_name)

    logger.info(f'{prem_disc=}')
    logger.info(f'{stock_info=}')

    if prem_disc: 
        if stock_info:
            if prem_disc < 0 and stock_info['nav_discount_avg_1y'] > prem_disc:
                logger.info(f'Discount for {stock} of {prem_disc} has exceeded its 1 year average of {stock_info['nav_discount_avg_1y']}')
            if prem_disc < 0 and stock_info['nav_discount_avg_alltime'] > prem_disc:
                logger.info(f'Discount for {stock} of {prem_disc} has exceeded its 1 year average of {stock_info['nav_discount_avg_alltime']}')
        else:
            logger.error(f'Error getting stock info for {stock}')
    else:
        logger.error(f'Error getting premium/discount for {stock}')

if __name__ == "__main__":
    main()
