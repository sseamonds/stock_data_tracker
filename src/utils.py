import configparser
import sys
import os


def get_symbol_from_full_path(full_path: str) -> str:
    path_elements = os.path.split(full_path)
    file_name_split = path_elements[len(path_elements) - 1].split("_")

    return file_name_split[0]


def get_period_from_full_path(full_path: str) -> str:
    path_elements = os.path.split(full_path)
    file_name_split = path_elements[len(path_elements) - 1].split("_")

    return file_name_split[1]


def get_aws_credentials(aws_profile='default'):
    """
    Gets the aws credentials from ~/.aws/credentials for aws_profile arg
    """
    # the global variables where we store the aws credentials
    global aws_access_key_id
    global aws_secret_access_key

    # parse the aws credentials file
    path = os.environ['HOME'] + '/.aws/credentials'
    config = configparser.ConfigParser()
    config.read(path)

    # read in the aws_access_key_id and the aws_secret_access_key
    # if the profile does not exist, error and exit
    if aws_profile in config.sections():
        aws_access_key_id = config[aws_profile]['aws_access_key_id']
        aws_secret_access_key = config[aws_profile]['aws_secret_access_key']
    else:
        print("Cannot find profile '{}' in {}".format(aws_profile, path), True)
        sys.exit()

    # if we don't have both the access and secret key, error and exit
    if aws_access_key_id is None or aws_secret_access_key is None:
        print("AWS config values not set in '{}' in {}".format(aws_profile, path), True)
        sys.exit()