import ConfigParser
import os
import re

cf = ConfigParser.ConfigParser()
work_home = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
config_home = os.path.dirname(os.path.realpath(__file__))
cf.read(config_home + "/config.conf")


class Config:
    section = "eos"

    @staticmethod
    def get_work_home():
        return work_home

    @staticmethod
    def get_process_name():
        return cf.get(Config.section, "process_name")

    @staticmethod
    def get_api_list():
        remote_api_list = []
        api_list = cf.get(Config.section, "remote_api_list").split(',')
        for api in api_list:
            if api != "":
                remote_api_list.append(api)
        return remote_api_list

    @staticmethod
    def get_local_api():
        return cf.get(Config.section, "local_api")

    @staticmethod
    def get_max_height_diff():
        return cf.getint(Config.section, "max_height_diff")

    @staticmethod
    def get_bp_account():
        return cf.get(Config.section, "bp_account")

    @staticmethod
    def get_bidname_list():
        bidname_list = []
        name_list = cf.get(Config.section, "bidname_list").split(',')
        for name in name_list:
            if name != "":
                bidname_list.append(name)
        return bidname_list

    @staticmethod
    def get_log_file():
        return cf.get(Config.section, "eos_log_file")


class MetricConfig:
    section = "metrics"

    @staticmethod
    def get_prometheus_host_port():
        return cf.get(MetricConfig.section, "prometheus_host_port")


class MonitorConfig:
    section = "monitor"

    @staticmethod
    def node_monitor():
        return MonitorConfig.get("node_monitor", enable=True, cron="5m")

    @staticmethod
    def eos_process_monitor():
        return MonitorConfig.get("process_monitor", enable=True, cron="30s")

    @staticmethod
    def bp_status_monitor():
        return MonitorConfig.get("bp_status_monitor", enable=False, cron="10m")

    @staticmethod
    def bp_block_monitor():
        return MonitorConfig.get("bp_block_monitor", enable=False, cron="5m")

    @staticmethod
    def bidname_monitor():
        return MonitorConfig.get("bidname_monitor", enable=False, cron="30m")

    @staticmethod
    def auto_claim():
        return MonitorConfig.get("auto_claim", enable=False, cron="10m")

    @staticmethod
    def get(key, enable=False, cron=None):
        value = cf.get(MonitorConfig.section, key)
        pattern = '(?P<enable>\w*)\s*,\s*(?P<cron>[1-9][0-9]*[smh])\s*.*'
        res = re.search(pattern, value)
        if res is None:
            return enable, cron
        group_dict = res.groupdict()
        enable_ = group_dict['enable']
        if enable_ == "True":
            enable_ = True
        else:
            enable_ = False
        return enable_, group_dict['cron']


class ClaimConfig:
    section = "claim"

    @staticmethod
    def get_client():
        return cf.get(ClaimConfig.section, "eos_client")

    @staticmethod
    def get_wallet_name():
        return cf.get(ClaimConfig.section, "wallet_name")

    @staticmethod
    def get_wallet_pwd():
        return cf.get(ClaimConfig.section, "wallet_password")

    @staticmethod
    def get_wallet_api():
        return cf.get(ClaimConfig.section, "wallet_api")


class LogConfig:
    section = "logger"

    @staticmethod
    def get_log_path():
        log_home = cf.get(LogConfig.section, "log_home")
        if log_home == "default" or log_home == "":
            return Config.get_work_home() + "/logs"
        return log_home

    @staticmethod
    def get_monitor_log():
        return cf.get(LogConfig.section, "monitor_log_file")

    @staticmethod
    def console_enable():
        return cf.getboolean(LogConfig.section, "console_enable")

    @staticmethod
    def file_enable():
        return cf.getboolean(LogConfig.section, "file_enable")


class NotifyConfig:
    section = "notify"

    @staticmethod
    def get_beary_id():
        return cf.get(NotifyConfig.section, "beary_id")

    @staticmethod
    def get_beary_token():
        return cf.get(NotifyConfig.section, "beary_token")

    @staticmethod
    def get_ding_talk_token():
        return cf.get(NotifyConfig.section, "ding_talk_token")

    @staticmethod
    def get_err_beary_id():
        return cf.get(NotifyConfig.section, "err_beary_id")

    @staticmethod
    def get_err_beary_token():
        return cf.get(NotifyConfig.section, "err_beary_token")

    @staticmethod
    def get_err_ding_talk_token():
        return cf.get(NotifyConfig.section, "err_ding_talk_token")

    @staticmethod
    def get_telegram_token():
        return cf.get(NotifyConfig.section, "telegram_token")

    @staticmethod
    def get_telegram_chat_id():
        return cf.get(NotifyConfig.section, "telegram_chat_id")


class HttpConfig:
    section = "http"

    @staticmethod
    def default_time_out_sec():
        return cf.getfloat(HttpConfig.section, "def_timeout_sec")
