import appconfig
import redis
import time  # 引入time模块
import requests  
from bs4 import BeautifulSoup
import mysql.connector  
from mysql.connector import Error


# redis配置读取
r = redis.StrictRedis(host=appconfig.redishost, port=appconfig.redisport,password=appconfig.redispassword, db=appconfig.redisdbnum)


def hy_str(s):
    # s = "计算机 -- IT服务Ⅱ -- IT服务Ⅲ （共117家）"  
  
    # 1. 去掉所有空格  
    s_no_spaces = s.replace(" ", "")  
    
    # 2. 去掉包括“（”及其后面的所有字符串  
    # 这里我们找到“（”的位置，并截取它之前的所有内容  
    index_of_bracket = s_no_spaces.find("（")  
    if index_of_bracket != -1:  # 如果找到了“（”  
        s_no_bracket_and_spaces = s_no_spaces[:index_of_bracket]  
    else:  
        s_no_bracket_and_spaces = s_no_spaces  # 如果没有找到“（”，则整个字符串都不变  
    
    # 3. 替换“--”为“,”  
    # 注意：由于之前已经去掉了空格，所以这里直接替换“--”即可  
    final_string = s_no_bracket_and_spaces.replace("--", ",")  
    
    return final_string  # 输出: 计算机,IT服务Ⅱ,IT服务Ⅲ
  
# 行业采集
def fetch_span_content(url):  
    headers = {  
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'  
    }  
    try:  
        response = requests.get(url, headers=headers)  
        response.raise_for_status()  # 如果响应状态码不是200，则抛出HTTPError异常  
          
        # 尝试显式指定UTF-8编码（尽管requests通常会这样做）  
        response.encoding = 'gbk'  
          
        # 解析HTML  
        soup = BeautifulSoup(response.text, 'html.parser')  
          
        # 查找<span class="tip f14">标签  
        span_tag = soup.find('span', class_='tip f14')  
        if span_tag:  
            # 获取并打印标签内的文本内容  
            content = span_tag.get_text(strip=True)  
            stockHy = hy_str(content)
            # print("找到的内容:", content)  
        # else:  
            # print("未找到<span class='tip f14'>标签")  
              
    except requests.RequestException as e:  
        print(e)  
    return stockHy

#概念采集
def fetch_concept_names(url):  
    conceptList = ""
    headers = {  
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'  
    }
    try:  
        # 发送HTTP GET请求
        response = requests.get(url, headers=headers)
        # 尝试显式指定UTF-8编码（尽管requests通常会这样做）  
        response.encoding = 'gbk'  
       
        # 检查请求是否成功  
        if response.status_code != 200:  
            print("Failed to retrieve the page")  
            return []  
        
        # 使用BeautifulSoup解析HTML  
        soup = BeautifulSoup(response.text, 'html.parser')  
        
        # 查找包含概念名称的表格行  
        # 注意：这里假设概念名称位于表格的<td>标签内，并且表格有特定的类或ID（这里需要根据实际HTML结构调整）  
    
       # 查找所有class为"gnName"的<td>标签  
        concept_names = soup.find_all('td', class_='gnName')  
    
        # 提取并打印概念名称  
        for concept in concept_names:  
            # 去除标签内的额外空格和换行符  
            clean_name = concept.get_text(strip=True)  
            conceptList +=  clean_name +  "," 

    except requests.RequestException as e:  
        print(e)  
    return conceptList  
  
def fetch_concept(ts_code):
    # 行业采集地址
    url = 'https://basic.10jqka.com.cn/'+ts_code+'/field.html'  
    concept_span = fetch_span_content(url)
    # print( fetch_span_content(url) )

    # 概念采集地址
    url = 'https://basic.10jqka.com.cn/'+ts_code+'/concept.html'  
    concept_names = fetch_concept_names(url)  
    # print(concept_names)  
    fetch_concept_list = str(concept_names) + str(concept_span)
    return fetch_concept_list

#######################################################################################################
def connect_to_mysql():  
    try:  
        connection = mysql.connector.connect(  
            host=appconfig.host,         # MySQL服务器地址  
            database=appconfig.database, # 数据库名  
            user=appconfig.username,     # 数据库用户名  
            password=appconfig.password  # 数据库密码  
        )  
        print(appconfig.host+'-'+appconfig.database+'-'+appconfig.username+'-'+appconfig.password)

        if connection.is_connected():  
            db_Info = connection.get_server_info()  
            print(f"Connected to MySQL Server version {db_Info}")  
            print("成功连接到MySQL数据库")  
            return connection  
        else:  
            print("连接失败")  
    except Error as e:  
        print(f"连接错误: {e}")  
