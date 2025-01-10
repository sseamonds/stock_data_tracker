import argparse as ap
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from stock_data_calcs import calculate_cef_metrics
from utils import get_period_from_full_path
from rds_functions import get_stock_history, save_stock_metrics_history
from dotenv import load_dotenv

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
            'password': os.getenv('PASSWORD',None), 
            'db_name': os.environ['DB_NAME']}

def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--symbol", type=str, required=True)
    parser.add_argument("--type", type=str, choices=['stock', 'cef'], 
                        default='stock', required=False)
    
    params = vars(parser.parse_args())

    return params


if __name__ == "__main__":
    args = parse_arg()
    type = args['type']
    symbol = args['symbol']
    
    if type == 'cef':
        df = get_stock_history(symbol, db_params)
        logger.info(f'after get_stock_history {df.columns=}')
        logger.info(f'after get_stock_history :\n{df=}')

        calc_df = calculate_cef_metrics(df)
        success = save_stock_metrics_history(calc_df, db_params)

        if success:
            logger.info(f'CEF metrics data saved to postgres for symbol {symbol}')
        else:
            logger.error(f'Error saving CEF metrics data to postgres for symbol {symbol}')
    else:
        logger.error(f'Invalid type: {type}')
        pass # we will add stock metrics later
