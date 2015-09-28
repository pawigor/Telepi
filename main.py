__author__ = 'z'

import telegram


def get_token():
    # global token
    f = open('bot.token', 'r')
    token = f.readline()
    return token


# return get_token()

bot = telegram.Bot(token=get_token())

print(bot.getMe())
