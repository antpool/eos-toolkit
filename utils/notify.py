import requests

import logger
from config.config import NotifyConfig

beary_chat_id = NotifyConfig.get_beary_chat_id()
beary_token = NotifyConfig.get_beary_token()
ding_talk_token = NotifyConfig.get_ding_talk_token()
telegram_chat_id = NotifyConfig.get_telegram_chat_id()
telegram_token = NotifyConfig.get_telegram_token()


class Notify:
    @staticmethod
    def notify(msg):
        # add other like slack, sms...
        Notify.all_notify(msg)

    @staticmethod
    def all_notify(msg):
        Beary.beary_notify(msg, beary_chat_id, beary_token)
        DingTalk.ding_talk_notify(msg, ding_talk_token)
        Telegram.telegram_notify(msg, telegram_chat_id, telegram_token)


class DingTalk:
    @staticmethod
    def ding_talk_notify(message, token):
        if token is None or token is "":
            return
        ding_talk_hook_url = "https://oapi.dingtalk.com/robot/send?access_token=" + token
        body = ('{"msgtype":"text","text":{"content":"%s"}}' % (message))
        post('ding_talk', ding_talk_hook_url, data=body)


class Beary:
    @staticmethod
    def beary_notify(message, chat_id, token):
        if chat_id is None or chat_id is "":
            return
        if token is None or token is "":
            return
        beary_hook_url = ("https://hook.bearychat.com/%s/incoming/%s" % (chat_id, token))
        body = ('{"text":"%s"}' % (message))
        post('beary', beary_hook_url, data=body)


class Telegram:
    @staticmethod
    def telegram_notify(message, chat_id, token):
        if chat_id is None or chat_id is "":
            return
        if token is None or token is "":
            return
        telegram_url = "https://api.telegram.org/bot%s/sendMessage" % (token)
        param = {"chat_id": chat_id, "text": message}
        post('telegram', telegram_url, param=param)


def_headers = {'Content-Type': 'application/json'}


def post(notify_type, url, headers=def_headers, timeout=3.0, data=None, param=None):
    try:
        if param is not None:
            response = requests.post(url, param, timeout=timeout)
        else:
            response = requests.post(url, data=data, headers=headers, timeout=timeout)
        logger.info("%s: %s" % (notify_type, response.json()))
    except Exception as e:
        logger.error(notify_type + " notify exception:" + str(e))
