#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

#sina行情采集
def fetch_stock_increase_ranking(url):  
    headers = {  
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'  
    }  
      
    try:  
        response = requests.get(url, headers=headers)  
        response.raise_for_status()  # 如果响应状态码不是200，则抛出HTTPError异常  
          
        data = response.json()  # 解析JSON数据  
          
        # 假设返回的JSON数据中有一个名为'data'的键，它包含了股票数据  
        # 注意：这里的键名（如'data'）需要根据实际返回的JSON结构来确定  
        return data
               
    except requests.RequestException as e:  
        print(f"请求出错: {e}")  

# redis删除涨停计数
def stockDel(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )    
    r.delete(rdate+':'+rstock)

# redis累加
def stockInc(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    expire_time_in_seconds = 24 * 60 * 60  # 48小时  

    # 尝试设置key的值，如果key不存在（NX）  
    if r.setnx(rdate+':'+rstock, 1):  
        # 设置过期时间  
        r.expire(rdate+':'+rstock, expire_time_in_seconds)  
        r.incrby(rdate+':'+rstock,1)
    else:  
        # 如果key已存在，则累加  
        # 注意：这里并没有再次检查key的过期时间，因为设置过期时间和累加操作是分开的  
        # 在实际应用中，你可能需要设计一种机制来定期更新过期时间，或者接受一定的过期时间误差  
        r.incrby(rdate+':'+rstock,1)

# 获取redis累加值 
def getStockInc(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    rvalue = r.get(rdate+':'+rstock)
    if rvalue is not None:  
        rvalue = int(rvalue.decode('utf-8'))
    return rvalue

#股票列表数据输出
def stock_list(stock_data):
    stock_list = stock_data
    #即将涨停列表
    stockJJList = []
    #涨停主板列表
    stockZtzbList = []
    #涨停科创业列表
    stockZtckList = []
    #涨停列表整体返回
    stockReData = []
    i = 1
    for stock in stock_list:  
    # 假设每个股票数据包含'symbol'（股票代码）、'name'（股票名称）和'changepercent'（涨幅）等字段  
    # 注意：这里的字段名（如'symbol', 'name', 'changepercent'）需要根据实际返回的JSON结构来确定  
        # 股票代码
        stockCode = stock['symbol'][2:8]
        # 股票名称  涨停 and stock['sell'] == '0.000'
        stcokName = stock['name']
        # 涨幅
        stockZf = float(stock['changepercent'])
        # 卖价
        stockMj = float(stock['sell'])
        if stcokName[0:1] != 'N' and stcokName[0:1] != 'C' and stcokName[0:2] != 'ST'  and stcokName[0:3] != '*ST' and ( stockCode[0:1] == '0'  or stockCode[0:1] == '3'  or stockCode[0:1] == '6') and stockZf > 8 :
            # 即将涨停深沪主板列表放到数组
            if  (stockCode[0:2] == '60' or  stockCode[0:2] == '00') and  stockZf > 9 and stock['sell'] != '0.000':
                stockDel(stockCode)
                stockJJList.append( [ stockCode,'X',stcokName,stockZf] )
            # 即将涨停创业、科创板列表放到数组
            elif  (stockCode[0:2] == '30' or  stockCode[0:2] == '68') and  stockZf > 18 and stock['sell'] != '0.000':
                stockDel(stockCode)
                stockJJList.append( [ stockCode,'X',stcokName,stockZf] )
            
            # 涨停沪深主板列表放到数组
            elif  (stockCode[0:2] == '60' or  stockCode[0:2] == '00') and stock['sell'] == '0.000':
                stockInc(stockCode)
                stockZtzbList.append( [ stockCode,getStockInc(stockCode),stcokName,stockZf] )
            # 涨停创业、科创板列表放到数组
            elif  (stockCode[0:2] == '30' or  stockCode[0:2] == '68') and stock['sell'] == '0.000':
                stockInc(stockCode)
                stockZtckList.append( [ stockCode,getStockInc(stockCode),stcokName,stockZf] )
            else:
                # 删除redis缓存
                stockDel(stockCode)

            # print(f"序号:{i} , 股票代码:{stock['symbol'][2:8]} , 股票名称:{stock['name'].ljust(6)}, 涨幅:{stock['changepercent']}%, 卖价:{stock['sell']}, 开盘:{stock['open']}, 高:{stock['high']}, 低:{stock['low']},")
            i = i + 1

    # 根据封板时间倒序
    stockJJList = sorted(stockJJList, key=lambda x:x[1] )  
    stockZtzbList = sorted(stockZtzbList, key=lambda x:x[1] )  

    # 即将涨停,涨停主板，涨停创业、科创板
    stockReData  = [stockJJList,stockZtzbList,stockZtckList]

    # print('\r\n')
    # # print(stockJJList)
    # print(stockReData[0])
    # print('\r\n')
    # print(stockReData[1])
    # print('\r\n')
    # print(stockReData[2])

    return stockReData

# 输出加了html标签的列表
def reList( ): 
    # js列表 https://vip.stock.finance.sina.com.cn/mkt/js/stock_list_cn.js?ts=202002271549
    # sian财经行情全部A股
    url1 = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=100&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init'

    url2 = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=2&num=100&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init' 

    url3 = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=3&num=100&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init' 

    stock_data_300 = fetch_stock_increase_ranking(url1)+fetch_stock_increase_ranking(url2)+fetch_stock_increase_ranking(url3)

    stockReData = stock_list(stock_data_300) 
 
    # 所有html列表
    stockListHtmlAll = []
    
    ###即将涨停
    stockListHtml = ''
    iColore = 0
    stockJJList = stockReData[0]
    
    for stockInfo in stockJJList[:]:
        
        iColorLine = '<font color="#FFFFFF">'
        if iColore == 0:
            iColorLine = '<font color="#FF0000">'
        if iColore == 1:
            iColorLine = '<font color="#FF4500">'
        if iColore == 2:
            iColorLine = '<font color="#FFD700">'
        stockListHtml += iColorLine + str(stockInfo[0])+','+str(stockInfo[1])+','+str(stockInfo[2])+','+str(stockInfo[3])+ '</font>' +' ↑ <br>'
        iColore = iColore +1
    stockListHtmlAll.append(stockListHtml) 

    ###主板涨停
    stockListHtml = ''
    iColore = 0
    stockZtzbList = stockReData[1]
    
    for stockInfo in stockZtzbList[:]:
        
        iColorLine = '<font color="#FFFFFF">'
        if iColore == 0:
            iColorLine = '<font color="#FF0000">'
        if iColore == 1:
            iColorLine = '<font color="#FF4500">'
        if iColore == 2:
            iColorLine = '<font color="#FFD700">'
        stockListHtml += iColorLine + str(stockInfo[0])+','+str(stockInfo[1])+','+str(stockInfo[2])+','+str(stockInfo[3])+ '</font>' +' ↑ <br>'
        iColore = iColore +1
    stockListHtmlAll.append(stockListHtml) 

    ###创业、科创版涨停
    stockListHtml = ''
    iColore = 0
    stockZtckList = stockReData[1]
    
    for stockInfo in stockZtckList[:]:
        
        iColorLine = '<font color="#FFFFFF">'
        if iColore == 0:
            iColorLine = '<font color="#FF0000">'
        if iColore == 1:
            iColorLine = '<font color="#FF4500">'
        if iColore == 2:
            iColorLine = '<font color="#FFD700">'
        stockListHtml += iColorLine + str(stockInfo[0])+','+str(stockInfo[1])+','+str(stockInfo[2])+','+str(stockInfo[3])+ '</font>' +' ↑ <br>'
        iColore = iColore +1
    stockListHtmlAll.append(stockListHtml) 
    
    return stockListHtmlAll




# sian财经行情 上证A股
# url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=100&sort=changepercent&asc=0&node=sh_a&symbol=&_s_r_a=init'  

# sian财经行情 深证A股
# url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=100&sort=changepercent&asc=0&node=sz_a&symbol=&_s_r_a=init'  

# sina财经行情 创业板
# url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=80&sort=changepercent&asc=0&node=cyb&symbol=&_s_r_a=sort'

# sina财经行情 科创板
# url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=80&sort=changepercent&asc=0&node=kcb&symbol=&_s_r_a=sort'

# stock_data_300 = fetch_stock_increase_ranking(url1)+fetch_stock_increase_ranking(url2)+fetch_stock_increase_ranking(url3)

# stock_list_str = stock_list(stock_data_300) 
# stock_list_str_re = reList( stock_list_str )
# print( stock_list_str_re[2] )

# redis连接
r = redis.StrictRedis(host='localhost', port=6379, db=0)
print(reList())


# C:\Python\project\daban>python caijisina.py
# 股票代码: bj832802, 股票名称: 保丽洁, 涨幅: 22.871%
# 股票代码: sz300187, 股票名称: 永清环保, 涨幅: 20.048%
# 股票代码: sz300639, 股票名称: 凯普生物, 涨幅: 20.042%
# 股票代码: sz301288, 股票名称: 清研环境, 涨幅: 20.033%
# 股票代码: sz300147, 股票名称: 香雪制药, 涨幅: 20.023%
# 股票代码: sz300875, 股票名称: 捷强装备, 涨幅: 19.99%
# 股票代码: sz300436, 股票名称: 广生堂, 涨幅: 19.978%
# 股票代码: sz301060, 股票名称: 兰卫医学, 涨幅: 19.95%
# 股票代码: sz300622, 股票名称: 博士眼镜, 涨幅: 19.855%
# 股票代码: sz300013, 股票名称: *ST新宁, 涨幅: 19.231%
# 股票代码: bj832145, 股票名称: 恒合股份, 涨幅: 16.736%
# 股票代码: sz300204, 股票名称: 舒泰神, 涨幅: 16.45%
# 股票代码: sz300256, 股票名称: 星星科技, 涨幅: 13.942%
# 股票代码: bj830946, 股票名称: 森萱医药, 涨幅: 13.69%
# 股票代码: sz300854, 股票名称: 中兰环保, 涨幅: 13.641%
# 股票代码: sz300261, 股票名称: 雅本化学, 涨幅: 13.406%
# 股票代码: sz301075, 股票名称: 多瑞医药, 涨幅: 12.008%
# 股票代码: sz300471, 股票名称: 厚普股份, 涨幅: 11.856%
# 股票代码: sz301399, 股票名称: 英特科技, 涨幅: 10.635%
# 股票代码: sz300149, 股票名称: 睿智医药, 涨幅: 10.297%