# 查询
def execute_search(connection, query):
    if connection.is_connected():  
        cursor = connection.cursor(dictionary=True)  # 使用字典游标以便获取结果作为字典  
        # 执行SQL查询  
        cursor.execute(query)  
        # 获取查询结果  
        result = cursor.fetchone()  # fetchone() 获取查询结果的第一行，或者你可以使用 fetchall() 获取所有行  
        # 处理查询结果  
        # if result:  
        #     print(f"The first concept is: {result['first_concept']}")  
        # else:  
        #     print("No result found for the given ts_code.")
    return result

# 查询All
def execute_searchall(connection, query):
    if connection.is_connected():  
        cursor = connection.cursor(dictionary=True)  # 使用字典游标以便获取结果作为字典  
        # 执行SQL查询  
        cursor.execute(query)  
        # 获取查询结果  
        result = cursor.fetchall()  # fetchone() 获取查询结果的第一行，或者你可以使用 fetchall() 获取所有行  
        # 处理查询结果  
        # if result:  
        #     print(f"The first concept is: {result['first_concept']}")  
        # else:  
        #     print("No result found for the given ts_code.")
    return result
  
def execute_query(connection, query, params=None):  
    cursor = connection.cursor()  
    try:  
        if params:  
            cursor.execute(query, params)  
        else:  
            cursor.execute(query)  
        # cursor.execute(query)  
        # connection.commit()  
        return cursor.fetchall()  
    except Error as e:  
        print(f"执行查询错误: {e}")  
    # finally:  
    #     if connection.is_connected():  
    #         cursor.close()  
    #         connection.close()  

def execute_insert(connection, query, params=None):  
    cursor = connection.cursor()  
    try:  
        cursor.execute(query,params)  
        connection.commit()  
    except Error as e:  
        print(f"执行查询错误: {e}") 
    finally:  
        if connection.is_connected():  
            cursor.close()  


def fetch_concept_caiji():  
    connection = connect_to_mysql()  
    if connection:  
        # 查询最新的trade_date和对应的ts_code  
        # query = f"""
        # SELECT left(sd.ts_code, 6) as ts_code, sd.trade_date  
        # FROM `stock_data` sd  
        # WHERE sd.trade_date = (SELECT MAX(sd2.trade_date) FROM `stock_data` sd2)  
        # """  

        query = f"""
        select * from (
            SELECT left(sd.ts_code, 6) as ts_code, sd.trade_date  
            FROM `stock_data` sd  
            WHERE sd.trade_date = (SELECT MAX(sd2.trade_date) FROM `stock_data` sd2)  
            ) ts
            where ts.ts_code not in (select sc.ts_code from stock_concepts sc   ) 
        """

        results = execute_query(connection, query)  
        print(results)
          
        if results:  
            for row in results: 
                # 假设我们只处理第一个结果（如果有多个结果，可以循环处理）  
                # ts_code, trade_date = results[0]  
                ts_code, trade_date = row
                # 采集判断同花顺概念+行业
                concepts = fetch_concept(ts_code)
                trade_date = trade_date.strftime('%Y-%m-%d')  

                # 插入到stock_concepts表  
                insert_query = """  
                INSERT INTO `stock_concepts` (`ts_code`, `trade_date`, `concepts`)  
                VALUES (%s, %s,  %s)  
                """  
                
                val = (ts_code, trade_date,concepts)  
                print(insert_query)
                print(val)
                execute_insert(connection, insert_query, val)  
                print(f"成功插入 {ts_code} 到 stock_concepts 表，trade_date: {trade_date},concepts:{concepts}")  
            else:  
                print("没有找到结果")  
  
        connection.close()  

def getStockGl(ts_code):
    stockGL = ''
    connection = connect_to_mysql()  
    if connection:  
        query = f"""
        SELECT SUBSTRING_INDEX(sc.concepts, ',', 1) as stockGL FROM `stock_concepts` sc where sc.ts_code = '{ts_code}'
        """
        results = execute_search(connection, query)  
        # print(results)
        stockGL = results['stockGL']
        # if results:  
        #     stockGL = results[0]
        #     print(stockGL)
        connection.close()

