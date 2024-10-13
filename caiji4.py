import requests  
import re   
import ast  
import json 
# 定义目标URL  
url = 'https://hqdata.compass.cn/test/sort2.py/sortList.znzDo?cmd=sz|A|desc|0|30|ratio|0.47870068306029916&crossdomain=3728801485178092&from=xici.compass.cn'  
  
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
# 发送GET请求  
response = requests.get(url, headers=headers)  
  
# 检查响应内容编码  
# 如果服务器返回了gzip压缩的内容，requests库会自动处理它  
content_encoding = response.headers.get('Content-Encoding')  
if content_encoding == 'gzip':  
    print("Response was gzip encoded and automatically decoded.")  
  
# 输出响应内容  
# 假设服务器返回的是文本内容（比如HTML或JSON），我们可以直接打印它  
# 如果返回的是二进制数据（比如图片），则需要以不同的方式处理  
 
# 检查请求是否成功  
if response.status_code == 200:  
    # 获取HTML内容  
    html_content = response.text  
    # print(html_content)

    # 使用正则表达式找到数组部分（双引号内的内容）  
    match = re.search(r'AJAJ_ON_READYSTATE_CHANGE\(\d+,(.*)\);0', html_content)  
    # 获取股票排序列表Html
    jshtml = match.group(1)
    # 截取字符串前后字符
    # jsHtmlJson = jshtml[10:-3].replace('\\\\\\','')
    jsHtmlJson = jshtml[10:-3].replace('\\"', '"').replace('\\\\', '\\').replace('\\', '')  

    # 使用正则表达式替换所有的'false'为'False'  
    fixed_str = re.sub(r'\bfalse\b', 'False', jsHtmlJson)  
            
    # 使用eval()解析修正后的字符串（注意：eval()在处理不受信任的输入时是不安全的）  
    data = eval(fixed_str)
    print(data[1])