#!/usr/bin/env python
# -*- coding: utf-8 -*

import time

import init_work_home

init_work_home.init()
from config.config import Config
from utils import http
from utils.logger import logger
from utils.notify import Notify

api = Config.get_local_api() + '/v1/chain/get_producers'
bp_name = Config.get_bp_account()

max_check_period = 150
interval = 20


def log(msg):
    logger.info('%s %s', bp_name, msg)


def notify(msg):
    log(msg)
    Notify.notify(bp_name, msg)


def get_unpaid_block():
    unpaid_blocks = None
    response = http.post(api, api, data='{"json":true,"limit":21}')
    for data in response.json()['rows']:
        if data['owner'] == bp_name:
            unpaid_blocks = int(data['unpaid_blocks'])
            break
    return unpaid_blocks


def check_bp_produce():
    last_unpaid_blocks = 0
    last_date = time.time()
    while True:
        unpaid_blocks = get_unpaid_block()
        if unpaid_blocks is None:
            log('not in top21')
            break
        if unpaid_blocks != last_unpaid_blocks:
            if last_unpaid_blocks != 0:
                log('produce check success')
                break
            last_unpaid_blocks = unpaid_blocks
            last_date = time.time()
            time.sleep(1)
        else:
            delta = time.time() - last_date
            if delta > max_check_period:
                notify('not producing for too long')
                break
            else:
                log('not currently producing')
                time.sleep(interval)


if __name__ == '__main__':
    check_bp_produce()
