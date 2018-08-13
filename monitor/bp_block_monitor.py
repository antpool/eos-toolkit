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
block_interval = 8
all_block_interval = 130


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


def get_last_unpaid_blocks():
    last_unpaid_blocks = 0
    last_date = time.time()
    while True:
        unpaid_blocks = get_unpaid_block()
        if unpaid_blocks is None:
            log('not in top21')
            break
        if unpaid_blocks != last_unpaid_blocks:
            if last_unpaid_blocks != 0:
                time.sleep(block_interval)
                unpaid_blocks = get_unpaid_block()
                log('produce check success, unpaid_blocks:%s' % unpaid_blocks)
                return unpaid_blocks
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


def check_bp_block():
    last_unpaid_blocks = get_last_unpaid_blocks()
    if last_unpaid_blocks is not None:
        time.sleep(all_block_interval)
        unpaid_blocks = get_unpaid_block()
        produce_blocks = unpaid_blocks - last_unpaid_blocks
        if produce_blocks == 12:
            log("produce blocks count last:%s, now:%s, success" % (last_unpaid_blocks, unpaid_blocks))
        elif produce_blocks < 0:
            notify("maybe claim now, unpaid_last:%s, unpaid_now:%s" % (last_unpaid_blocks, unpaid_blocks))
        else:
            notify("produced blocks check Failed, %s" % produce_blocks)


if __name__ == '__main__':
    check_bp_block()
