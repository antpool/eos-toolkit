import ConfigParser
import os

cf = ConfigParser.ConfigParser()
work_home = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
config_home = os.path.dirname(os.path.realpath(__file__))
cf.read(config_home + "/config.conf")


class Config:

    def __init__(self):
        pass

    @staticmethod
    def get_work_home():
        return work_home

    @staticmethod
    def get_process_name():
        return cf.get("eos", "process_name")

    @staticmethod
    def get_api_list():
        remote_api_list = []
        api_list = cf.get("eos", "remote_api_list").split(',')
        for api in api_list:
            if api != "":
                remote_api_list.append(api)
        return remote_api_list

    @staticmethod
    def get_local_api():
        return cf.get("eos", "local_api")

    @staticmethod
    def get_max_height_diff():
        return cf.get("eos", "max_height_diff")

    @staticmethod
    def get_log_path():
        log_home = cf.get("logger", "log_home")
        if log_home == "default" or log_home == "":
            return Config.get_work_home() + "/logs"
        return log_home

    @staticmethod
    def get_monitor_log():
        return cf.get("logger", "monitor_log_file")
