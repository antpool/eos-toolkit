import requests

from logger import logger

def_headers = {'Content-Type': 'application/json'}


def get(action, url, params=None, timeout=3.0, record_response=False):
    response = requests.get(url, params=params, timeout=timeout)
    check_and_record(action, response, record_response)
    return response


def post(action, url, headers=None, timeout=3.0, data=None, params=None, record_response=False):
    response = requests.post(url, data=data, params=params, headers=headers, timeout=timeout)
    check_and_record(action, response, record_response)
    return response


def check_and_record(action, response, record):
    if response.status_code != 200:
        raise Exception(response.text)
    if record:
        logger.info("%s: %s", action, response.json())
