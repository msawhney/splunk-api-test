import logging
import os
import boto3
from botocore.exceptions import ClientError


def get_logger():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)

    debug_level = get_setting('LOG_LEVEL')
    if debug_level is not None:
        if debug_level.upper() == 'DEBUG':
            logger.setLevel(logging.DEBUG)
        elif debug_level.upper() == 'INFO':
            logger.setLevel(logging.INFO)
        elif debug_level.upper() == 'WARN':
            logger.setLevel(logging.WARN)
        elif debug_level.upper() == 'ERROR':
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.INFO)
    return logger


def get_setting(param_name, default='None'):
    """This function looks for an upper case environment variable and then defaults
    to checking the AWS SSM Parameters (lower case)

    Arguments:
        param_name {str} -- Parameter Name

    Keyword Arguments:
        default {str} -- [description] (default: {'None'})
    """

    try:
        value = os.environ.get(param_name.upper())
        if value is None:
            value = get_ssm_parameter(param_name.lower())
            # logging.error(f'Param Name: {param_name} not set in env file')

    except (IndexError, KeyError) as e:
        logging.warn(e)
        value = default

    return value


def get_ssm_parameter(param_name):
    """This functions reads the param_name from AWS SSM service

    Arguments:
        param_name {str} -- Parameter name
    """

    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameters(
            Names=[
                param_name,
            ],
            WithDecryption=True
        )

        # Store the credentials in a variable name
        credentials = response['Parameters'][0]['Value']
        return credentials
    except (IndexError, ClientError) as e:
        logging.warn(f'No AWS SSM Parameter found for {param_name}\n{e}')
        raise
