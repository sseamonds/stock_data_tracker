"""populate current_stock_metrics table with summary metrics 
from stock_metrics_history table"""
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from current_stock_metrics import get_current_nav_metrics_from_df
from rds_functions import save_current_stock_metrics, get_stock_metrics_history
from dotenv import load_dotenv
import argparse as ap

# configure logging
default_log_args = {
    "level": logging.DEBUG,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)

# get .env variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# postgres settings
db_params = {'rds_host': os.environ['RDS_HOST'], 
            'user_name': os.environ['USER_NAME'], 
            'password': os.getenv('PASSWORD',None), 
            'db_name': os.environ['DB_NAME']}


def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()
    parser.add_argument("--symbol", type=str, required=True)
    params = vars(parser.parse_args())

    return params


if __name__ == '__main__':
    symbol = parse_arg()['symbol']

    calc_df = get_stock_metrics_history(symbol, db_params)
    logger.debug(f'{calc_df=}')

    nav_discount_premium_avg_1yr, nav_discount_premium_avg_max = get_current_nav_metrics_from_df(calc_df)
    logger.debug(f'{nav_discount_premium_avg_1yr=}, {nav_discount_premium_avg_max=}')

    insert_return_value = save_current_stock_metrics(symbol, 
                                                       nav_discount_premium_avg_1yr, 
                                                       nav_discount_premium_avg_max, 
                                                       db_params) 
    if insert_return_value:
        logger.info(f'inserted stock metrics data for {symbol}')
