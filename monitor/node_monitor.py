#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import random
import socket
import time

import init_work_home

work_home = init_work_home.init()
from utils.notify import Notify
from utils.metric import Metric
from config.config import Config, BackupConfig
from utils.logger import logger
from api import eos_api

url_local = Config.get_local_api()
max_height_diff = Config.get_max_height_diff()
remote_api_list = Config.get_api_list()
remote_api_size = len(remote_api_list)
http_time_out_sec = 2.0 / (remote_api_size + 2)
hostname = '【%s】' % socket.gethostname()
backup_status = '%s/backup/%s' % (work_home, BackupConfig.get_backup_status())


def notify(*args):
    Notify.notify_error(*args)


def diff_record_or_warning(local_block_num, remote_block_num, other_api):
    diff = remote_block_num - local_block_num
    msg = ("local:%s,remote(%s):%s,diff:%s" % (local_block_num, other_api, remote_block_num, diff))
    logger.info('%s, %s', hostname, msg)
    Metric.metric(Metric.height_diff, diff, version=local_server_version)
    if abs(diff) >= max_height_diff:
        notify(hostname, msg)


def get_chain_info_from_other():
    index = random.randint(0, remote_api_size - 1)
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
    return eos_api.get_chain_info(url, timeout=time_out_sec)


def get_head_block_num():
    global local_server_version
    local_server_version = -1
    remote_block_num, local_block_num = 0, 0
    result_info, other_api = get_chain_info_from_other()
    if result_info != "":
        remote_block_num = result_info["head_block_num"]
    success, result_info = get_chain_info_from_node(url_local)
    if success:
        local_block_num = result_info["head_block_num"]
        local_server_version = int(result_info["server_version"], 16)
    return local_block_num, remote_block_num, other_api


def check_height():
    local_block_num, remote_block_num, other_api = get_head_block_num()
    if remote_block_num == 0 or local_block_num == 0:
        return
    diff_record_or_warning(local_block_num, remote_block_num, other_api)


def check_node_alive(url):
    if os.path.isfile(backup_status):
        backup_cost_time = int(time.time()) - get_last_backup_time()
        if backup_cost_time >= BackupConfig.get_max_sec():
            msg = 'node backup for too long(%sm), please check' % (backup_cost_time / 60)
            logger.info(msg)
            notify(hostname, msg)
            return False
        logger.info('node is backup, skipped node check')
        return False
    is_alive, msg = get_chain_info_from_node(url)
    if not is_alive:
        notify(hostname, 'node is need check', msg)
        return False
    return True


def get_last_backup_time():
    with open(backup_status, 'r') as f:
        return int(f.read().rstrip('\n'))


def usage():
    global url_local, max_height_diff
    parser = argparse.ArgumentParser(description='BP nodeosd monitor tool.')
    parser.add_argument('-u', '--url_local', default=url_local, help='local node api')
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
        logger.error("check fail:%s", e)


if __name__ == '__main__':
    usage()
    main()
