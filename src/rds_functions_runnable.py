import logging
import os
from dotenv import load_dotenv
import argparse
from rds_functions import insert_stock_metrics, get_metrics_by_stock
import numpy as np
import pandas as pd

# Load the environment variables from the .env file
load_dotenv()

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

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--action', choices=['query', 'insert'], help='Action to perform')
    args = parser.parse_args()
    stock_symbol = args.stock_symbol

    if args.action == 'query':
        logger.info("Performing query action")

        return_val = get_metrics_by_stock(stock_symbol, user_name, password, rds_host, db_name)
        logger.info(f'{return_val=}')
    elif args.action == 'insert':
        logger.info("Performing insert action")

        if not args.input_file:
            logger.error("input_file argument is required for insert action")
            return

        input_file = args.input_file
        calc_df = pd.read_parquet(input_file)
        logger.debug(f'{calc_df=}')
        nav_discount_avg_1y = calc_df.tail(1)['nav_discount_premium_moving_avg_1yr'][0]
        logger.info(f'{nav_discount_avg_1y=}')
        nav_discount_avg_alltime = np.round(calc_df['nav_discount_premium'].mean(), 4)
        logger.info(f'{nav_discount_avg_alltime=}')

        insert_stock_metrics(stock_symbol, nav_discount_avg_1y, nav_discount_avg_alltime, user_name, password, rds_host, db_name)

if __name__ == "__main__":
    main()