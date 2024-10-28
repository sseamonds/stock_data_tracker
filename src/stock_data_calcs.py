import utils
import numpy as np
import awswrangler as wr
import pandas as pd

def calculate_stock_metrics(input_path: str, output_path: str, logger, platform: str = 's3'):
    """
    Calculate and persist metrics.

    :return: None
    """
    symbol = utils.get_symbol_from_full_path(input_path)
    period = utils.get_period_from_full_path(input_path)

    if platform == 's3':
        stock_df = wr.s3.read_parquet(input_path, columns=['dividends_filled', 'close', 'volume', 'Date'])
    else:
        stock_df = pd.read_parquet(input_path)

    # 20, 60, 200 day moving averages
    stock_df['moving_avg_20'] = np.round(stock_df['close'].rolling(20, min_periods=10).mean(), 2)
    stock_df['moving_avg_60'] = np.round(stock_df['close'].rolling(60, min_periods=50).mean(), 2)
    stock_df['moving_avg_200'] = np.round(stock_df['close'].rolling(200, min_periods=180).mean(), 2)

    # running div yield
    div_multiplier = 4  # in the future, this will be calculated based on distribution schedule or provided as an arg
    stock_df['div_yield_rolling'] = np.round(stock_df['dividends_filled'].div(stock_df['close']) * div_multiplier, 4)

    full_output_path = f"{output_path}/{symbol}_{period}_stock_metrics.parquet"
    logger.info(f'writing stock metrics data to {full_output_path}')

    if platform == 's3':
        wr.s3.to_parquet(stock_df, path=full_output_path, index=True)
    else:
        stock_df.to_parquet(full_output_path, index=True)
    