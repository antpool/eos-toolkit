# eos-toolkit
toolkit for EOSIO

### Environment
```
python 2.7
```

### Configuration

```
config/config.conf
[eos]
bp_account      = eosantpoolbp
bidname_list    =                            # e.g. eos,one
process_name    = nodeos                     # node process name to get pid
remote_api_list = http://api.bp.antpool.com, # external api list for height check
local_api       = http://127.0.0.1:8888      # local api
max_height_diff = 5                          # max diff for alarm

[claim]
eos_client      = /path/cleos
wallet_name     = default
wallet_password =
wallet_api      = http://127.0.0.1:8900

[logger]
log_home         = default                   # default is /path/eos-toolkit/logs
monitor_log_file = monitor.log
console_enable   = true
file_enable      = true

# add own info or add other notify tools slack/sms/email...
[notify]
beary_chat_id    =
beary_token      =
ding_talk_token  =
telegram_chat_id =    # e.g. 1,2...
telegram_token   =
```

### Notify
```
utils/notify.py
add other tools e.g. sms/email...
```

### Metric
```
utils/metric.py
add metric collector
```

### Run
```
1.cpu,ram,connecitons monitor
python /path/eos-toolkit/monitor/eos_process_monitor.py

2.node alive,height check
python /path/eos-toolkit/monitor/node_monitor.py

3.bp status monitor e.g. rank,votes,reward,claim_time
python /path/eos-toolkit/monitor/bp_status_monitor.py

4.bidname status monitor
python /path/eos-toolkit/monitor/bidname_status.py

5.bp produce monitor
python /path/eos-toolkit/monitor/bp_block_monitor.py

6.auto claim
1) setup permission claim for claimrewards and import claim's private key
2) use 'verbose-http-errors = true' get verbose error output when claim failed
3) /path/eos-toolkit/claim/auto_claim.sh

crontab
*/1 * * * * python /path/eos-toolkit/monitor/eos_process_monitor.py
*/5 * * * * python /path/eos-toolkit/monitor/node_monitor.py
*/10 * * * * python /path/eos-toolkit/monitor/bp_status_monitor.py
*/30 * * * * python /path/eos-toolkit/monitor/bidname_status.py
*/3 * * * * python /path/eos-toolkit/monitor/bp_block_monitor.py
0 */1 * * * /path/eos-toolkit/claim/auto_claim.sh
```
