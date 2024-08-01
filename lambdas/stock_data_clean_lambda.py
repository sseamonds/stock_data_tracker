import json
import os
import logging
import pandas as pd
import awswrangler as wr
from urllib.parse import unquote_plus
import numpy as np

logger = logging.getLogger()
logger.setLevel("INFO")


def get_symbol_from_full_path(full_path: str) -> str:
    path_elements = os.path.split(full_path)
    file_name_split = path_elements[len(path_elements) - 1].split("_")

    return file_name_split[0]


def get_period_from_full_path(full_path: str) -> str:
    path_elements = os.path.split(full_path)
    file_name_split = path_elements[len(path_elements) - 1].split("_")

    return file_name_split[1]


def clean_stock_data(input_path: str, output_path: str):
    """
    convert dates, rename cols, fill divs

    :return: None
    """
    symbol = get_symbol_from_full_path(input_path)
    period = get_period_from_full_path(input_path)

    stock_df = wr.s3.read_parquet(input_path)
    stock_df.drop(columns=['Capital Gains', 'High', 'Low', 'Open', 'Stock Splits'], inplace=True)

    # Converting the original datetime to just a date.
    # For now there is no need for a timestamp, just a date
    stock_df.index = pd.to_datetime(stock_df.index.strftime('%Y-%m-%d'))

    # rename cols
    stock_df.rename(mapper=str.lower, axis='columns', inplace=True)

    # fill dividends to be the most recent distribution
    stock_df.loc[stock_df['dividends'] == 0, ['dividends']] = np.nan
    stock_df['dividends_filled'] = stock_df['dividends'].ffill(inplace=False)
    stock_df['dividends_filled'] = stock_df['dividends'].bfill(inplace=False)

    price_full_output_path = f"{output_path}/{symbol}_{period}_closing_data_cleaned.parquet"
    response = wr.s3.to_parquet(stock_df, path=price_full_output_path, index=True)
    logger.info(f'stock metrics data written to to {response['paths']}')


def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    logger.info(f'{bucket=}')
    key = unquote_plus(record['s3']['object']['key'])
    logger.info(f'{key=}')

    try:
        dest_folder = "silver"

        output_path = f"s3://{bucket}/{dest_folder}"
        logger.info(f'{output_path=}')
        input_path = f's3://{bucket}/{key}'
        logger.info(f'{input_path=}')

        clean_stock_data(input_path, output_path)
    except Exception as e:
        logger.info(e)
        logger.info(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e