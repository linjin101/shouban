#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import appconfig
import time  # 引入time模块
import re  
import json
from urllib.parse import unquote_plus  
# 导入tushare
import array as arr
import random
import caiji3
import time
import datetime
import time

# python写程序判断日期在周一到周五之间，时间在9:20到15:00之间，循环print(1)
def is_weekday_and_time_range():
    # 获取当前日期和时间
    now = datetime.datetime.now()

    # 判断是否是周一到周五
    if now.weekday() < 5 and now.weekday() >= 0:  # Monday is 0 and Friday is 4
        # 将当前时间转换为时间对象，方便比较
        current_time = now.time()

        # 定义时间范围
        start_time = datetime.time(9, 20)
        end_time = datetime.time(15, 0)

        # 判断时间是否在范围内
        if start_time <= current_time <= end_time:
            return True
    return False

while True:
    if is_weekday_and_time_range():#True:
        caiji3.reStockListAll()
        # 为了避免过于频繁的打印，可以添加一个小延时（例如1秒）
        # time.sleep(1)
    else:
        # 如果不满足条件，可以暂停一小段时间再检查
        print('不在交易时间')
        # break

# if appconfig.server == 'aliyun':
#     # 服务器使用
#     caiji3.reList(1)
#     caiji3.reList(2)
#     caiji3.reList(3)
# elif appconfig.server == 'local':
#     # 本机调试用
#     counter = 1
#     while counter < 3600:
#         caiji3.reStockListAll()
#         # caiji3.reList(2)
#         # caiji3.reList(3)
#         counter = counter + 1
#         # time.sleep(1)
#         print(counter)
#     # print(counter)
