"""Get historical stock data from DB, 
calculate daily moving metrics and save to DB
"""
import json
import logging
import os
import boto3
from stock_data_calcs import calculate_cef_metrics
from rds_functions import get_stock_history, save_stock_metrics_history

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
    logger.info("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    symbol = record['symbol']
#    type = record['type']

    try:
        logger.info(f'{symbol=}')
        df = get_stock_history(symbol, db_params)
        logger.info(f'{df=}')

        # differentiate transformations based on the type of data
#       if type == 'cef' != -1:
        calc_df = calculate_cef_metrics(df)
        logger.info(f'{calc_df=}')
        # else:
        #     calc_df = calculate_stock_metrics(df)

        logger.info(f'writing stock calculations data to stock_metrics_history table')
        success = save_stock_metrics_history(calc_df, db_params)

        if success: 
            next_lambda = 'arn:aws:lambda:us-west-2:043309363436:function:agg_metrics_to_rds'
            # Trigger current stock metrics lambda
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
                "body":f"Successfuly saved stock metrics data for ${symbol}"
            }
        else:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body":f"Error saving stock metrics data for ${symbol}"
            }
    except Exception as e:
        logger.info(f"An exception occurred generating calculations for stock data: {e}")
        raise e
