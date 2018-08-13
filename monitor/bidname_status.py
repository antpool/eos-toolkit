#!/usr/bin/env python
# -*- coding: utf-8 -*

import time

import init_work_home

init_work_home.init()
from config.config import Config
from utils import http
from utils.logger import logger
from utils.notify import Notify

api = Config.get_local_api() + '/v1/chain/get_table_rows'
bidname_list = Config.get_bidname_list()


def get_bindname_info(bidname):
    params = '{"scope":"eosio",' \
             '"table":"namebids",' \
             '"json":true,' \
             '"code":"eosio",' \
             '"limit":1,' \
             '"lower_bound":"%s"}' % bidname
    response = http.post('bidname', api, data=params)
    handle_reponse(bidname, response.json())


def handle_reponse(bidname, json):
    bid_info = json['rows'][0]
    if bidname != bid_info['newname']:
        logger.info('%s finish or not start bid', bidname)
        return
    name = 'name: %s' % bidname
    bidder = 'bidder: %s' % bid_info['high_bidder']
    amount = 'amount: %s' % (float(bid_info['high_bid']) / 10000)
    timestamp = int(bid_info['last_bid_time'])
    time_format_str = time.strftime("%F %T %Z", time.localtime(timestamp / 1000000))
    time_str = 'date: %s' % time_format_str
    timestamp = 'time: %s' % timestamp
    result = [name, bidder, amount, time_str, timestamp]
    logger.info(result)
    Notify.notify(name, bidder, amount, time_str, timestamp)


def get_all_bidname_info():
    for bidname in bidname_list:
        get_bindname_info(bidname)


def main():
    get_all_bidname_info()


if __name__ == '__main__':
    main()
