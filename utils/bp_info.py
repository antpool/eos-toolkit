#!/usr/bin/env python
# -*- coding: utf-8 -*

import argparse
import re
import time

import init_work_home

init_work_home.init()

from config.config import Config
from utils.logger import logger
from api import eos_api

ct = int(time.time() * 1000000)
bp_name = Config.get_bp_account()
url = Config.get_local_api()
query_info = None


def init_timezone():
    global timezone
    timezone = str(time.strftime("%z", time.localtime()))
    timezone = timezone.replace("+", "")
    timezone = timezone.replace("0", "")
    if not timezone:
        timezone = 0
    else:
        int(timezone)


def timestamp(date):
    pattern = re.compile("\..*")
    result = re.sub(pattern, '', date)
    reformat_date = result.replace("T", " ")
    millions_secs = int(time.mktime(time.strptime(reformat_date, "%Y-%m-%d %H:%M:%S"))) * 1000000
    return millions_secs + int(timezone) * 3600 * 1000000


def get_account_info():
    global bp_vote_weight, unpaid_blocks, last_claim_time, rank, find_bp
    rank = 0
    find_bp = False
    producer = eos_api.get_producers(url, account=bp_name, limit=1000)
    if not producer:
        return
    find_bp = True
    rank = int(producer['rank'])
    bp_vote_weight = float(producer['total_votes'])
    unpaid_blocks = int(producer['unpaid_blocks'])
    last_claim_time = timestamp(producer['last_claim_time'])


def get_bp_account_info():
    get_account_info()
    if not find_bp:
        logger.info("%s not found." % (bp_name))
        return
    if query_info == 'last_claim_time':
        print(last_claim_time)


def usage():
    global bp_name, url, query_info
    parser = argparse.ArgumentParser(description='BP account query tool.')
    parser.add_argument('-bp', '--bp_name', default=bp_name, help='bp name')
    parser.add_argument('-u', '--url', default=url, help='node api')
    parser.add_argument('-i', '--info', default=None, help='query info')
    args = parser.parse_args()
    bp_name = args.bp_name
    url = args.url
    query_info = args.info


def main():
    global rank
    try:
        init_timezone()
        get_bp_account_info()
    except Exception as e:
        logger.error("occurs exception:%s" % e)


if __name__ == '__main__':
    usage()
    main()
