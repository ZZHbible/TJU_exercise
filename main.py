#!/usr/bin/env python
# author = 'ZZH'
# time = 2022/11/30
# project = main

import json
import requests
import datetime
from urllib.parse import urljoin
import argparse
from threading import Thread, Timer

with open("field.json", 'r') as f:
    opt = json.load(f)
with open("config.json", 'r') as f:
    cookie = json.load(f)

# 天津大学场馆域名
host = "http://vfmc.tju.edu.cn"

headers = {
    'User-Agent': "Mozilla/5.0",
    'Cookie': cookie['cookie']
}

'''
    date 为 11.30 的格式，符合本人使用习惯
'''


def calc_day(date: str):
    now_date = datetime.date.today()
    now_date = datetime.datetime(now_date.year, now_date.month, now_date.day)
    month, day = date.split('.')
    exercise_day = datetime.datetime(now_date.year, int(month), int(day))
    if (exercise_day - now_date).days < 0:
        if exercise_day.month == 1 and (exercise_day.day == 1 or exercise_day.day == 2):
            exercise_day = datetime.datetime(now_date.year + 1, month, day)
        else:
            return -1
    return (exercise_day - now_date).days


'''
    data: 11.30 的格式
    campus: 北洋园，卫津路体育馆，卫津路体育场，卫津路篮球馆
    sports: 各自校区的运动
    time_list= 14 15 13 按照自己喜欢的时间顺序排序
'''


def get_infos(date: str, time_list="15", campus="北洋园", sports="羽毛球"):
    dateadd = calc_day(date)
    if dateadd < 0 or dateadd > 2: print("输入格式有误或日期错误，需要距离本日2日内")
    time_list = time_list.split()
    total_time = opt["Time"]
    infos = []
    for time in time_list:
        for key, val in total_time.items():
            if time in val:
                data = {
                    "dateadd": str(dateadd),
                    "TimePeriod": str(key),
                    "VenueNo": opt[campus]["venueNo"],
                    "FieldTypeNo": opt[campus][sports]["FieldTypeNo"]
                }
                url = urljoin(host, '/Field/GetVenueStateNew')
                res = requests.get(url=url, data=data, headers=headers).text
                data = json.loads(json.loads(res)["resultdata"])
                BeginTime = val[-1]
                for i, t in enumerate(val):
                    if time in t:
                        BeginTime = t
                        break
                for raw in data:
                    if raw["DateBeginTime"].split()[1].split(":")[0] == time:
                        info = {
                            "FieldNo": raw["FieldNo"],
                            "FieldTypeNo": raw["FieldTypeNo"],
                            "FieldName": raw["FieldName"],
                            "DateAdd": str(dateadd),
                            "BeginTime": BeginTime + ":00",
                            "Endtime": ":".join([str(int(BeginTime) + 1), "00"]),
                            "Price": raw["FinalPrice"]
                        }
                        infos.append(info)

    return infos


def OrderField(info, venueNo):
    url = urljoin(host, "/Field/OrderField")
    data = {
        "checkdata": str([info]),
        "VenueNo": venueNo,
        "OrderType": "Field"
    }
    print(data)
    req = requests.post(url=url, json=data, headers=headers)

    content = json.loads(req.text)
    # print(content)
    return content


def send_post(infos, campus="北洋园"):
    venueNo = opt[campus]["venueNo"]
    for info in infos:
        res = OrderField(info, venueNo)
        if res["type"] == 1:
            print("succeed", info)
            # break
        print("failed", info)


def main():
    date = datetime.datetime.today() + datetime.timedelta(days=2)
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default=str(date.month) + "." + str(date.day), help="日期 like 11.30")
    parser.add_argument('--campus', type=str, default="卫津路体育场", help="校区体育场")
    parser.add_argument('--sport', type=str, default="北网球场", help="活动")
    parser.add_argument('--time', type=str, default="15", help="期望时间")
    args = parser.parse_args()

    infos = get_infos(date=args.date, time_list=args.time, campus=args.campus, sports=args.sport)
    threads = []
    now = datetime.datetime.now()
    begin_time = datetime.datetime(now.year, now.month, now.day, hour=21)

    # t1=Thread(target=send_post,args=(infos, args.campus))
    # t1.start()

    for i in range(10):
        threads.append(Timer(interval=(begin_time - now).seconds, function=send_post, args=(infos, args.campus)))
    for thread in threads:
        thread.start()

    print("end..")


if __name__ == '__main__':
    main()
