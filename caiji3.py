#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import appconfig
import time  # 引入time模块
import requests  
import re
from urllib.parse import unquote_plus  
# 导入tushare
import tushare as ts
import redis
import caijithsgl

# 目标URL  
# 上海
urlsh = 'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sh|A|desc|0|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'
urlsh2 = 'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sh|A|desc|31|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'
urlsh3 = 'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sh|A|desc|61|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'

# 深证
urlsz = 'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sz|A|desc|0|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'
urlsz2 = 'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sz|A|desc|31|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'
urlsz3 = 'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sz|A|desc|61|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'


# redis配置读取
r = redis.StrictRedis(host=appconfig.redishost, port=appconfig.redisport,password=appconfig.redispassword, db=appconfig.redisdbnum)
expire_time_in_seconds = 24 * 60 * 60 * 3  # 24小时 * 3天   
## redis涨停概念删除sadd对应

# redis涨停概念累加
def stockGLAdd(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天   

    # 尝试设置key的值，如果key不存在（NX）  
    if r.exists('GL:'+rdate):  
        # 如果key已存在，则累加  
        # 注意：这里并没有再次检查key的过期时间，因为设置过期时间和累加操作是分开的  
        # 在实际应用中，你可能需要设计一种机制来定期更新过期时间，或者接受一定的过期时间误差  
        r.sadd('GL:'+rdate,rstock)
        # 增加过期时间10天设置
        r.expire('GL:' + rdate, expire_time_in_seconds)
        ts_code_list = r.sunion('GL:'+rdate)
        # print('涨停概念：')
        # print(ts_code_list)
    else:
        r.sadd('GL:'+rdate,'')
        # 设置过期时间  
        r.expire('GL:'+rdate, expire_time_in_seconds)  


# redis删除涨停计数
def stockDel(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天 

    # 尝试设置key的值，如果key不存在（NX）  
    if r.setnx(rdate+':'+rstock, 0):  
        # 设置过期时间  
        r.expire(rdate+':'+rstock, expire_time_in_seconds)  
        # r.set(rdate+':'+rstock,0)
    else:  
        # 如果key已存在，则累加  
        # 注意：这里并没有再次检查key的过期时间，因为设置过期时间和累加操作是分开的  
        # 在实际应用中，你可能需要设计一种机制来定期更新过期时间，或者接受一定的过期时间误差  
        r.set(rdate+':'+rstock,0)
        # 增加过期时间10天设置
        r.expire(rdate+':'+rstock, expire_time_in_seconds)

def setStockList(stockList,listFlag):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天   

    r.set(listFlag,stockList)
    r.expire(listFlag, expire_time_in_seconds) 

# redis累加
def stockInc(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天   

    # 尝试设置key的值，如果key不存在（NX）  
    if r.setnx(rdate+':'+rstock, 1):  
        # 设置过期时间  
        r.expire(rdate+':'+rstock, expire_time_in_seconds)  
        # r.incrby(rdate+':'+rstock,1)
    else:  
        # 如果key已存在，则累加  
        # 注意：这里并没有再次检查key的过期时间，因为设置过期时间和累加操作是分开的  
        # 在实际应用中，你可能需要设计一种机制来定期更新过期时间，或者接受一定的过期时间误差  
        r.incrby(rdate+':'+rstock,1)
        r.expire(rdate + ':' + rstock, expire_time_in_seconds)

# 获取redis累加值 
def getStockInc(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    rvalue = r.get(rdate+':'+rstock)
    if rvalue is not None:  
        rvalue = int(rvalue.decode('utf-8'))
    return rvalue

# redis回封,破板4，回封5
def getStockHF(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    rvalue = r.get(rdate+':'+rstock+'HF')
    if rvalue is not None:  
        rvalue = int(rvalue.decode('utf-8'))
        return rvalue
    return 0

# redi回封,涨停3，破板4，回封5
def stockHF(rstock,rFlag):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天  

    # 尝试设置key的值，如果key不存在（NX）  
    if r.setnx(rdate+':'+rstock+'HF', rFlag):  
        # 设置过期时间  
        r.expire(rdate+':'+rstock+'HF', expire_time_in_seconds)  
        # r.set(rdate+':'+rstock+'HF',rFlag)
    else:  
        r.set(rdate+':'+rstock+'HF',rFlag)
        r.expire(rdate + ':' + rstock + 'HF', expire_time_in_seconds)

    # 回封次数获取
def getStockHFNum(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    rvalue = r.get('HF-'+rdate+':'+rstock)
    if rvalue is not None:
        rvalue = int(rvalue.decode('utf-8'))
        return rvalue
    return 0

# 回封次数保存
def setStockHFNum(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天
    # 尝试设置key的值，如果key不存在（NX）
    if r.setnx('HF-'+rdate+':'+rstock, 1):
        # 设置过期时间
        r.expire('HF-'+rdate+':'+rstock, expire_time_in_seconds)
    else:
        # 如果key已存在，则累加
        # 注意：这里并没有再次检查key的过期时间，因为设置过期时间和累加操作是分开的
        # 在实际应用中，你可能需要设计一种机制来定期更新过期时间，或者接受一定的过期时间误差
        r.incrby('HF-'+rdate+':'+rstock,1)
        r.expire('HF-' + rdate + ':' + rstock, expire_time_in_seconds)

# redis删除回封计数
def stockDelHFNum(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天

    # 尝试设置key的值，如果key不存在（NX）
    if r.setnx('HF-'+rdate+':'+rstock, 0):
        # 设置过期时间
        r.expire('HF-'+rdate+':'+rstock, expire_time_in_seconds)
        # r.set(rdate+':'+rstock,0)
    else:
        # 如果key已存在，则累加
        # 注意：这里并没有再次检查key的过期时间，因为设置过期时间和累加操作是分开的
        # 在实际应用中，你可能需要设计一种机制来定期更新过期时间，或者接受一定的过期时间误差
        r.set('HF-'+rdate+':'+rstock,0)
        r.expire('HF-' + rdate + ':' + rstock, expire_time_in_seconds)

# 破板价格保存
def setStockPb(rstock,sprice):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    # expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天  

    # 尝试设置key的值，如果key不存在（NX）  
    if r.setnx('PB-'+rdate+':'+rstock, sprice):  
        # 设置过期时间  
        r.expire('PB-'+rdate+':'+rstock, expire_time_in_seconds)  
        # r.set('PB-'+rdate+':'+rstock,sprice)
    else:  
        r.set('PB-'+rdate+':'+rstock,sprice)
        r.expire('PB-' + rdate + ':' + rstock, expire_time_in_seconds)

    # 获取破板当前价格
def getStockPb(rstock):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    sprice = r.get('PB-'+rdate+':'+rstock)
    if sprice is not None:  
        return sprice
    return 0

# 多个股票列表整理,股票代码加上.SZ .SH
def tscodelist(stocklist): 
    jys = '.SH'
    tscode = ''
    for item in stocklist[:]:  # 打印前10项  
        if item[0:2] == '60':
            jys = '.SH'
        elif item[0:2] == '68':
            jys = '.SH'
        elif item[0:2] == '00':
            jys = '.SZ'
        elif item[0:2] == '30':
            jys = '.SZ'
        tscode += item + jys + ','
    return tscode[0:-1]

# 多个股票列表，区间价格
def zrjg(ts_code,start_date,end_date):
    # 初始化pro接口
    pro = ts.pro_api('16fa068f73952f45f9e9c45ed0cd13d0f0f5aabc1112c4ac9ab956ec')
    #df = pro.daily(ts_code='000001.SZ', start_date='20180701', end_date='20180718')

    # 拉取数据
    #多个股票
    # df = pro.daily(ts_code='688515.SH,002168.SZ', start_date='20240718', end_date='20240718')
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    return df
    # print(df)

# 昨日涨停筛选排除
#       ts_code trade_date   open   high    low  close  pre_close  change  pct_chg        vol       amount
# 0   603232.SH   20240718   9.51   9.90   9.27   9.58       9.69   -0.11  -1.1352   41594.20    39418.510
# 1   688693.SH   20240718  29.00  29.68  27.83  29.30      29.31   -0.01  -0.0341   27866.42    80093.085
# 2   688515.SH   20240718  55.82  55.82  53.73  55.28      56.05   -0.77  -1.3738   10151.45    55557.888
# 3   605218.SH   20240718  15.00  15.01  14.36  14.73      15.05   -0.32  -2.1262   27842.00    40730.071
def zrzt(ts_zrjg):
    ts_zrjg = []
    # print(ts_zrjg['ts_code'][8],ts_zrjg['pct_chg'][8])
    for item in ts_zrjg['pct_chg']:  # 数组循环
        print (  ts_zrjg['pct_chg'] )
        if (  ts_zrjg['pct_chg'].astype(float) > 9.85):
            print(item['ts_code'],ts_zrjg['pct_chg'],ts_zrjg['trade_date'])
    return ts_zrjg

# 股票涨幅排行榜，首板、N格，回封，神秘里面概念，情绪，老鸭头切片，MA60
def szztpro( urlsh ):
    #返回涨停列表
    stockZtList1 = [] #接近涨停
    stockZtList2 = [] #10cm首板回封
    stockZtList3 = [] #20cm首板回封
    stockZtList4 = 0 # 涨幅<8用户采集循环截止标记
    stockZtList5 = []  # 连板
    stockZtList6 = []  # 10cm首板
    stockZtList7 = []  # 20cm首板
    strRepost = ''
    # 定义请求头  
    headers = {  
        'Accept': '*/*',  
        'Accept-Encoding': 'gzip, deflate',  
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',  
        'Connection': 'keep-alive',  
        'Cookie': 'Hm_lvt_08be8f13a5bc5a326158306b8930299f=2723381822; Qs_lvt_8880=2723381821; Qs_pv_8880=577795623916564500',
        'Host': 'hqdata.compass.cn',
        'Referer': 'http://xici.compass.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        # 注意：这里不应该包含实际的Cookie值，因为它们是用户特定的，  
        # 并且在这个例子中提供的是无效的或者过期的。  
        # 如果有必要，你应该在代码中安全地处理Cookie。  
        # 'Cookie': 'Hm_lvt_08be8f13a5bc5a326158306b8930299f=1723381822; Qs_lvt_8880=1723381822',  
        # 如果你有有效的Cookie，请在这里添加  
    }
    # 发送HTTP GET请求  
    response = requests.get(urlsh, headers=headers)
    # 检查请求是否成功  
    if response.status_code == 200:  
        # 获取HTML内容  
        html_content = response.text  
        # 使用正则表达式查找newSortPreData变量的值  
        # 注意：这个正则表达式假设newSortPreData被赋值为一个JSON格式的字符串  
        pattern = r'AJAJ_ON_READYSTATE_CHANGE\(\d+,(.*)\);0'  
        match = re.search(pattern, html_content, re.DOTALL)  
        # 获取股票排序列表Html
        jshtml = match.group(1)
        # 截取字符串前后字符
        jsHtmlJson = jshtml[10:-3].replace('\\"', '"').replace('\\\\', '\\').replace('\\', '')  

        # 使用正则表达式替换所有的'false'为'False'  
        fixed_str = re.sub(r'\bfalse\b', 'False', jsHtmlJson)  
        
        # 使用eval()解析修正后的字符串（注意：eval()在处理不受信任的输入时是不安全的）  
        data = eval(fixed_str)  
        # print(data)
        # print('-----------------------------------')
        # 格式化成2016-03-20 11:45:39形式
        # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        # strRepost += '|'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        i = 0
        iLine = 0
        for item in data[:]:  # 打印前10项  
            stockMcj = item[9] # 股票卖出价
            istockZf = item[10] # 股票涨幅数字
            stockZf = str(item[10])+'%' # 股票涨幅字符串%
            stockCode = item[0] # 股票代码
            stcokName =  unquote_plus(item[15]) # 股票中文名
            # 涨幅<8
            if item[10] < 8:
                stockZtList4 = 1
            
            if stockCode[4:6] == '30' or stockCode[4:6] == '68':
                 # 接近涨停价格
                stcokPriceNum  = 16
            else:
                # 接近涨停价格
                stcokPriceNum  = 8

            # 首板标识
            ztxs = caijithsgl.getStockTopBanRedis(stockCode[4:])
            # 接近涨停
            # if stockMcj == 0.0:
            # print(stockCode,stockZf,stcokPriceNum)
            if istockZf > stcokPriceNum and stockMcj != 0.0 and stcokName[0:2] != 'ST' and stcokName[0:3] != '*ST'  and stcokName[0:1] != 'C'   and stcokName[0:1] != 'N':
                if getStockHF(stockCode[4:]) == 3 or getStockHF(stockCode[4:]) == 5:
                    stockHF(stockCode[4:],4)
                    #破板设置4
                    # print ( '破板设置:'  )
                    # print(  getStockHF(stockCode[4:]) )
                elif getStockHF(stockCode[4:]) == 4: #破板价格存储
                    setStockPb(stockCode[4:],stockMcj)

                # 删除redis计数
                stockDel(stockCode[4:])
                # 破板累加
                stockInc(stockCode[4:]+'PB')

                if ztxs == '首板':
                    # 股票价格列表放到数组
                    stockZtList1.append( [ stockCode[4:],getStockInc(stockCode[4:]+'PB'),stcokName,stockZf,stockMcj] )
                    # print([ stockCode[4:],getStockInc(stockCode[4:]+'PB'),stcokName,stockZf,stockMcj])
                i = i + 1

            # 封板显示
            if stockMcj == 0.0 and ( stockCode[4:6] == '00' or stockCode[4:6] == '60' ) and stcokName[0:2] != 'ST' and stcokName[0:3] != '*ST'  and stcokName[0:1] != 'C'   and stcokName[0:1] != 'N':
                # 回封次数累加
                # 如果回封5
                if getStockHF(stockCode[4:]) == 4:
                    setStockHFNum(stockCode[4:])
                # 如果破板4,回封5
                if getStockHF(stockCode[4:]) == 4 or getStockHF(stockCode[4:]) == 5:
                    stockHF(stockCode[4:],5)
                    # print ( '回封设置:'  )
                    # print(  getStockHF(stockCode[4:]) )
                else:
                    stockHF(stockCode[4:],3)
                    
                # 涨停累加
                stockInc(stockCode[4:])
                # 删除破板redis计数
                stockDel(stockCode[4:]+'PB')
                # 涨停概念累加
                stockGLAdd(stockCode[4:])
                if ztxs == '首板' and getStockHF(stockCode[4:]) == 5: # 首板回封
                    stockZtList2.append( [ stockCode[4:],getStockInc(stockCode[4:]),stcokName,stockZf,stockMcj] )
                elif ztxs == '首板' and getStockHF(stockCode[4:]) == 3:
                    stockZtList6.append( [ stockCode[4:],getStockInc(stockCode[4:]),stcokName,stockZf,stockMcj] )
                else:
                    stockZtList5.append([stockCode[4:], getStockInc(stockCode[4:]), stcokName, stockZf, stockMcj])
                i = i + 1

            # 创业板显示 and stockCode[4:2] == '30' 
            if stockMcj == 0.0 and ( stockCode[4:6] == '30' or stockCode[4:6] == '68' ) and stcokName[0:2] != 'ST' and stcokName[0:3] != '*ST'  and stcokName[0:1] != 'C'   and stcokName[0:1] != 'N':
                # 回封次数累加
                # 如果回封5
                if getStockHF(stockCode[4:]) == 4:
                    setStockHFNum(stockCode[4:])
                # 如果破板4,回封5
                if getStockHF(stockCode[4:]) == 4 or getStockHF(stockCode[4:]) == 5:
                    stockHF(stockCode[4:],5)
                    # print ( '回封设置:'  )
                    # print(  getStockHF(stockCode[4:]) )
                else:
                    stockHF(stockCode[4:],3)

                # 涨停累加
                stockInc(stockCode[4:])
                # 删除破板redis计数
                stockDel(stockCode[4:] + 'PB')
                # 涨停概念累加
                stockGLAdd(stockCode[4:])
                if ztxs == '首板' and getStockHF(stockCode[4:]) == 5: # 首板回封
                    stockZtList3.append( [ stockCode[4:],getStockInc(stockCode[4:]),stcokName,stockZf,stockMcj] )
                elif ztxs == '首板' and getStockHF(stockCode[4:]) == 3:
                    stockZtList7.append( [ stockCode[4:],getStockInc(stockCode[4:]),stcokName,stockZf,stockMcj] )
                else:
                    stockZtList5.append([stockCode[4:], getStockInc(stockCode[4:]), stcokName, stockZf, stockMcj])

                i = i + 1
    else:  
        print("请求失败，状态码：", response.status_code)
    # 涨停列表
    stockZtList = [stockZtList1,stockZtList2,stockZtList3,stockZtList4,stockZtList5,stockZtList6,stockZtList7]
    # print('################')
    # print(stockZtList[0])
    # print(stockZtList[1])
    # print(stockZtList[2])
    # print(stockZtList[3])
    # print('################')
    return stockZtList

def reStockListAll():
    stockListHtml1 =''
    stockListHtml2 = ''
    stockListHtml3 = ''
    stockListHtml4 = ''
    stockListHtml5 = ''
    stockListHtml6 = ''

    # 上海涨幅排行榜
    urlsh1 =  'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sh|A|desc|'
    urlsh2 = '|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'
    shlist = reStockList(urlsh1,urlsh2)

    # 深圳涨幅排行榜
    stockListArrSz2 = []
    urlsz1 =  'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sz|A|desc|'
    urlsz2 = '|30|ratio|0.5567433334567789961&crossdomain=1341454252487098&from=xici.compass.cn'
    szlist = reStockList(urlsz1, urlsz2)

    stockListHtml1 = reListpro(shlist[0]+szlist[0])
    stockListHtml2 = reListpro(shlist[1]+szlist[1])
    stockListHtml3 = reListpro(shlist[2]+szlist[2])

    stockListHtml4 = reListpro(shlist[3] + szlist[3])

    stockListHtml5 = reListpro(shlist[4] + szlist[4])
    stockListHtml6 = reListpro(shlist[5] + szlist[5])

    # print(stockListHtml1)
    # print(stockListHtml2)
    # print(stockListHtml3)
    # stock列表存放redis
    setStockList(stockListHtml1,1)
    setStockList(stockListHtml2,2)
    setStockList(stockListHtml3,3)

    setStockList(stockListHtml4, 4)
    setStockList(stockListHtml5, 5)
    setStockList(stockListHtml6, 6)

    # print('1:'+stockListHtml1)
    # print('2:'+stockListHtml2)
    # print('3:'+stockListHtml3)
    # print('\r\n')

# 61,63涨幅排行榜
def reStockList(url1,url2):
    stockListArr = []
    stockListArrSh1 = []
    stockListArrSh2 = []
    stockListArrSh3 = []
    stockListArrSh4 = []
    stockListArrSh5 = []
    stockListArrSh6 = []
    i = 0
    while i <= 330:
        urlsh = url1 + str(i) + url2
        # print(urlsh)
        stockListArr = szztpro(urlsh)
        stockListArrSh1 += stockListArr[0]
        stockListArrSh2 += stockListArr[1]
        stockListArrSh3 += stockListArr[2]

        stockListArrSh4 += stockListArr[4]
        stockListArrSh5 += stockListArr[5]
        stockListArrSh6 += stockListArr[6]

        if stockListArr[3] == 1:
            # print('涨幅<8')
            break
        i += 30
    return [stockListArrSh1,stockListArrSh2,stockListArrSh3,stockListArrSh4,stockListArrSh5,stockListArrSh6]
    # print('#################################################')
    # print(stockListArrSh1+stockListArrSh2+stockListArrSh3)

    # stockListHtml1 += reListpro(stockListArrSh1)
    # stockListHtml2 += reListpro(stockListArrSh2)
    # stockListHtml3 += reListpro(stockListArrSh3)
    #
    # # stock列表存放redis
    # setStockList(stockListHtml1,1)
    # setStockList(stockListHtml2, 2)
    # setStockList(stockListHtml3, 3)


def reListpro(stockArr):
    stockZtListOut = sorted(stockArr, key=lambda x:x[1] )  
    stockListHtml = ''
    iColore = 0
    for stockInfo in stockZtListOut[:]:
        iColorLine = '<font color="#FFFFFF">'
        if iColore == 0:
            iColorLine = '<font color="#FF0000">'
        if iColore == 1:
            iColorLine = '<font color="#E74F4C">'
        if iColore == 2:
            iColorLine = '<font color="#FFD700">'
 
        # 破板和回封
        stockHF = ''
        # 回封次数
        stockHFNum = ''
        stockRdHF = getStockHF(stockInfo[0])
        stcokHFColor = '80D34B' # 绿色
        # print(stockRdHF)
        if stockRdHF == 4:
            stockHF = '破'
            stcokHFColor = '#80D34B' # 绿色
        elif stockRdHF == 5:
            stockHF = '回封'
            stcokHFColor = '#FF0000' # 红色
            # 回封次数获取
            if str(getStockHFNum(stockInfo[0])) != '0':
                stockHFNum = str(getStockHFNum(stockInfo[0]))

        # print(stockInfo)
        #  破板状态上升
        stockPbzt = ''
        if stockInfo[0] != 0.0 and getStockPb(stockInfo[0]) !=0:
            if float(stockInfo[0]) > float(getStockPb(stockInfo[0])):
                stockPbzt = '↑'
            else:
                stockPbzt = '↓'
        # k线 深圳的添加sz
        stockCode = stockInfo[0]
        if stockCode[0:2] == '30' or stockCode[0:2] == '00' :
            kx = ' <a id="'+stockCode+'" target="_blank" style="color: #ff0000;" href="https://quote.eastmoney.com/sz'+stockCode+'.html#fullScreenChart">k线</a>'
        else:
            kx = ' <a id="'+stockCode+'" target="_blank" style="color: #ff0000;" href="https://quote.eastmoney.com/kcb/'+stockCode+'.html#fullScreenChart">k线</a>'
        # 首板标识
        ztxs = caijithsgl.getStockTopBanRedis(stockInfo[0])
        # 概念
        stockGl = caijithsgl.getStockGlRedis(stockInfo[0])
        if ztxs == '首板':
            stockListHtml += iColorLine + '<b>'+str(stockInfo[0])+'</b>'+','+str(stockInfo[1])+','+str(stockInfo[2])+','+str(stockInfo[3])+ '</font> <font color="#FF0000"><b> '+ztxs+' </b></font>'+'<font color="'+stcokHFColor+'"><b> '+stockHF+'</b></font> <font color="FF00FF">'+stockHFNum+'</font> '+stockPbzt+stockGl+kx+' <br>'
            # print(str(stockInfo[0])+':'+ztxs+'=>'+stockGl)
            iColore = iColore + 1
        else:
            stockListHtml += iColorLine + '<b>'+str(stockInfo[0])+'</b>'+','+str(stockInfo[1])+','+str(stockInfo[2])+','+str(stockInfo[3])+ '</font> <font color="#006400"><b> '+ztxs+' </b></font>'+'<font color="'+stcokHFColor+'"><b> '+stockHF+'</b></font> <font color="FF00FF">'+stockHFNum+'</font> '+stockPbzt+stockGl+kx+' <br>'
            # print(str(stockInfo[0])+':'+ztxs+'=>'+stockGl)
            # iColore = iColore + 1




    return stockListHtml

# 返回redis的列表
def getStockList(dbType):
    return r.get(dbType)

 
# 返回redis的列表
def getStockListAll():
    response_data_json = {1:'',2:'',3:'',4:'',5:'',6:''}
    response_data_json[1] = (r.get(1)).decode('utf-8')
    response_data_json[2] = (r.get(2)).decode('utf-8')
    response_data_json[3] = (r.get(3)).decode('utf-8')

    response_data_json[4] = (r.get(4)).decode('utf-8')
    response_data_json[5] = (r.get(5)).decode('utf-8')
    response_data_json[6] = (r.get(6)).decode('utf-8')
    return response_data_json

# print( getStockListAll() )

# reList(1)
# reList(2)
# reList(3)

# print( reList(1)  )
# print( reList(2)  )
# print( reList(3)  )
# reList(3)
# print(  )
# reList(3)

# print('---------------------------------------------------')
# stockZtList1 = sorted(stockZtList1, key=lambda x: (x[1], x[0]))  
# print(stockZtList1)
# print('---------------------------------------------------')
# stockZtList2 = sorted(stockZtList2, key=lambda x: (x[1], x[0]))  
# print(stockZtList2)
# print('---------------------------------------------------')
# stockZtList3 = sorted(stockZtList3, key=lambda x: (x[1], x[0]))  
# print(stockZtList3)
# print('---------------------------------------------------')