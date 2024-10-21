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

if appconfig.server == 'aliyun':
    # 服务器使用
    caiji3.reList(1)
    caiji3.reList(2)
    caiji3.reList(3)
elif appconfig.server == 'local':
    # 本机调试用
    counter = 1
    while counter < 3600:
        caiji3.reList(1)
        caiji3.reList(2)
        caiji3.reList(3)
        counter = counter + 1
        # print(counter)
        time.sleep(2)