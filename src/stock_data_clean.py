import pandas as pd
import utils
import numpy as np
import awswrangler as wr


def clean_price_data(input_path: str, output_path:str, logger, platform:str='s3'):
    """
    Price and Div data from yahoo.
    Convert dates, rename cols, fill divs

    :return: None
    """
    symbol = utils.get_symbol_from_full_path(input_path)
    period = utils.get_period_from_full_path(input_path)

    if platform == 's3':
        stock_df = wr.s3.read_parquet(input_path)
    else:
        stock_df = pd.read_parquet(input_path)

    stock_df.drop(columns=['Capital Gains', 'High', 'Low', 'Open', 'Stock Splits'], 
                  inplace=True)

    # Converting the original datetime to just a date.
    # For now there is no need for a timestamp, just a date
    stock_df.index = pd.to_datetime(stock_df.index.strftime('%Y-%m-%d'))

    # rename cols
    stock_df.rename(mapper=str.lower, axis='columns', inplace=True)

    # fill dividends to be the most recent distribution
    stock_df.loc[stock_df['dividends'] == 0, ['dividends']] = np.nan
    stock_df['dividends_filled'] = stock_df['dividends'].bfill(inplace=False)
    stock_df['dividends_filled'] = stock_df['dividends_filled'].ffill(inplace=False)
    stock_df.drop(columns=['dividends'], inplace=True)

    price_full_output_path = f"{output_path}/{symbol}_{period}_closing_data_cleaned.parquet"
    logger.info(f'writing closing price data to {price_full_output_path}')
    if platform == 's3':
        response = wr.s3.to_parquet(stock_df, path=price_full_output_path, index=True)
        logger.debug(f'{response=}')
    else:
        stock_df.to_parquet(price_full_output_path, index=True)


def clean_cef_data(input_path: str, output_path:str, logger, input_format='csv',
                   platform:str='s3'):
    """
    CEF data from CEF Connect
    Convert dates, rename cols

    :return: None
    """
    symbol = utils.get_symbol_from_full_path(input_path)
    period = utils.get_period_from_full_path(input_path)

    if platform == 's3':
        if input_format == 'csv':
            df = wr.s3.read_csv(input_path, index_col=0)
            logger.info(f'read_csv: {df.dtypes=}')
            logger.info(f'{df.index=}')
            logger.info(f'{df=}')
        else:
            df = wr.s3.read_parquet(input_path)
            logger.info(f'read_parquet: {df.dtypes=}')
            logger.info(f'{df.index=}')
            logger.info(f'{df=}')
    else:
        if input_format == 'csv':
            df = pd.read_csv(input_path)
            logger.info(f'read_csv: {df.dtypes=}')
            logger.info(f'{df.index=}')
            logger.info(f'{df=}')
        else:
            df = pd.read_parquet(input_path)

    # CEF Connect format has an extra blank column at the end
    # Date is read in as the index automatically
    df.columns = ['Name', 'NAV', 'empty']
    df.drop(columns=['empty', 'Name'], inplace=True)
    df.rename(columns={"NAV": "nav"}, inplace=True)
    df.index = pd.to_datetime(df.index)

    price_full_output_path = f"{output_path}/nav/{symbol}_{period}_nav_data_cleaned.parquet"
    logger.info(f'writing closing price data to {price_full_output_path}')
    
    if platform == 's3':
        logger.info(f'saving df : {df.dtypes=}')
        logger.info(f'{df.index=}')
        logger.info(f'{df=}')
        response = wr.s3.to_parquet(df, path=price_full_output_path, index=True)
        logger.debug(f'{response=}')
    else:
        df.to_parquet(price_full_output_path, index=True)