#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse

def usage():
    global bpname, api_url
    parser = argparse.ArgumentParser(description='BP Rewards Query Tool.')
    parser.add_argument('-u', '--url', required=True, help='eos api')
    parser.add_argument('-n', '--name', required=True, help='bp name')
    args = parser.parse_args()
    bpname, api_url = args.name, args.url

def get_global_info():
    global total_producer_vote_weight
    global_url = api_url+"/v1/chain/get_table_rows"
    response = requests.post(global_url, data='{"scope":"eosio","table":"global","json":true,"code":"eosio","limit":1}')
    global_data=response.json()['rows'][0]
    total_producer_vote_weight=float(global_data['total_producer_vote_weight'])

def get_producer_info():
    get_global_info()
    bp_vote_weight = None
    producers_url = api_url+"/v1/chain/get_producers"
    response = requests.post(producers_url, data='{"json":true,"limit":60}')
    i = 1
    for data in response.json()['rows']:
        if data['owner'] == bpname:
            bp_vote_weight = float(data['total_votes'])
            break;
        i = i + 1
    if bp_vote_weight == None:
        print("%s not found." % (bpname))
        sys.exit()
    print 'bpname:',bpname
    print '#:',i
    print 'vote_weight:',int(bp_vote_weight)
    print '%:',(bp_vote_weight/total_producer_vote_weight)

if __name__ == '__main__':
    usage()
    get_producer_info()
