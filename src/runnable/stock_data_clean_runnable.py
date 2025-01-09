import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse as ap
import logging
import pandas as pd
from rds_functions import save_stock_history
from utils import get_symbol_from_full_path, get_period_from_full_path, get_prefix_from_full_path
from stock_data_clean import clean_price_data, clean_cef_data
import time
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# postgres settings
db_params = {'RDS_HOST': os.environ['RDS_HOST'], 
            'USER_NAME': os.environ['USER_NAME'], 
            'PASSWORD': os.getenv('PASSWORD',None), 
            'DB_NAME': os.environ['DB_NAME']}

def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--input_path2", type=str)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--type", type=str, choices=['price', 'nav'], required=True)

    params = vars(parser.parse_args())

    return params


if __name__ == "__main__":
    """
    Local script to run clean stock data
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    args = parse_arg()
    input_path = args['input_path']
    output_path = args['output_path']
    type = args['type']

    df = pd.read_parquet(input_path)
    
    # Here we explicitly pass on the two files to clean and merge
    # In the lambda we look for the matching file based on the symbol/prefix
    if type == 'nav':
        input_path2 = args['input_path2']
        df_nav = pd.read_parquet(input_path2)
        df_cleaned = clean_cef_data(df, df_nav)
    else:
        df_cleaned = clean_price_data(df)

    symbol = get_symbol_from_full_path(input_path)
    period = get_period_from_full_path(input_path)
    full_output_path = f"{output_path}/{type}/{symbol}_{period}_cleaned.parquet"
    
    logger.info(f'writing cleaned data to {full_output_path}')

    # write to file
    df_cleaned.to_parquet(full_output_path, index=True)

    # write to RDS
    start_time = time.time()
    save_stock_history(df=df_cleaned, 
                       symbol=symbol, 
                       db_params=db_params)
    
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f'upsert_stock_history execution time: {execution_time} seconds')
