# -*- coding: utf-8 -*-
import configparser
import os
import socket
import threading

import schedule
import telegram
import time
from flask import Flask, request
from rtorrent import RTorrent

MISC_AGE_LAST = "/misc/age/Подкасты/last"

SECTION = 'main'

__author__ = 'z'

ANT_COUNT = 1
job = None

config = configparser.RawConfigParser()
config.read('config.cfg')


def get_rtorrent():
    return RTorrent()


def get_config_key(key):
    try:
        return config.get(section=SECTION, option=key)
    except configparser.NoOptionError:
        return None


def set_config_key(key, value):
    return config.set(section=SECTION, option=key, value=value)


LAST_UPDATE_ID = get_config_key('last_update_id')

rt = RTorrent(url="http://127.0.0.1", _verbose=False)


# rt.load_torrent_simple(
#     "magnet:?xt=urn:btih:d5bc08ec2c2a8f1c2a133850e126cc9922214399"
#     "&dn=Spotless%20%20-%20Season%201%20%28AlexFilm%29%20BDRip%201080p", "url", True, True)


# torrents = rt.torrents()

# print(torrents)


# CERT = get_crt()
# CERT_KEY = get_key()
# CHAT_ID = get_chat_id()


def create_bot():
    global bot
    bot = telegram.Bot(token=(get_config_key('token')))
    # print(bot.getMe())
    print(bot.setWebhook(webhook_url=get_config_key('url'), certificate=open(get_config_key('crt'), 'rb')))


create_bot()

# print(bot.getUpdates()[-1].message.text)


app = Flask(__name__)


def other_job():
    bot.sendMessage(chat_id=get_config_key('chat_id'), text=os.popen('date').read())


def test_job():
    global ANT_COUNT
    bot.sendMessage(chat_id=get_config_key('chat_id'), text=telegram.Emoji.ANT * ANT_COUNT)


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


def dwnl_pdcsts_job():
    os.popen("touch " + MISC_AGE_LAST)
    os.popen("gpo update")
    os.popen("gpo download")
    t = os.popen("find /misc/age/Подкасты/ -type f -newer " + MISC_AGE_LAST).read()
    bot.sendMessage(chat_id=get_config_key('chat_id'), text=t)


podcast_job = schedule.every(1).day.at('03:00').do(dwnl_pdcsts_job)


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
        set_config_key('last_update_id', update.update_id)

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
                bot.sendMessage(chat_id=chat_id, text=(get_status()))
            elif text[0:7] == "magnet:":
                rt.load_torrent_simple(text, "url", True, True)
                bot.sendMessage(chat_id=chat_id, text=text[0:7])
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


def get_status():
    msg = 'Online. I\'''m ' + bot.getMe().username + '\n'
    msg += 'Torrents:\n'
    rt.update()
    for torrent in rt.torrents:
        percent = float(torrent.get_completed_bytes()) / float(torrent.get_size_bytes()) * 100.0
        msg += '*** %s  [%2.2f%%] ***\n' % (torrent.get_name(), percent)
    for job in schedule.jobs:
        if hasattr(job.job_func, '__name__'):
            msg += " %s %s \n" % (job.job_func.__name__, job.__repr__)
    return msg


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
