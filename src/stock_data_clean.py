import argparse as ap
import logging
import pandas as pd
import utils
import numpy as np


def clean_stock_data(input_path: str, output_path:str):
    """
    convert dates, rename cols, fill divs

    :return: None
    """

    symbol = utils.get_symbol_from_full_path(input_path)
    period = utils.get_period_from_full_path(input_path)

    stock_df = pd.read_parquet(input_path, columns=['Dividends', 'Close', 'Volume'])
    logger.info(f'{stock_df.dtypes=}')
    logger.info(f'{stock_df.index=}')
    logger.info(f'{stock_df.head()=}')
    logger.info(f'{stock_df.columns=}')

    # Converting the original datetime to just a date.
    # For now there is no need for a timestamp, just a date
    stock_df.index = pd.to_datetime(stock_df.index.strftime('%Y-%m-%d'))

    # rename cols
    stock_df.rename(mapper=str.lower, axis='columns', inplace=True)
    #
    # # fill dividends to be the most recent distribution
    # stock_df.loc[stock_df['dividends'] == 0, ['dividends']] = np.nan
    # stock_df['dividends_filled'] = stock_df['dividends'].ffill(inplace=False)
    # stock_df['dividends_filled'] = stock_df['dividends'].bfill(inplace=False)
    #
    # price_full_output_path = f"{output_path}/{symbol}_{period}_closing_data_cleaned.parquet"
    # logger.info(f'writing closing price data to {price_full_output_path}')
    # stock_df.to_parquet(price_full_output_path)


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

    clean_stock_data(source_path, dest_path)