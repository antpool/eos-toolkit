#!/bin/bash

tag="mainnet-1.1.4"

eos_user=eos
opt_path="/opt"
work_home="${opt_path}/eosbp"
data_dir="${work_home}/data"
log_dir="${work_home}/logs"
config_dir="${work_home}/config"
scripts_dir="${work_home}/scripts"

init_folder() {
  cd /opt
  [ ! -d ${work_home} ] && sudo mkdir ${work_home} && sudo chown ${eos_user} ${work_home}
  cd ${work_home}
  [ ! -d logs ] && mkdir logs
  [ ! -d data ] && mkdir data
  [ ! -d config ] && mkdir config
  [ ! -d scripts ] && mkdir scripts
}


get_code() {
  cd ${work_home}
  git clone https://github.com/EOS-Mainnet/eos.git
  cd eos
  git checkout ${tag}
  git submodule update --init --recursive
  ./eosio_build.sh
  cd ./build
  sudo make install
}

main() {
  init_folder
  get_code
}

main