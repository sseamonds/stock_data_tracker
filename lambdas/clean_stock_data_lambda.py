import os
import json
import logging
import awswrangler as wr 
import boto3
from urllib.parse import unquote_plus
from stock_data_clean import clean_cef_data
from rds_functions import save_stock_history
from utils import get_symbol_from_full_path, get_period_from_full_path, get_prefix_from_full_path

# configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)

# postgres settings
db_params = {'rds_host': os.environ['RDS_HOST'], 
            'user_name': os.environ['USER_NAME'], 
            'password': os.environ['PASSWORD'], 
            'db_name': os.environ['DB_NAME']}


def lambda_handler(event, context):
    logger.debug("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    logger.debug(f'{bucket=}')
    key = unquote_plus(record['s3']['object']['key'])
    logger.debug(f'{key=}')

    try:
        dest_folder = "silver/cef"
        output_base_path = f"s3://{bucket}/{dest_folder}"
        input_path = f's3://{bucket}/{key}'
        logger.info(f'{input_path=}')
        
        # Todo : add logic for stock data
        # ensure both source files exist, otherwise do nothing
        if '/price/' in key:
            price_df = wr.s3.read_parquet(input_path)
            cef_nav_path = input_path.replace('/price/', '/nav/')

            if wr.s3.does_object_exist(cef_nav_path):
                nav_df = wr.s3.read_parquet(cef_nav_path)
            else:
                logger.info(f'corresponding nav path: {cef_nav_path} does not exist')
                return {
                    "statusCode": 204,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body":f"Corresponding nav data not found for {key}.  No action taken."  
                }
        elif '/nav/' in key:
            nav_df = wr.s3.read_parquet(input_path)
            cef_price_path = input_path.replace('/nav/', '/price/')

            if wr.s3.does_object_exist(cef_price_path):
                price_df = wr.s3.read_parquet(cef_price_path)
            else:
                logger.info(f'corresponding price path: {cef_price_path} does not exist')
                return {
                    "statusCode": 204,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body":f"Corresponding price data not found for {key}.  No action taken."  
                }
        else:
            logger.error(f'Invalid path format path: {key}')
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body":f"Invalid path format path: {key}.  No action taken."  
            }

        cleaned_df = clean_cef_data(price_df, nav_df)

        symbol = get_symbol_from_full_path(input_path)
        period = get_period_from_full_path(input_path)
        sub_prefix = get_prefix_from_full_path(input_path) # type specific subprefix
        full_output_path = f"{output_base_path}/{sub_prefix}/{symbol}_{period}.parquet"
        logger.info(f'writing cleaned data to {full_output_path}')

        response = wr.s3.to_parquet(cleaned_df, path=full_output_path, index=True)
        logger.debug(f'Done writing cleaned data: {response=}')

        # insert stock history
        save_stock_history(df=cleaned_df, symbol=symbol, db_params=db_params)

        # Trigger data calcs lambda
        next_lambda = 'arn:aws:lambda:us-west-2:043309363436:function:stock_data_calcs'
        lambda_client = boto3.client('lambda')
        payload = {"Records": [{"symbol": symbol}]}
        invoke_response = lambda_client.invoke(
            FunctionName=next_lambda,
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
        logger.debug(f'Triggered lambda {next_lambda} : {invoke_response}')

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":f"Successfuly cleaned stock data for ${symbol}"
        }
    except Exception as e:
        logger.error(f"An exception occurred cleaning stock data: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":f"An exception occurred cleaning stock data: {e}"
        }
