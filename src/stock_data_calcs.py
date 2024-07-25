import argparse as ap
import logging
import pandas as pd
import utils
import numpy as np


def calculate_stock_metrics(input_path: str, output_path: str):
    """
    Calculate and persist metrics.

    :return: None
    """

    symbol = utils.get_symbol_from_full_path(input_path)
    period = utils.get_period_from_full_path(input_path)

    stock_df = pd.read_parquet(input_path, columns=['dividends_filled', 'close'])

    # 20, 60, 200 day moving averages
    stock_df['moving_avg_20'] = np.round(stock_df['close'].rolling(20, min_periods=10).mean(), 2)
    stock_df['moving_avg_60'] = np.round(stock_df['close'].rolling(60, min_periods=50).mean(), 2)
    stock_df['moving_avg_200'] = np.round(stock_df['close'].rolling(200, min_periods=180).mean(), 2)

    # running div yield
    div_multiplier = 4  # in the future, this will be calculated based on distribution schedule or provided as an arg
    stock_df['div_yield_rolling'] = np.round(stock_df['dividends_filled'].div(stock_df['close']) * div_multiplier, 4)

    stock_df_full_output_path = f"{output_path}/{symbol}_{period}_stock_metrics.parquet"
    logger.info(f'writing stock metrics data to {stock_df_full_output_path}')
    stock_df.to_parquet(stock_df_full_output_path)


def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--source_path", type=str, required=True)
    parser.add_argument("--dest_path", type=str, required=True)

    params = vars(parser.parse_args())

    return params


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    args = parse_arg()
    source_path = args['source_path']
    dest_path = args['dest_path']

    calculate_stock_metrics(source_path, dest_path)