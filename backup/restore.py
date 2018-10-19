#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import gzip
import os
import urllib
import socket

import requests
import yaml

import init_work_home

init_work_home.init()
from config.config import BackupConfig
from utils.logger import logger
from utils.notify import Notify

backup_index = ''

base_url = BackupConfig.get_backup_server() + '/api/backup'
backup_home = BackupConfig.get_backup_home()
type_indexes = 'indexes'
type_chunks = 'chunks'
indexes_home = backup_home + '/' + type_indexes
chunks_home = backup_home + '/' + type_chunks
hostname = '【%s】' % socket.gethostname()


def check_backup_home():
    create_dir(backup_home)
    create_dir(indexes_home)
    create_dir(chunks_home)


def create_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def fetch_backup_latest_index():
    global backup_index
    if backup_index is None or backup_index == '':
        backup_index = requests.get("%s/%s" % (base_url, 'list/latest')).text
        if backup_index is None or backup_index == '':
            raise Exception('not found latest index')
    check_and_download_index(backup_index)
    backup_index = '%s/%s' % (indexes_home, backup_index)
    return backup_index


def fetch_backup():
    global backup_index
    backup_index = fetch_backup_latest_index()
    if not os.path.isfile(backup_index):
        raise Exception('Config %s not exists.' % backup_index)
    with gzip.open(backup_index, 'rb') as f:
        content = yaml.load(f.read())
    files = content['files']
    backup_data = dict()
    for chunk in files:
        backup_file, chunk_hash_list = handle_chunk(chunk)
        backup_data[backup_file] = chunk_hash_list
        logger.info('fetch %s backup, size: %s' % (backup_file, len(chunk_hash_list)))
        i = 1
        empty_size = 0
        list_size = len(chunk_hash_list)
        for chunk_hash in chunk_hash_list:
            empty_size = check_and_download_chunk('%s/%s' % (i, list_size), chunk_hash, empty_size)
            i += 1
        logger.info('fetch %s backup success, skipped %s empty pieces' % (backup_file, empty_size))
    logger.info('fetch %s finished' % backup_index)


def handle_chunk(chunk):
    pieces = chunk['chunks']
    backup_file = chunk['filename']
    chunk_hash_list = list()
    if pieces is None:
        return backup_file, chunk_hash_list
    for piece in pieces:
        try:
            chunk_hash_list.append(piece['contentSHA'])
        except Exception as e:
            chunk_hash_list.append('empty')
            if not piece['empty']:
                raise e
    return backup_file, chunk_hash_list


def check_and_download_index(index):
    if os.path.exists('%s/%s' % (indexes_home, index)):
        return
    download(type_indexes, index)
    logger.info("%s download success" % index)


def check_and_download_chunk(index, chunk_hash, empty_size):
    if os.path.exists('%s/%s' % (chunks_home, chunk_hash)):
        logger.info('%s -> %s download success, local' % (index, chunk_hash))
        return empty_size
    if chunk_hash == 'empty':
        empty_size += 1
        return empty_size
    download(type_chunks, chunk_hash)
    logger.info('%s -> %s download success, remote' % (index, chunk_hash))
    return empty_size


def download(file_type, filename):
    response = requests.get("%s/query/%s/%s" % (base_url, file_type, filename))
    if response.text == "False":
        return
    if file_type == type_chunks:
        backup_file = '%s/%s' % (chunks_home, filename)
    elif file_type == type_indexes:
        backup_file = '%s/%s' % (indexes_home, filename)
    else:
        raise Exception('unknown file type %s' % file_type)

    urllib.urlretrieve(download_url(file_type, filename), backup_file)


def download_url(file_type, filename):
    return '%s/download/%s/%s' % (base_url, file_type, filename)


def usage():
    global backup_index
    parser = argparse.ArgumentParser(description='eos backup download tool.')
    parser.add_argument('-i', '--index', default=None, help='backup index file')
    args = parser.parse_args()
    backup_index = args.index


if __name__ == '__main__':
    usage()
    try:
        check_backup_home()
        fetch_backup()
    except Exception as e:
        msg = '%s\nbackup auto restore error\n %s' % (hostname, str(e))
        logger.error(msg)
        Notify.notify_error(msg)