# 判断昨日涨停
def getStockGlRedis(ts_code):
    stockGL = r.get('stockGL:'+ts_code)
    # 如果 my_value 是字节串，则进行解码  
    if stockGL is not None:
        if isinstance(stockGL, bytes):  
            stockGL = stockGL.decode('utf-8')  # 使用 UTF-8 编码进行解码 
        return stockGL
    return ''

# 设置概念到redis
def setStockGlRedis():
    connection = connect_to_mysql()  
    if connection:  
        query = f"""
        SELECT ts_code, SUBSTRING_INDEX(concepts, ',', 1) as stockGL FROM `stock_concepts`
        """
        results = execute_searchall(connection, query)  

        if results:  
            for row in results: 
                ts_code = row['ts_code']
                stockGL = row['stockGL']
                print(ts_code+':'+stockGL)
                rdate = time.strftime( "%Y-%m-%d", time.localtime() )
                expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天   
                r.set('stockGL:'+ts_code,stockGL)
                # r.expire('', expire_time_in_seconds)
        connection.close()
# 删除昨日涨停列表到redis
def delStockTopBanList():
    keys = r.keys('zrzt:*')
    if keys:
        r.delete(*keys)

# 设置昨日涨停列表到redis
def setStockTopBanList(ts_code,pct_chg,topban_date):
    rdate = time.strftime( "%Y-%m-%d", time.localtime() )
    expire_time_in_seconds = 24 * 60 * 60 * 10  # 24小时 * 10天   

    r.set('zrzt:'+ts_code,topban_date+':'+pct_chg)
    # r.expire('zrzt:'+ts_code, expire_time_in_seconds)

# 判断昨日涨停
def getStockTopBanRedis(ts_code):    
    # 尝试设置key的值，如果key不存在就是首板
    if r.exists('zrzt:'+ts_code):
        return '连板'
    return '首板'

#返回当天所有首板股票代码
def setStockTopBanToRedis(iday):
    connection = connect_to_mysql()  
    if connection:  
        query = f"""
        SELECT DATE_FORMAT(latest_trade.trade_date, '%Y-%m-%d') as topban_date,left(sd.ts_code,6) as ts_code,
CONCAT(sd.pct_chg,'') as pct_chg
        FROM stock_data sd  
        JOIN (  
            SELECT trade_date  
            FROM stock_data  
            WHERE trade_date = CURRENT_DATE()-{iday}
             ORDER BY trade_date DESC  
            LIMIT 1  
        ) latest_trade ON sd.trade_date = latest_trade.trade_date  
        WHERE (  
            (LEFT(sd.ts_code, 2) = '60' AND ROUND(sd.pre_close * 1.1, 2) = ROUND(sd.close,2) )  
            OR  
            (LEFT(sd.ts_code, 2) = '00' AND ROUND(sd.pre_close * 1.1, 2) = ROUND(sd.close,2))  
            OR  
            (LEFT(sd.ts_code, 2) = '30' AND ROUND(sd.pre_close * 1.2, 2) = ROUND(sd.close,2))
            OR  
            (LEFT(sd.ts_code, 2) = '68' AND ROUND(sd.pre_close * 1.2, 2) = ROUND(sd.close,2))  
        )  
        AND sd.high = sd.close  
        AND sd.pct_chg > 9  
        order by sd.pct_chg desc
        """
        # 删除M60之外的数据
        delquery = f"""
        
            DELETE FROM stock_data
            WHERE trade_date NOT IN ( select t.trade_date from  (
                            SELECT trade_date 
                    FROM stock_data 
                    GROUP BY trade_date
                    ORDER BY trade_date DESC
                            limit 0,60
            ) as t  )
        """

        results = execute_searchall(connection, query)
        # 删除MA60之外
        execute_insert(connection, delquery)
        print('删除MA60之外')
        # 先删除后添加
        delStockTopBanList()
        if results:  
            for row in results: 
                # print(row)
                # ts_code, pct_chg = row
                setStockTopBanList(row['ts_code'],row['pct_chg'],row['topban_date'])
        
        # if results is not None:
        #     stockTopBan = results['pct_chg']
        connection.close()
    return results


