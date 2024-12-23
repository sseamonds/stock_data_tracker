
import json
import logging
from botocore.exceptions import ClientError
import boto3
import os

# Configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def messages_to_string(messages):
    """could add some better messaging/formatting here"""
    return "\n".join(messages)


def alert(alert_mode, messages):
    '''Send alert messages based on alert_mode'''
    if alert_mode == 'SNS':
        send_email_message("CEF Premium/Discount Alert", messages_to_string(messages))
    else:
        for message in messages:
            logger.info(message)


def send_email_message(subject, email_message):
    '''Send email message to SNS topic'''
    sns_topic_arn = os.environ['SNS_TOPIC']
    # Get the topic resource
    sns_resource = boto3.resource('sns')
    topic = sns_resource.Topic(sns_topic_arn)
    logger.debug(f"Sending email message to sns_topic_arn : {sns_topic_arn}")

    try:
        message = {
            "default": email_message
        }
        response = topic.publish(
            Message=json.dumps(message),
            Subject=subject, 
            MessageStructure="json"
        )
        message_id = response["MessageId"]
        logger.info("Published email message to topic %s.", topic.arn)
    except Exception as e:
        raise(f"Couldn't publish email message to topic {topic.arn}.", e)
    else:
        return message_id