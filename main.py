__author__ = 'z'

import telegram


def get_token():
    # global token
    f = open('bot.token', 'r')
    token = f.readline()
    return token


# return get_token()
LAST_UPDATE_ID = None

bot = telegram.Bot(token=get_token())

print(bot.getMe())


def echo():
    global LAST_UPDATE_ID
    updates = bot.getUpdates(offset=LAST_UPDATE_ID)
    for u in updates:
        print(u.message)
        message_chat_id = u.message.chat_id
        print(message_chat_id)
        chat_id = message_chat_id
        message = u.message.text
        # ('utf-8')
        print(message)
        if message:
            bot.sendMessage(chat_id=chat_id, text=message)
        LAST_UPDATE_ID = u.update_id + 1

        # bot.sendMessage(u.message)
        # bot.message(u.de_json(u.message))


while True:
    echo()
