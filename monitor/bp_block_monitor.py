#!/usr/bin/env python
# -*- coding: utf-8 -*

import time

import init_work_home

init_work_home.init()
from config.config import Config
from utils import http
from utils.logger import logger
from utils.notify import Notify

api = Config.get_local_api()
bp_name = Config.get_bp_account()

max_check_period = 150
interval = 20
block_interval = 12
bp_produce_block_count = 12


def log(msg):
    logger.info('%s %s', bp_name, msg)


def notify(msg):
    log(msg)
    Notify.notify_error(bp_name, msg)


def get_block_num():
    get_info_api = api + '/v1/chain/get_info'
    response = http.get(get_info_api, get_info_api)
    return response.json()['head_block_num']


def get_unpaid_block():
    unpaid_blocks = None
    producers_api = api + '/v1/chain/get_producers'
    response = http.post(producers_api, producers_api, data='{"json":true,"limit":21}')
    for data in response.json()['rows']:
        if data['owner'] == bp_name:
            unpaid_blocks = int(data['unpaid_blocks'])
            break
    return unpaid_blocks


def get_last_unpaid_blocks():
    last_unpaid_blocks = 0
    last_date = time.time()
    head_num = get_block_num()
    while True:
        unpaid_blocks = get_unpaid_block()
        if unpaid_blocks is None:
            log('not in top21')
            unpaid_blocks = None
            break
        if unpaid_blocks != last_unpaid_blocks:
            if last_unpaid_blocks != 0:
                time.sleep(block_interval)
                unpaid_blocks = get_unpaid_block()
                head_num = get_block_num()
                break
            last_unpaid_blocks = unpaid_blocks
            last_date = time.time()
            time.sleep(1)
        else:
            delta = time.time() - last_date
            if delta > max_check_period:
                notify('not producing for too long after %s' % head_num)
                unpaid_blocks = None
                break
            else:
                time.sleep(interval)
    return head_num, unpaid_blocks


def check_bp_produce():
    last_head_num, last_unpaid_blocks = get_last_unpaid_blocks()
    if last_unpaid_blocks is not None:
        head_num, unpaid_blocks = get_last_unpaid_blocks()
        produce_blocks = unpaid_blocks - last_unpaid_blocks
        if produce_blocks == bp_produce_block_count:
            log("produced check success, [%s, %s] unpaid_last:%s unpaid_now:%s" %
                (last_head_num, head_num, last_unpaid_blocks, unpaid_blocks))
        elif produce_blocks < 0:
            notify("maybe claim now, [%s, %s] unpaid_last:%s unpaid_now:%s" %
                   (last_head_num, head_num, last_unpaid_blocks, unpaid_blocks))
        else:
            notify("produced check failed, [%s, %s] missed %s" %
                   (last_head_num, head_num, (bp_produce_block_count - produce_blocks)))


def main():
    check_bp_produce()


if __name__ == '__main__':
    main()
