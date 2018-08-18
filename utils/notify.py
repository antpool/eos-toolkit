import argparse

import init_work_home

init_work_home.init()
from config.config import NotifyConfig
import http

beary_id = NotifyConfig.get_beary_id()
beary_token = NotifyConfig.get_beary_token()
ding_talk_token = NotifyConfig.get_ding_talk_token()
err_beary_id = NotifyConfig.get_err_beary_id()
err_beary_token = NotifyConfig.get_err_beary_token()
err_ding_talk_token = NotifyConfig.get_err_ding_talk_token()
telegram_chat_id = NotifyConfig.get_telegram_chat_id()
telegram_token = NotifyConfig.get_telegram_token()


class Notify:
    @staticmethod
    def notify_status(*args):
        Notify.all_notify(False, *args)

    @staticmethod
    def notify_error(*args):
        Notify.all_notify(True, *args)

    @staticmethod
    def all_notify(is_error, *args):
        # add other like slack, sms...
        if args is None or len(args) < 1:
            return
        msg = '\n'.join(args)
        if is_error:
            Beary.beary_notify(msg, err_beary_id, err_beary_token)
            DingTalk.ding_talk_notify(msg, err_ding_talk_token)
            Telegram.telegram_notify(msg, telegram_chat_id, telegram_token)
        else:
            Beary.beary_notify(msg, beary_id, beary_token)
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
    global msg, is_error
    parser = argparse.ArgumentParser(description='notify tool.')
    parser.add_argument('-m', '--msg', default=None, help='notify msg')
    parser.add_argument('-e', '--error', default=None, help='None is error data')
    args = parser.parse_args()
    msg = args.msg
    is_error = args.error


if __name__ == "__main__":
    usage()
    if is_error is None:
        Notify.notify_error(msg)
    else:
        Notify.notify_status(msg)
