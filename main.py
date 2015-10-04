# -*- coding: utf-8 -*-
import socket
import threading
import time
import configparser
import os

import schedule
import telegram
from flask import Flask, request

SECTION = 'main'

__author__ = 'z'

ANT_COUNT = 1
job = None

config = configparser.RawConfigParser()
config.read('config.cfg')


def get_token():
    return get_config_key('token')


def get_chat_id():
    return get_config_key('chat_id')


def get_crt():
    return get_config_key('crt')


def get_key():
    return get_config_key('key')


def get_config_key(key):
    return config.get(section=SECTION, option=key)


LAST_UPDATE_ID = None


# CERT = get_crt()
# CERT_KEY = get_key()
# CHAT_ID = get_chat_id()


def create_bot():
    global bot
    bot = telegram.Bot(token=(get_token()))
    print(bot.getMe())
    print(bot.setWebhook(webhook_url=get_config_key('url'), certificate=open(get_config_key('crt'), 'rb')))


create_bot()


# print(bot.getUpdates()[-1].message.text)


app = Flask(__name__)


def other_job():
    bot.sendMessage(chat_id=get_chat_id(), text=os.popen('date').read())


def test_job():
    global ANT_COUNT
    bot.sendMessage(chat_id=get_chat_id(), text=telegram.Emoji.ANT * ANT_COUNT)


def schedule_start():
    global cease_continuous_run
    # schedule.every(10).seconds.do(test_job)
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(1)

    continuous_thread = ScheduleThread()
    continuous_thread.start()


schedule_start()


@app.route("/")
def hello():
    print("Hello")
    return 'hello'


@app.route("/hook", methods=['POST'])
def hook():
    # print("hook")
    if request.method == "POST":
        global ANT_COUNT
        global job
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))

        print(update.message)
        chat_id = update.message.chat.id
        msg_id = update.message.message_id

        # Telegram understands UTF-8, so encode text for unicode compatibility
        text = update.message.text.encode('utf-8')
        if text:
            # print(text[0], text[1], text[2], text[3])
            # print(text[0:4])
            print(text)
            if text.lower() == '/cmd':
                custom_keyboard = [
                    [telegram.Emoji.THUMBS_UP_SIGN, telegram.Emoji.THUMBS_DOWN_SIGN, telegram.Emoji.ALARM_CLOCK,
                     telegram.Emoji.ALIEN_MONSTER]]
                reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                bot.sendMessage(chat_id=chat_id, text=socket.gethostname(), reply_to_message_id=msg_id,
                                reply_markup=reply_markup)
            elif text.lower() == 'status':
                bot.sendMessage(chat_id=chat_id, text='Online. I\'m ' + bot.getMe().username)
            elif text.lower() == "ls":
                t = os.popen("find /home/pi/age/Подкасты/ -type f -newer /home/pi/age/Подкасты/last").read()
                bot.sendMessage(chat_id=chat_id, text=t)
            elif text == telegram.Emoji.ALARM_CLOCK:
                job = schedule.every(5).seconds.do(other_job)
                bot.sendMessage(chat_id=chat_id, text="set alarmClock")
            elif text == telegram.Emoji.ALIEN_MONSTER:
                for job in schedule.jobs:
                    schedule.cancel_job(job)
            elif text == telegram.Emoji.THUMBS_UP_SIGN:
                ANT_COUNT += 1
                bot.sendMessage(chat_id=chat_id, text=str(ANT_COUNT))
            elif text == telegram.Emoji.THUMBS_DOWN_SIGN:
                ANT_COUNT -= 1
                bot.sendMessage(chat_id=chat_id, text=str(ANT_COUNT))
            else:
                # repeat the same message back (echo)
                bot.sendMessage(chat_id=chat_id, text=text)

    return 'ok'


# def echo():
#     global LAST_UPDATE_ID
#     updates = bot.getUpdates(offset=LAST_UPDATE_ID)
#     for u in updates:
#         print(u.message)
#         message_chat_id = u.message.chat_id
#         print(message_chat_id)
#         chat_id = message_chat_id
#         message = u.message.text
#         # ('utf-8')
#         print(message)
#         if message:
#             bot.sendMessage(chat_id=chat_id, text=message)
#         LAST_UPDATE_ID = u.update_id + 1
#
#         # bot.sendMessage(u.message)
#         # bot.message(u.de_json(u.message))
#
#
# while True:
#     echo()
context = (get_config_key('crt'), get_config_key('key'))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context=context)
