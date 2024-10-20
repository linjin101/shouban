
# 本地或阿里云服务器标识
server = 'local' # aliyun

if server == 'local':
    # 本地调试配置
    ipconfig = '127.0.0.1:5000'
    ipconfigHtml = ipconfig

    # MySQL数据库连接参数  
    username = 'root'  
    password = 'root'  
    host = 'localhost'  
    database = 'dfstock'  

    # redis服务器配置
    redishost = 'localhost'
    redisport = 6379
    redispassword = 'shouban33'
    redisdbnum = 0

elif server == 'aliyun':
    # 服务器配置
    ipconfig = '127.0.0.1:5000'
    ipconfigHtml = 'sanhu918.com:5555'

    # 服务器MySQL数据库连接参数  
    username = 'root'  
    password = 'root101'  
    host = 'localhost'  
    database = 'dfstock'  

    # redis服务器配置
    redishost = 'localhost'
    redisport = 6379
    redispassword = 'shouban33'
    redisdbnum = 0







