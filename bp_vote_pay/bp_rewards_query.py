#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import sys
import time

# usage
parser = argparse.ArgumentParser(description='BP Rewards Query Tool.')
parser.add_argument('-u', '--url', required=True, help='eos api')
parser.add_argument('-n', '--name', required=True, help='bp name')
args = parser.parse_args()
bpname, host = args.name, args.url

# bp vote info
bp_vote_weight = None
producers_url = host+"/v1/chain/get_table_rows"
response = requests.post(producers_url, data='{"scope":"eosio","table":"producers","json":true,"code":"eosio","limit":10000}')
for data in response.json()['rows']:
    if data['owner'] == bpname:
        bp_vote_weight = float(data['total_votes'])
        print("bp:%s, bp_vote_weight:%s" % (bpname,int(bp_vote_weight)))
if bp_vote_weight == None:
    print("%s not found" % (bpname))
    sys.exit()

# global info
global_url = host+"/v1/chain/get_table_rows"
response = requests.post(global_url, data='{"scope":"eosio","table":"global","json":true,"code":"eosio","limit":1}')
global_data=response.json()['rows'][0]
total_producer_vote_weight=float(global_data['total_producer_vote_weight'])
pervote_bucket=int(global_data['pervote_bucket'])

# bp vote pay
print("execute(pervote_bucket*prod.total_votes/total_producer_vote_weight): %s*%s/%s/10000" % (pervote_bucket,bp_vote_weight,total_producer_vote_weight))
bp_vote_pay = pervote_bucket*bp_vote_weight/total_producer_vote_weight/10000
print "bp_vote_pay:",bp_vote_pay
