# eos-toolkit
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

7.log parser and trxs,latency metrics collect
1) change config eos_log_file
2) python /path/eos-toolkit/log_monitor/eos_log_monitor.py
```

### Environment
```
python 2.7

apt-get install bc jq
pip install -r requirements
```

### Configuration

```
config/config.conf
[eos]
bp_account      = eosantpoolbp
bidname_list    =                            # e.g. eos,one
process_name    = nodeos                     # node process name to get pid
eos_log_file    = /path/eos.log
remote_api_list = http://api.bp.antpool.com, # external api list for height check
local_api       = http://127.0.0.1:8888      # local api
max_height_diff = 5                          # max diff for alarm

[claim]
eos_client      = /path/cleos
wallet_name     = default
wallet_password =
wallet_api      = http://127.0.0.1:8900

[monitor]
# monitor process enable or not for start/monitor_start.py
node_monitor      = true
process_monitor   = true
bp_block_monitor  = false
bp_status_monitor = false
bidname_monitor   = false
auto_claim        = false

[metrics]
prometheus_host_port =

[logger]
log_home         = default                   # default is /path/eos-toolkit/logs
monitor_log_file = monitor.log
console_enable   = true
file_enable      = true

# add own info or add other notify tools slack/sms/email...
[notify]
beary_id            =    # for bp status or other normal status notify
beary_token         =
ding_talk_token     =
err_beary_id        =    # for exception info notify
err_beary_token     =
err_ding_talk_token =
telegram_chat_id    =
telegram_token      =
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
choose any one:
1./path/eos-tookit/start/monitor_start.py

2.systemctl
create /usr/lib/systemd/system/eosmonitor.service
e.g. eos-toolkit/systemctl/eosmonitor.service

systemctl start eosmonitor.service
systemctl restart eosmonitor.service
systemctl stop eosmonitor.service

3.crontab
*/1 * * * * python /path/eos-toolkit/monitor/eos_process_monitor.py
*/5 * * * * python /path/eos-toolkit/monitor/node_monitor.py
*/10 * * * * python /path/eos-toolkit/monitor/bp_status_monitor.py
*/30 * * * * python /path/eos-toolkit/monitor/bidname_status.py
*/3 * * * * python /path/eos-toolkit/monitor/bp_block_monitor.py
0 */1 * * * /path/eos-toolkit/claim/auto_claim.sh
```

### LogParser & Monitor
```
choose any one:
1./path/eos-tookit/log_monitor/eos_log_monitor.py

2.systemctl
create /usr/lib/systemd/system/eoslogmonitor.service
e.g. eos-toolkit/systemctl/eoslogmonitor.service

systemctl start eoslogmonitor.service
systemctl restart eoslogmonitor.service
systemctl stop eoslogmonitor.service
```

### Auto Install & Run
```
install
/path/eos-tookit/start/install.sh
1) auto install requirements
2) auto install systemctl service

run
/path/eos-tookit/start/start_all_service.sh
```
