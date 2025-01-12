'''Get current metrics for a cef from yfinance, 
write to SQS queue for further processing'''

import json
import logging
import os
import stock_data_functions as sdf
import boto3

# configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    logger.debug("Received event: " + json.dumps(event, indent=2))

    record = event['Records'][0]
    stock_symbol = record['stock']

    logger.info(f'Checking discount for {stock_symbol}')
    current_premium_discount = sdf.get_current_cef_discount(stock_symbol)
    logger.info(f'Discount for {stock_symbol} is {current_premium_discount}')
    
    if current_premium_discount:
        # Create SQS client
        sqs = boto3.client('sqs')
        # Get the queue URL from environment variables
        queue_url = os.environ['SQS_QUEUE_URL']
        message = {
            'stock_symbol': stock_symbol,
            'current_premium_discount': current_premium_discount
        }

        # Send the message to the SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )

        logger.debug(f'Message sent to SQS queue {queue_url} with response: {response}')
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
                "body":f'{{"Current premium/discount for {stock_symbol} is {current_premium_discount} sent to SQS queue {queue_url}"}}'
            }
    else:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":f'{"Failed to get current metrics for stock {stock_symbol}"}'
        }