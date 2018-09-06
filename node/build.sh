#!/bin/bash

current_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${current_home};cd ../;pwd)
get_config="${work_home}/config/config.sh"
eos_home=$(${get_config} "eos_home")
eosio_home="${eos_home}/eos"
build_home="${eosio_home}/build"
command_home="${eos_home}/command"
logs_home="${eos_home}/logs"
build_log="${logs_home}/build.log"
tag=$(${get_config} "tag")
last_server_version=""
new_server_version=""

log() {
  echo "[$(date '+%F %T%z')] ${@}"| tee -a ${build_log}
}

execute() {
  log $@
  $@
}

go_command_home() {
  cd ${command_home}
}

install_command() {
  go_command_home
  keosd="${eosio_home}/build/programs/keosd/keosd"
  nodeos="${eosio_home}/build/programs/nodeos/nodeos"
  cleos="${eosio_home}/build/programs/cleos/cleos"
  [ ! -f ${keosd} ] && log "${keosd} install failed." && exit 1 || rm -f ${command_home}/keosd && execute cp ${keosd} ${command_home}/keosd
  [ ! -f ${cleos} ] && log "${cleos} install failed." && exit 1 || rm -f ${command_home}/cleos && execute cp ${cleos} ${command_home}/cleos
  [ ! -f ${nodeos} ] && log "${nodeos} install failed." && exit 1 || rm -f ${command_home}/nodeos && execute cp ${nodeos} ${command_home}/nodeos
}

make_eos() {
  check_tag
  go_eosio_home
  clear_build_home
  ${eosio_home}/eosio_build.sh -s EOS
  [ 0 != $? ] && log "eosio_build failed." && exit 1
  [ ! -d build ] && log "build not exists." && exit 1
  go_build_home
  sudo make install
}

clear_build_home() {
  last_server_version=`${build_home}/programs/nodeos/nodeos -v`
  clear_command="rm -rf ${build_home}"
  log "execute ${clear_command} Y/n?"
  read ensure
  is_execute ${ensure} && [ -d ${build_home} ] && execute rm -rf ${build_home}
}

go_build_home() {
  cd ${build_home}
}

go_eosio_home() {
  cd ${eosio_home}
}

is_execute() {
  local ensure=$1
  [ "Y" != "${ensure}" ] && [ "y" != "${ensure}" ] && return 1
  return 0
}

check_tag() {
  go_eosio_home
  [ "${tag}" == "" ] && log "need tag." && exit 1
  execute git checkout .
  execute git pull --tags 2>/dev/null
  current_tag=`git status | head -1|sed "s/.* //g"`
  log "current_tag: ${current_tag}"
  [ "${tag}" != "$(git tag | grep "${tag}")" ] && log "tag ${tag} error." && exit 1
  log "checkout to ${tag} Y/n?"
  read ensure
  is_execute ${ensure}
  if [ $? -eq 0 ]; then
    execute git checkout ${tag} 2>/dev/null
    execute git submodule update --init --recursive
  fi
}

check_home() {
  [ ! -d ${eos_home} ] && log "${eos_home} not exists." && exit 1
  [ ! -d ${eosio_home} ] && log "${eosio_home} not exists." && exit 1
  [ ! -d ${command_home} ] && mkdir ${command_home}
  [ ! -d ${command_home} ] && log "${command_home} not exists." && exit 1
}

build_eos() {
  [ "$1" != "" ] && tag=$1
  check_home
  make_eos
  install_command
  log "build successfully"
  log "current tag: ${tag}"
  log "last_server_version ${last_server_version}"
  log "new_server_version `${command_home}/nodeos -v`"
}

build_eos $@