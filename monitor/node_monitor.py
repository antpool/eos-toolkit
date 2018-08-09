#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import random
import socket

import requests

import init_work_home

init_work_home.init()
from utils.notify import Notify
from utils.metric import Metric
from config.config import Config
from utils import logger

remote_api_list = Config.get_api_list()
other_api_size = len(remote_api_list)
http_time_out_sec = 2.0 / (other_api_size + 2)


def log_and_notify(msg):
    msg = ('【%s】\n%s' % (socket.gethostname(), msg))
    logger.info(msg)
    notify(msg)


def diff_record_or_warning(local_block_num, remote_block_num, other_api):
    diff = remote_block_num - local_block_num
    msg = ("local:%s,remote(%s):%s,diff:%s" % (local_block_num, other_api, remote_block_num, diff))
    logger.info(msg)
    Metric.metric("eosHeight", diff)
    if abs(diff) >= max_height_diff:
        log_and_notify(msg)


def notify(msg):
    Notify.notify(msg, 'alarm')


def get_chain_info_from_other():
    index = random.randint(0, other_api_size - 1)
    url = remote_api_list[index]
    success, chain_info = get_chain_info_from_node(url)
    if success:
        return chain_info, url
    for url in remote_api_list:
        success, chain_info = get_chain_info_from_node(url)
        if success:
            break
    return chain_info, url


def get_chain_info_from_node(url, time_out_sec=http_time_out_sec):
    success = False
    try:
        url = url + "/v1/chain/get_info"
        result = requests.get(url, timeout=time_out_sec)
        msg = result.text
        if result.status_code == 200:
            success = True
            msg = json.loads(result.text)
    except BaseException as e:
        msg = str(e)
    if not success:
        logger.error('Failed to call %s error:%s' % (url, msg))
    return success, msg


def get_head_block_num(url_local):
    remote_block_num, local_block_num = 0, 0
    result_info, other_api = get_chain_info_from_other()
    if result_info != "":
        remote_block_num = result_info["head_block_num"]
    success, result_info = get_chain_info_from_node(url_local)
    if success:
        local_block_num = result_info["head_block_num"]
    return local_block_num, remote_block_num, other_api


def check_height():
    local_block_num, remote_block_num, other_api = get_head_block_num(url_local)
    if remote_block_num == 0 or local_block_num == 0:
        return
    diff_record_or_warning(local_block_num, remote_block_num, other_api)


def check_node_alive(url):
    is_alive, msg = get_chain_info_from_node(url)
    if not is_alive:
        log_and_notify('node is need check\n%s' % (msg))
        return False
    return True


def usage():
    global url_local, max_height_diff
    local_api = Config.get_local_api()
    max_height_diff = Config.get_max_height_diff()
    parser = argparse.ArgumentParser(description='BP nodeosd monitor tool.')
    parser.add_argument('-u', '--url_local', default=local_api, help='local node api')
    parser.add_argument('-d', '--height_diff', default=max_height_diff, help='max height diff')
    args = parser.parse_args()
    url_local = args.url_local
    max_height_diff = args.height_diff


def main():
    try:
        if not check_node_alive(url_local):
            return
        check_height()
    except BaseException as e:
        logger.error("check fail:%s" % str(e))


if __name__ == '__main__':
    usage()
    main()
