import os
import time
import json
import logging
import awswrangler as wr
from urllib.parse import unquote_plus
from stock_data_clean import clean_price_data
from utils import get_symbol_from_full_path, get_prefix_from_full_path, get_period_from_full_path
from rds_functions import save_stock_history

# Configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)

user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_host = os.environ['RDS_HOST']
db_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    logger.debug("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    logger.debug(f'{bucket=}')
    key = unquote_plus(record['s3']['object']['key'])
    logger.debug(f'{key=}')

    try:
        dest_folder = "silver/stock"
        output_base_path = f"s3://{bucket}/{dest_folder}"
        input_path = f's3://{bucket}/{key}'
        logger.info(f'{input_path=}')

        df = wr.s3.read_parquet(input_path)
        cleaned_df = clean_price_data(df, 'price')

        symbol = get_symbol_from_full_path(input_path)
        period = get_period_from_full_path(input_path)
        sub_prefix = get_prefix_from_full_path(input_path) # type specific subprefix
        full_output_path = f"{output_base_path}/{sub_prefix}/{symbol}_{period}_cleaned.parquet"
        logger.info(f'writing cleaned data to {full_output_path}')

        response = wr.s3.to_parquet(cleaned_df, path=full_output_path, index=True)
        logger.debug(f'{response=}')

        # Insert cleaned data into RDS
        start_time = time.time()
        save_stock_history(df=cleaned_df, symbol=symbol, 
                             db_params={'rds_host': rds_host, 
                                        'user_name': user_name, 
                                        'password': password, 
                                        'db_name': db_name})
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f'upsert_stock_history execution time: {execution_time} seconds')

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":f"Successfuly cleaned stock data for ${symbol}"
        }
    except Exception as e:
        logger.info(f"An exception occurred cleaning stock data: {e}")
        raise e
