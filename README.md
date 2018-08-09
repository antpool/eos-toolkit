# eos-toolkit
toolkit for EOSIO

### bp_vote_pay query
```
python bp_vote_pay_query.py -n eosantpoolbp -u http://127.0.0.1:8888
```

### bp_info query
```
python producer_query.py -n eosantpoolbp -u http://127.0.0.1:8888
```

### configuration

```
config/config.conf
[eos]
process_name    = nodeos                     # node process name to get pid
other_api_list  = http://api.bp.antpool.com, # external api list for height check
local_api       = http://127.0.0.1:8888      # local api
max_height_diff = 5                          # max diff for alarm

[logger]
log_home         = default                   # default is /path/eos-toolkit/logs
monitor_log_file = monitor.log


notify
add own slack/sms/email... to utils/notify.py

metric
add own metric collector to utils/metric.py

```
### node monitor run
```
1.cpu/ram/connecitons monitor
python eos_process_monitor.py

2.node alive/height check
python node_monitor.py

use crontab
*/1 * * * * python /path/eos_process_monitor.py
*/5 * * * * python /path/node_monitor.py
```
