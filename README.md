# eos-toolkit

### Features
- Monitor
    - [cpu,memory,connecitons monitor](monitor)
    - [node alive,height check](monitor)
    - [bp status(rank,votes,reward,claim_time) monitor](monitor)
    - [bidname status monitor](monitor)
    - [bp produce monitor](monitor)
- Claim
    - [auto claim](claim)
- Log Collect
    - [log parser and trxs,latency metrics collect](monitor)
- Utils
    - [notify & metrics](utils)

### [Configuration](config/config.conf)

### QuickStart
#### Install
- auto install requirements
- auto install systemctl service
```
/path/eos-tookit/start/install.sh
```

#### Run
```
/path/eos-tookit/start/start_all_service.sh
```
### Requirements
```
python 2.7
apt-get install bc jq
pip install -r requirements
```
