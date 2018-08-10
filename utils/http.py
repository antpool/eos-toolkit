import requests

from logger import logger

def_headers = {'Content-Type': 'application/json'}


def get(action, url, params=None, timeout=3.0, log=False):
    try:
        response = requests.get(url, params=params, timeout=timeout)
        record_response(action, response, log)
        return response
    except Exception as e:
        logger.error("%s get exception:%s", action, e)
        raise e


def post(action, url, headers=None, timeout=3.0, data=None, params=None, log=False):
    try:
        response = requests.post(url, data=data, params=params, headers=headers, timeout=timeout)
        record_response(action, response, log)
        return response
    except Exception as e:
        logger.error("%s post exception:%s", action, e)
        raise e


def record_response(action, response, log=False):
    result = 'success'
    if log:
        result = response.json()
    logger.info("%s: %s", action, result)
