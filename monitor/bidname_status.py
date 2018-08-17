#!/usr/bin/env python
# -*- coding: utf-8 -*

import time

import init_work_home

init_work_home.init()
from config.config import Config
from utils.logger import logger
from utils.notify import Notify
from api import eos_api

api = Config.get_local_api()
bidname_list = Config.get_bidname_list()


def get_bindname_info(bidname):
    bid_info = eos_api.get_bindname_info(bidname, url=api)
    if not bid_info:
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
    Notify.notify_status(name, bidder, amount, time_str, timestamp)


def get_all_bidname_info():
    for bidname in bidname_list:
        get_bindname_info(bidname)


def main():
    get_all_bidname_info()


if __name__ == '__main__':
    main()
