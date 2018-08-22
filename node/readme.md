# Nodeos
### install
1. change [nodeos config](../config/config.conf)
2. ```/path/node/init.sh```
    - init folder and config
    - clone https://github.com/EOS-Mainnet/eos.git
    - build

### start
```
/path/node/start.sh
```
if first time start
```
/path/node/start.sh --genesis-json /path/eos_home/config/genesis.json
```

### stop
```
/path/node/stop.sh
```

### build
```
/path/node/build.sh tag
```