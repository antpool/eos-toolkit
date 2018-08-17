# eos-toolkit

### Features
- [cpu,memory,connecitons monitor](monitor)
- [node alive,height check](monitor)
- [bp status(rank,votes,reward,claim_time) monitor](monitor)
- [bidname status monitor](monitor)
- [bp produce monitor](monitor)
- [auto claim](claim)
- [log parser and trxs,latency metrics collect](monitor)
- [notify & metrics](utils)

### Configuration
[config](config/config.conf)

### Quick Install & Run
```
install
/path/eos-tookit/start/install.sh
1) auto install requirements
2) auto install systemctl service

run
/path/eos-tookit/start/start_all_service.sh
```

### Requirements
```
python 2.7
apt-get install bc jq
pip install -r requirements
```
