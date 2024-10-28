import json
import logging
from urllib.parse import unquote_plus
from stock_data_calcs import calculate_stock_metrics
from utils import get_symbol_from_full_path

logger = logging.getLogger()
logger.setLevel("INFO")


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

        calculate_stock_metrics(input_path, output_path, logger)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":f"Successfuly saved stock metrics data for ${get_symbol_from_full_path(input_path)}"
        }
    except Exception as e:
        logger.info(e)
        logger.info(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e

