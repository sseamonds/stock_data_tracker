import argparse as ap
import logging
import pandas as pd
from stock_data_calcs import calculate_stock_metrics, calculate_cef_metrics
from utils import get_symbol_from_full_path, get_period_from_full_path

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.INFO)


def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--input_path2", type=str)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--type", type=str, choices=['price', 'nav'], 
                        default='price', required=False)
    
    params = vars(parser.parse_args())

    return params


if __name__ == "__main__":
    args = parse_arg()
    input_path = args['input_path']
    output_path = args['output_path']
    type = args['type']
    
    if type == 'nav':
        df = pd.read_parquet(input_path)
        calc_df = calculate_cef_metrics(df)
    else:
        df = pd.read_parquet(input_path)
        calc_df = calculate_stock_metrics(df)

    symbol = get_symbol_from_full_path(input_path)
    period = get_period_from_full_path(input_path)
    full_output_path = f"{output_path}/{type}/{symbol}_{period}_calcs.parquet"

    logger.info(f'writing metrics data to {full_output_path}')
    calc_df.to_parquet(full_output_path, index=True)
