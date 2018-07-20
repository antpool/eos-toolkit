#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import requests
import socket
import sys
import random
import inspect
import time

other_api_list = [
        # add 1-4 api
        "http://api.bp.antpool.com"
    ]
other_api_size = len(other_api_list)
http_time_out_sec = 2.0/(other_api_size + 2)

def log(message):
    caller_info = inspect.stack()[1]
    print("[%s %s %d] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), caller_info[3], caller_info[2], message))

def log_and_alarm(msg):
    msg = ('【%s】\n%s' % (socket.gethostname(),msg))
    log(msg)
    # add slack,email...

def diff_record_or_warning(local_block_num,remote_block_num,other_api):
    diff = remote_block_num - local_block_num 
    msg = ("local:%s,remote(%s):%s,diff:%s" % (local_block_num,other_api,remote_block_num, diff))
    log(msg)
    if abs(diff) >= max_height_diff:
        log_and_alarm(msg)

def get_chain_info_from_other():
    index = random.randint(0, other_api_size-1)
    url = other_api_list[index]
    success,chain_info = get_chain_info_from_node(url)
    if success:
        return chain_info,url
    for url in other_api_list:
        success,chain_info = get_chain_info_from_node(url)
        if success:
            break
    return chain_info,url

def get_chain_info_from_node(url, time_out_sec=http_time_out_sec):
    success = False
    msg = ""
    try:
        url = url+"/v1/chain/get_info"
        result = requests.get(url, timeout=time_out_sec)
        msg = result.text
        if result.status_code == 200:
            success = True
            msg = json.loads(result.text)
    except BaseException as e:
        msg = str(e)
    if not success:
        log('Failed to call %s error:%s' % (url, msg))
    return success,msg

def get_head_block_num(url_local):
    remote_block_num,local_block_num = 0,0
    result_info,other_api = get_chain_info_from_other()
    if result_info != "":
        remote_block_num = result_info["head_block_num"]
    success,result_info = get_chain_info_from_node(url_local)
    if success:
        local_block_num = result_info["head_block_num"]
    return local_block_num,remote_block_num,other_api

def check_height():
    local_block_num,remote_block_num,other_api = get_head_block_num(url_local)
    if remote_block_num == 0 or local_block_num == 0:
        return
    diff_record_or_warning(local_block_num,remote_block_num,other_api)

def check_node_alive(url):
    is_alive,msg = get_chain_info_from_node(url)
    if not is_alive:
        log_and_alarm('node is need check\n%s' % (msg))
        sys.exit()

def usage():
    global url_local,max_height_diff
    parser = argparse.ArgumentParser(description='BP nodeos monitor tool.')
    parser.add_argument('-u','--url_local',default='http://localhost:8888',help='local node api')
    parser.add_argument('-d','--height_diff',default=5,help='max height diff for alarm')
    args = parser.parse_args()
    url_local = args.url_local
    max_height_diff = args.height_diff

def main():
    try:
        check_node_alive(url_local)
        check_height()
    except Exception as e:
        log("check fail:%s" % str(e))

if __name__ == '__main__':
    usage()
    main()