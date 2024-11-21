import argparse as ap
import logging
import pandas as pd
from utils import get_symbol_from_full_path, get_period_from_full_path, get_prefix_from_full_path
from stock_data_clean import clean_price_data, clean_cef_data


def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--input_path2", type=str)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--type", type=str, choices=['price', 'nav', 'hist'], required=True)

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
    
    if type == 'nav':
        input_path2 = args['input_path2']
        df2 = pd.read_parquet(input_path2)
        df_cleaned = clean_cef_data(df, df2)
    else:
        df_cleaned = clean_price_data(df)

    symbol = get_symbol_from_full_path(input_path)
    period = get_period_from_full_path(input_path)
    logger.info(f'{input_path=}')
    logger.info(f'{period=}')
    logger.info(f'{symbol=}')
    full_output_path = f"{output_path}/{type}/{symbol}_{period}_cleaned.parquet"
    
    logger.info(f'writing cleaned data to {full_output_path}')

    df_cleaned.to_parquet(full_output_path, index=True)
