#!/usr/bin/env python
# author = 'ZZH'
# time = 2022/11/30
# project = bot_server

from main import send_post, get_infos
from threading import Timer
import datetime
import telebot
import json

with open("field.json", 'r') as f:
    opt = json.load(f)
with open("config.json", 'r') as f:
    config = json.load(f)

# 天津大学场馆域名
host = "http://vfmc.tju.edu.cn"

headers = {
    'User-Agent': "Mozilla/5.0",
    'Cookie': config['cookie']
}
bot = telebot.TeleBot(config['token'])


@bot.message_handler(commands=['exercise'])
def exercise(message):
    def parse_arg(text):
        return " ".join(text.split()[1:])

    # 可以个性化设置 这里默认 args[0]选2天后的时间
    time_list = parse_arg(message.text)
    date = datetime.datetime.today() + datetime.timedelta(days=2)
    date = str(date.month) + "." + str(date.day)
    infos = get_infos(date=date, time_list=time_list, campus="北洋园", sports="羽毛球")
    threads = []
    now = datetime.datetime.now()
    begin_time = datetime.datetime(now.year, now.month, now.day, hour=21)

    for i in range(10):
        threads.append(Timer(interval=(begin_time - now).seconds, function=send_post, args=(infos, "北洋园")))
    for thread in threads:
        thread.start()

    print('end..')


bot.polling()
