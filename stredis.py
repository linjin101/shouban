import appconfig
import time  # 引入time模块
import requests  
import re  
import json
from urllib.parse import unquote_plus  
# 导入tushare
import tushare as ts
import array as arr
import random
import redis
import caijithsgl

# redis配置读取
r = redis.StrictRedis(host=appconfig.redishost, port=appconfig.redisport,password=appconfig.redispassword, db=appconfig.redisdbnum)

# pro = ts.realtime_list('16fa068f73952f45f9e9c45ed0cd13d0f0f5aabc1112c4ac9ab956ec')


'''
#东财数据
df = ts.realtime_list(src='dc')
print( type(df) )
print("\n按行遍历:")  
i = 0
for index, row in df.iterrows():  
    if i < 5:
        print(f"Index: {index}")  
        print(f"Row data: {row['NAME']}")
        i = i + 1
'''
def addone(ts_gl,stockGL):
    if ts_gl in stockGL:
        stockGL[ts_gl] += 1
    else:
        stockGL[ts_gl] = 1

rdate = time.strftime( "%Y-%m-%d", time.localtime() )

stockGL = {}
rvalue = r.keys(rdate+':*')
for item in rvalue:
    strStock = str(item)
    ts_code = strStock[13:19]
    # print( strStock[13:19])
    ts_gl = r.get('stockGL:'+ts_code).decode('utf-8') 
    # print(ts_gl)
    addone(ts_gl,stockGL)
# 排序数据  
stockGL = sorted(stockGL.items(), key=lambda item: item[1], reverse=True)  

for strGL in stockGL:
    print(strGL)
 