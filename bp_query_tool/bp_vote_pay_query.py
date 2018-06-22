#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import sys
import time

def usage():
    global bpname, api_url
    parser = argparse.ArgumentParser(description='BP Rewards Query Tool.')
    parser.add_argument('-u', '--url', required=True, help='eos api')
    parser.add_argument('-n', '--name', required=True, help='bp name')
    args = parser.parse_args()
    bpname, api_url = args.name, args.url

def get_vote_weight():
    global bp_vote_weight, unpaid_blocks
    bp_vote_weight = None
    unpaid_blocks = 0
    producers_url = api_url+"/v1/chain/get_table_rows"
    response = requests.post(producers_url, data='{"scope":"eosio","table":"producers","json":true,"code":"eosio","limit":10000}')
    for data in response.json()['rows']:
        if data['owner'] == bpname:
            bp_vote_weight = float(data['total_votes'])
            unpaid_blocks = int(data['unpaid_blocks'])
    if bp_vote_weight == None:
        print("%s not found." % (bpname))
        sys.exit()

def get_global_info():
    global total_producer_vote_weight, pervote_bucket, total_unpaid_blocks
    global_url = api_url+"/v1/chain/get_table_rows"
    response = requests.post(global_url, data='{"scope":"eosio","table":"global","json":true,"code":"eosio","limit":1}')
    global_data=response.json()['rows'][0]
    total_producer_vote_weight=float(global_data['total_producer_vote_weight'])
    pervote_bucket=int(global_data['pervote_bucket'])
    total_unpaid_blocks=int(global_data['total_unpaid_blocks'])

def get_vote_pay():
    global bp_vote_pay
    print bpname, api_url
    get_vote_weight()
    get_global_info()
    print("execute(pervote_bucket*prod.total_votes/total_producer_vote_weight): %s*%s/%s/10000" % (pervote_bucket,bp_vote_weight,total_producer_vote_weight))
    bp_vote_pay = pervote_bucket*bp_vote_weight/total_producer_vote_weight/10000
    print "bp_vote_pay:",bp_vote_pay

def get_block_pay():
    global bp_block_pay
    print("execute(pervote_bucket*prod.unpaid_blocks/total_unpaid_blocks): %s*%s/%s/10000" % (pervote_bucket,unpaid_blocks,total_unpaid_blocks))
    bp_block_pay = pervote_bucket*unpaid_blocks/total_unpaid_blocks/10000
    print "bp_block_pay:",bp_block_pay

if __name__ == '__main__':
    usage()
    get_vote_pay()
    get_block_pay()
    print 'bp_all_pay:', (bp_vote_pay+bp_block_pay)
