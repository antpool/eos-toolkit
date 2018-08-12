import argparse

import http
import init_work_home

init_work_home.init()
from config.config import NotifyConfig

beary_chat_id = NotifyConfig.get_beary_chat_id()
beary_token = NotifyConfig.get_beary_token()
ding_talk_token = NotifyConfig.get_ding_talk_token()
telegram_chat_id = NotifyConfig.get_telegram_chat_id()
telegram_token = NotifyConfig.get_telegram_token()


class Notify:
    @staticmethod
    def notify(msg, *args):
        # add other like slack, sms...
        Notify.all_notify(msg, *args)

    @staticmethod
    def all_notify(*args):
        if args is None or len(args) < 1:
            return
        msg = '\n'.join(args)
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
        http.post('ding_talk', ding_talk_hook_url, data=body, headers=http.def_headers)


class Beary:
    @staticmethod
    def beary_notify(message, chat_id, token):
        if chat_id is None or chat_id is "":
            return
        if token is None or token is "":
            return
        beary_hook_url = ("https://hook.bearychat.com/%s/incoming/%s" % (chat_id, token))
        body = ('{"text":"%s"}' % (message))
        http.post('beary', beary_hook_url, data=body, headers=http.def_headers)


class Telegram:
    @staticmethod
    def telegram_notify(message, chat_id, token):
        if chat_id is None or chat_id is "":
            return
        if token is None or token is "":
            return
        telegram_url = "https://api.telegram.org/bot%s/sendMessage" % (token)
        param = {"chat_id": chat_id, "text": message}
        http.post('telegram', telegram_url, params=param)


def usage():
    global msg
    parser = argparse.ArgumentParser(description='notify tool.')
    parser.add_argument('-m', '--msg', default=None, help='notify msg')
    args = parser.parse_args()
    msg = args.msg


if __name__ == "__main__":
    usage()
    Notify.notify(msg)
