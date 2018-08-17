# Monitor

- cpu,memory,connecitons monitor
```
python /path/eos-toolkit/monitor/eos_process_monitor.py
```
- node alive,height check
```
python /path/eos-toolkit/monitor/node_monitor.py
```
- bp status(rank,votes,reward,claim_time) monitor
```
python /path/eos-toolkit/monitor/bp_status_monitor.py
```
- bidname status monitor
```
python /path/eos-toolkit/monitor/bidname_status.py
```
- bp produce monitor
```
python /path/eos-toolkit/monitor/bp_block_monitor.py
```
- log parser and trxs,latency metrics collect
```
1) change config eos_log_file
2) python /path/eos-toolkit/monitor/eos_log_monitor.py
```