# 首板判断，需要改进多个股票判断
def getStockTopBan(ts_code):
    stockTopBan = 0
    if ts_code[0:2] == '30' or ts_code[0:2] == '68':
        ts_code = ts_code + '.SZ'
    if ts_code[0:2] == '60' or ts_code[0:2] == '00':
        ts_code = ts_code + '.SH'

    connection = connect_to_mysql()  
    if connection:  
        query = f"""
        SELECT sd.pct_chg as pct_chg
        FROM stock_data sd  
        JOIN (  
            SELECT trade_date  
            FROM stock_data  
            WHERE trade_date < CURRENT_DATE()  
            AND ts_code = '{ts_code}'  
            ORDER BY trade_date DESC  
            LIMIT 1  
        ) latest_trade ON sd.trade_date = latest_trade.trade_date  
        WHERE (  
            (LEFT(sd.ts_code, 2) = '60' AND ROUND(sd.pre_close * 1.1, 2) = sd.close)  
            OR  
            (LEFT(sd.ts_code, 2) = '00' AND ROUND(sd.pre_close * 1.1, 2) = sd.close)  
            OR  
            (LEFT(sd.ts_code, 2) = '30' AND ROUND(sd.pre_close * 1.2, 2) = sd.close)
            OR  
            (LEFT(sd.ts_code, 2) = '68' AND ROUND(sd.pre_close * 1.2, 2) = sd.close)  
        )  
        AND sd.high = sd.close  
        AND sd.pct_chg > 9  
        AND sd.ts_code = '{ts_code}'
        """
        results = execute_search(connection, query)  
        if results is not None:
            stockTopBan = results['pct_chg']
        connection.close()

    return stockTopBan


# 首板改成redis
# print( setStockTopBanToRedis() )
# print( getStockTopBanRedis('002031') )

# 获取概念
# print( getStockGlRedis('002031') )

# zrzt = getStockTopBan('002843')
# if zrzt == 0:
#     print( zrzt )
# print( getStockGl('002506') )

# 概念采集
# fetch_concept_caiji()

# print( fetch_concept('000566') )
# 获取ts_code
# SELECT left(sd.ts_code ,6) as ts_code
# FROM `stock_data` sd
# where sd.trade_date = (select max(sd2.trade_date) from `stock_data` sd2)

# 采集程序由于mysql连接过多中断，取没有采集完的ts_code
# select * from (
# SELECT left(sd.ts_code, 6) as ts_code, sd.trade_date  
# FROM `stock_data` sd  
# WHERE sd.trade_date = (SELECT MAX(sd2.trade_date) FROM `stock_data` sd2)  
# ) ts
# where ts.ts_code not in (select sc.ts_code from stock_concepts sc   ) 

# 概念查询
# select * from  `stock_concepts`  sc
# where sc.concepts like '%AI%'

##  涨停列表
# SELECT pct_chg, stock_data.*
# FROM stock_data  
# WHERE (  
#     (LEFT(ts_code, 2) = '60' OR LEFT(ts_code, 2) = '00' AND ROUND( pre_close*1.1, 2) = close)  
#     OR  
#     (LEFT(ts_code, 2) = '30' OR LEFT(ts_code, 2) = '68' AND ROUND( pre_close*1.1, 2) = close)  
# )  
# AND high = close and pct_chg > 9
# and trade_date = CURRENT_DATE()
# order by pct_chg desc
 
## 昨日涨停
# SELECT sd.ts_code,sd.pct_chg
# FROM stock_data sd  
# JOIN (  
#     SELECT trade_date  
#     FROM stock_data  
#     WHERE trade_date < CURRENT_DATE()  
#       AND ts_code  in ('600276.SH','300865.SZ'  )
#     ORDER BY trade_date DESC  
#     LIMIT 1  
# ) latest_trade ON sd.trade_date = latest_trade.trade_date  
# WHERE (  
#     (LEFT(sd.ts_code, 2) = '60' AND ROUND(sd.pre_close * 1.1, 2) = sd.close)  
#     OR  
#     (LEFT(sd.ts_code, 2) = '00' AND ROUND(sd.pre_close * 1.1, 2) = sd.close)  
#     OR  
#     (LEFT(sd.ts_code, 2) = '30' AND ROUND(sd.pre_close * 1.2, 2) = sd.close)
#     OR  
#     (LEFT(sd.ts_code, 2) = '68' AND ROUND(sd.pre_close * 1.2, 2) = sd.close)  
# )  
# AND sd.high = sd.close  
# AND sd.pct_chg > 9  
# AND sd.ts_code in ('600276.SH','300865.SZ'  )