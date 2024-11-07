import json
import logging
import awswrangler as wr
from urllib.parse import unquote_plus
from stock_data_calcs import calculate_stock_metrics, calculate_cef_metrics
from utils import get_symbol_from_full_path, get_period_from_full_path, get_prefix_from_full_path

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.INFO)


def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    logger.info(f'{bucket=}')
    key = unquote_plus(record['s3']['object']['key'])
    logger.info(f'{key=}')

    try:
        dest_base_folder = "gold"
        input_path = f's3://{bucket}/{key}'
        logger.debug(f'{input_path=}')
        df = wr.s3.read_parquet(input_path)

        # differentiate transformations based on the type of data
        if key.find('nav') != -1:
            calc_df = calculate_cef_metrics(df)
        else:
            calc_df = calculate_stock_metrics(df)

        symbol = get_symbol_from_full_path(input_path)
        period = get_period_from_full_path(input_path)
        sub_prefix = get_prefix_from_full_path(input_path) # type specific subprefix
        output_base_path = f"s3://{bucket}/{dest_base_folder}"
        full_output_path = f"{output_base_path}/{sub_prefix}/{symbol}_{period}_calcs.parquet"
        logger.info(f'writing stock calculations data to {full_output_path}')

        response = wr.s3.to_parquet(calc_df, path=full_output_path, index=True)
        logger.debug(f'{response=}')

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":f"Successfuly saved stock metrics data for ${symbol}"
        }
    except Exception as e:
        logger.info("An exception occurred generating calculations for stock data: ", e)
        raise e

