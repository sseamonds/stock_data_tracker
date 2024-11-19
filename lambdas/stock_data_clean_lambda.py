import json
import logging
import awswrangler as wr
from urllib.parse import unquote_plus
from stock_data_clean import clean_price_data
from utils import get_symbol_from_full_path, get_prefix_from_full_path, get_period_from_full_path

# can't do custom logging config in lambda afaik
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
