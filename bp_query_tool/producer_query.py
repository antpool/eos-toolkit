#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import sys
import time

def usage():
    global bpname, api_url
    parser = argparse.ArgumentParser(description='BP Query Tool.')
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
    response = requests.post(producers_url, data='{"json":true,"limit":600}')
    i = 1
    for data in response.json()['rows']:
        if data['owner'] == bpname:
            bp_vote_weight = float(data['total_votes'])
            break;
        i = i + 1
    if bp_vote_weight == None:
        print("%s not found." % (bpname))
        sys.exit()
    print 'bp_name :',bpname
    print 'bp_index:',i
    print 'weight  :',int(bp_vote_weight)
    print 'vote_eos:', votes2eos(bp_vote_weight)
    print 'percent :',(bp_vote_weight/total_producer_vote_weight)

def votes2eos(votes):
    date = (int(time.time()) - (946684800000 / 1000))
    weight = float(date / (24 * 3600 * 7)) / float(52)
    return (float(votes) / pow(2, weight)) / 10000

if __name__ == '__main__':
    usage()
    get_producer_info()
