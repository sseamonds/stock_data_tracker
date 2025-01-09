'''
Runnable for getting current stock data from yfinance and checking the premium/discount against the 1 year and all time averages in the RDS database
Will be split into two for Lamnda runs
'''
import logging
import os
from dotenv import load_dotenv
import argparse
from stock_metrics import check_current_cef_discount
from stock_data_functions import get_current_cef_discount

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

    curr_disc = get_current_cef_discount(args.stock)
    logger.info(f'Current discount for {args.stock} is {curr_disc}')
    check_current_cef_discount(args.stock, curr_disc, user_name, password, rds_host, db_name)

if __name__ == "__main__":
    main()
