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


def calculate_stock_metrics(input_path: str, output_path: str):
    """
    Calculate and persist metrics.

    :return: None
    """

    symbol = get_symbol_from_full_path(input_path)
    period = get_period_from_full_path(input_path)

    stock_df = wr.s3.read_parquet(input_path, columns=['dividends_filled', 'close', 'volume', 'Date'])

    logger.info(f'{stock_df.columns=}')
    logger.info(f'{stock_df.dtypes=}')
    logger.info(f'{stock_df.shape=}')

    # 20, 60, 200 day moving averages
    stock_df['moving_avg_20'] = np.round(stock_df['close'].rolling(20, min_periods=10).mean(), 2)
    stock_df['moving_avg_60'] = np.round(stock_df['close'].rolling(60, min_periods=50).mean(), 2)
    stock_df['moving_avg_200'] = np.round(stock_df['close'].rolling(200, min_periods=180).mean(), 2)

    # running div yield
    div_multiplier = 4  # in the future, this will be calculated based on distribution schedule or provided as an arg
    stock_df['div_yield_rolling'] = np.round(stock_df['dividends_filled'].div(stock_df['close']) * div_multiplier, 4)

    full_output_path = f"{output_path}/{symbol}_{period}_stock_metrics.parquet"
    response = wr.s3.to_parquet(stock_df, path=full_output_path, index=True)
    logger.info(f'stock metrics data written to to {response['paths']}')


def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    logger.info(f'{bucket=}')
    key = unquote_plus(record['s3']['object']['key'])
    logger.info(f'{key=}')

    try:
        dest_folder = "gold"

        output_path = f"s3://{bucket}/{dest_folder}"
        logger.info(f'{output_path=}')
        input_path = f's3://{bucket}/{key}'
        logger.info(f'{input_path=}')

        calculate_stock_metrics(input_path, output_path)
    except Exception as e:
        logger.info(e)
        logger.info(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e

