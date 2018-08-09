import ConfigParser
import os

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
        return cf.get(Config.section, "max_height_diff")

    @staticmethod
    def get_bp_account():
        return cf.get(Config.section, "bp_account")


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
        return cf.get(LogConfig.section, "console_enable") == "true"

    @staticmethod
    def file_enable():
        return cf.get(LogConfig.section, "file_enable") == "true"


class NotifyConfig:
    section = "notify"

    @staticmethod
    def get_beary_chat_id():
        return cf.get(NotifyConfig.section, "beary_chat_id")

    @staticmethod
    def get_beary_token():
        return cf.get(NotifyConfig.section, "beary_token")

    @staticmethod
    def get_ding_talk_token():
        return cf.get(NotifyConfig.section, "ding_talk_token")

    @staticmethod
    def get_telegram_token():
        return cf.get(NotifyConfig.section, "telegram_token")

    @staticmethod
    def get_telegram_chat_id():
        return cf.get(NotifyConfig.section, "telegram_chat_id")
