'''
Runnable for getting current stock data from yfinance and checking the premium/discount 
against the 1 year and all time averages in the RDS database
Will be split into two for Lambda runs
'''
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
import argparse
from current_stock_metrics import check_current_cef_discount
from stock_data_functions import get_current_cef_discount

# configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# postgres settings
db_params = {'rds_host': os.environ['RDS_HOST'], 
            'user_name': os.environ['USER_NAME'], 
            'password': os.getenv('PASSWORD', None), 
            'db_name': os.environ['DB_NAME']}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--symbol', required=True, help='Stock symbol to get discount for')
    args = parser.parse_args()
    symbol = args.symbol

    curr_disc = get_current_cef_discount(symbol)

    if curr_disc:
        logger.info(f'Current discount for {symbol} is {curr_disc}')
        check_current_cef_discount(symbol, curr_disc, db_params=db_params)
    else:
        logger.error(f'Error getting discount for {symbol}')
